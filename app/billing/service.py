import logging
from datetime import datetime, timedelta
from typing import Optional

import stripe
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.models.database import User, Payment, UserRole, SubscriptionType

logger = logging.getLogger(__name__)

stripe.api_key = settings.stripe_secret_key


class BillingService:
    def __init__(self):
        self.stripe = stripe
    
    async def create_subscription(
        self,
        user: User,
        subscription_type: SubscriptionType,
        db: AsyncSession
    ) -> dict:
        try:
            if subscription_type == SubscriptionType.MONTHLY:
                price_id = "price_monthly"  # Замените на реальный Stripe Price ID
                amount = 999  # $9.99 в центах
            else:
                price_id = "price_yearly"  # Замените на реальный Stripe Price ID
                amount = 9999  # $99.99 в центах
            
            payment_intent = self.stripe.PaymentIntent.create(
                amount=amount,
                currency="usd",
                metadata={
                    "user_id": user.id,
                    "subscription_type": subscription_type.value
                }
            )
            
            payment = Payment(
                user_id=user.id,
                stripe_payment_intent_id=payment_intent.id,
                amount=amount / 100,
                currency="USD",
                subscription_type=subscription_type.value,
                status="pending"
            )
            db.add(payment)
            await db.commit()
            
            return {
                "client_secret": payment_intent.client_secret,
                "payment_intent_id": payment_intent.id
            }
            
        except Exception as e:
            logger.error(f"Error creating subscription: {e}")
            raise
    
    async def confirm_payment(self, payment_intent_id: str, db: AsyncSession) -> bool:
        try:
            payment_intent = self.stripe.PaymentIntent.retrieve(payment_intent_id)
            
            if payment_intent.status == "succeeded":
                result = await db.execute(
                    select(Payment).where(Payment.stripe_payment_intent_id == payment_intent_id)
                )
                payment = result.scalar_one_or_none()
                
                if payment:
                    payment.status = "completed"
                    user = payment.user
                    user.role = UserRole.PREMIUM
                    user.subscription_type = payment.subscription_type
                    
                    if payment.subscription_type == SubscriptionType.MONTHLY:
                        user.subscription_expires = datetime.utcnow() + timedelta(days=30)
                    else:
                        user.subscription_expires = datetime.utcnow() + timedelta(days=365)
                    
                    await db.commit()
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error confirming payment: {e}")
            return False
    
    async def cancel_subscription(self, user: User, db: AsyncSession) -> bool:
        try:
            user.role = UserRole.FREE
            user.subscription_type = None
            user.subscription_expires = None
            await db.commit()
            return True
        except Exception as e:
            logger.error(f"Error canceling subscription: {e}")
            return False
    
    async def check_subscription_status(self, user: User) -> dict:
        if user.role != UserRole.PREMIUM:
            return {
                "is_active": False,
                "role": user.role,
                "expires_at": None
            }
        
        if user.subscription_expires and user.subscription_expires < datetime.utcnow():
            return {
                "is_active": False,
                "role": UserRole.FREE,
                "expires_at": user.subscription_expires
            }
        
        return {
            "is_active": True,
            "role": user.role,
            "expires_at": user.subscription_expires
        }
    
    async def get_payment_history(self, user: User, db: AsyncSession) -> list:
        result = await db.execute(select(Payment).where(Payment.user_id == user.id))
        payments = result.scalars().all()
        return [
            {
                "id": payment.id,
                "amount": payment.amount,
                "currency": payment.currency,
                "subscription_type": payment.subscription_type,
                "status": payment.status,
                "created_at": payment.created_at
            }
            for payment in payments
        ]
