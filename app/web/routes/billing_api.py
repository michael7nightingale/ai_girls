from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from app.core.database import get_async_session
from app.core.auth import get_current_user
from app.billing.service import BillingService
from app.models.database import User

router = APIRouter(prefix="/api/billing", tags=["billing"])

billing_service = BillingService()


@router.post("/create-payment")
async def create_payment(
    plan: str,
    payment_method: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> Dict[str, Any]:
    """Создание платежа"""
    try:
        result = await billing_service.create_payment(
            user=current_user,
            plan=plan,
            payment_method=payment_method,
            db=db
        )
        
        return {
            "success": True,
            "data": result
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при создании платежа"
        )


@router.post("/confirm-payment")
async def confirm_payment(
    payment_id: str,
    payment_method: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> Dict[str, Any]:
    """Подтверждение платежа"""
    try:
        success = await billing_service.confirm_payment(
            payment_id=payment_id,
            payment_method=payment_method,
            db=db
        )
        
        if success:
            return {
                "success": True,
                "message": "Платеж успешно подтвержден"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Не удалось подтвердить платеж"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при подтверждении платежа"
        )


@router.get("/subscription-status")
async def get_subscription_status(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Получение статуса подписки"""
    try:
        status_info = await billing_service.check_subscription_status(current_user)
        
        return {
            "success": True,
            "data": status_info
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении статуса подписки"
        )


@router.post("/cancel-subscription")
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> Dict[str, Any]:
    """Отмена подписки"""
    try:
        success = await billing_service.cancel_subscription(
            user=current_user,
            db=db
        )
        
        if success:
            return {
                "success": True,
                "message": "Подписка успешно отменена"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Не удалось отменить подписку"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при отмене подписки"
        )


@router.get("/payment-history")
async def get_payment_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> Dict[str, Any]:
    """Получение истории платежей"""
    try:
        payments = await billing_service.get_payment_history(
            user=current_user,
            db=db
        )
        
        return {
            "success": True,
            "data": payments
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении истории платежей"
        )


@router.get("/plans")
async def get_subscription_plans() -> Dict[str, Any]:
    """Получение доступных планов подписки"""
    try:
        plans = await billing_service.get_subscription_plans()
        
        return {
            "success": True,
            "data": plans
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении планов подписки"
        )


@router.post("/stripe-webhook")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_async_session)
) -> Dict[str, Any]:
    """Webhook для обработки событий Stripe"""
    try:
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature")
        
        # Проверяем подпись webhook
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.stripe_webhook_secret
            )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid payload"
            )
        except stripe.error.SignatureVerificationError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid signature"
            )
        
        # Обрабатываем события
        if event["type"] == "payment_intent.succeeded":
            payment_intent = event["data"]["object"]
            
            # Находим платеж в базе
            result = await db.execute(
                select(Payment).where(
                    Payment.stripe_payment_intent_id == payment_intent["id"]
                )
            )
            payment = result.scalar_one_or_none()
            
            if payment:
                await billing_service._activate_subscription(payment, db)
        
        return {"success": True}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обработке webhook"
        )


@router.post("/paypal-webhook")
async def paypal_webhook(
    request: Request,
    db: AsyncSession = Depends(get_async_session)
) -> Dict[str, Any]:
    """Webhook для обработки событий PayPal"""
    try:
        payload = await request.json()
        
        # Проверяем событие
        if payload.get("event_type") == "PAYMENT.CAPTURE.COMPLETED":
            payment_data = payload["resource"]
            
            # Находим платеж в базе
            result = await db.execute(
                select(Payment).where(
                    Payment.paypal_order_id == payment_data["custom_id"]
                )
            )
            payment = result.scalar_one_or_none()
            
            if payment:
                await billing_service._activate_subscription(payment, db)
        
        return {"success": True}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обработке webhook"
        )


@router.get("/usage-stats")
async def get_usage_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> Dict[str, Any]:
    """Получение статистики использования"""
    try:
        # Получаем статистику сообщений
        result = await db.execute(
            select(func.count(Message.id)).where(
                Message.chat_id.in_(
                    select(Chat.id).where(Chat.user_id == current_user.id)
                )
            )
        )
        total_messages = result.scalar() or 0
        
        # Получаем количество чатов
        result = await db.execute(
            select(func.count(Chat.id)).where(Chat.user_id == current_user.id)
        )
        total_chats = result.scalar() or 0
        
        # Получаем статус подписки
        subscription_status = await billing_service.check_subscription_status(current_user)
        
        # Лимиты в зависимости от подписки
        if subscription_status["is_active"]:
            message_limit = "∞"
            chat_limit = "∞"
        else:
            message_limit = settings.free_messages_per_day
            chat_limit = settings.free_chats_limit
        
        return {
            "success": True,
            "data": {
                "total_messages": total_messages,
                "total_chats": total_chats,
                "message_limit": message_limit,
                "chat_limit": chat_limit,
                "subscription_status": subscription_status
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении статистики"
        )
