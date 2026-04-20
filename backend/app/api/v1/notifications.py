from __future__ import annotations

from app.api.deps import (PaginationParams, get_current_user, get_db,
                          require_role)
from app.crud.crud_misc import (create_notification, delete_notification,
                                get_notification, get_notifications_by_user,
                                update_notification)
from app.models import NotificationStatus, User, UserRole
from app.schemas.base import Page
from app.schemas.misc import (NotificationBulkCreate, NotificationCreate,
                              NotificationResponse, NotificationUpdate)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/notifications", tags=["notifications"])

_STAFF = (UserRole.ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.EDUCATOR)


# ────────────────────────────────────────────────────────────────────────────
# POST /notifications/send  (Bulk Support via type-based tagging)
# ────────────────────────────────────────────────────────────────────────────


@router.post(
    "/send",
    response_model=list[NotificationResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Send a notification to multiple users concurrently (staff only)",
)
async def send_notification(
    payload: NotificationBulkCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(*_STAFF)),
) -> list[NotificationResponse]:
    results: list[NotificationResponse] = []
    
    # In a very large scale system, this would be chunked/backgrounded.
    # For standard deployment, linear loop is acceptable for typical cohort sizes.
    for uid in set(payload.user_ids):
        data = NotificationCreate(
            user_id=uid,
            message=payload.message,
            notification_type=payload.notification_type,
        )
        notif = await create_notification(db, data)
        results.append(NotificationResponse.model_validate(notif))

    return results


# ────────────────────────────────────────────────────────────────────────────
# GET /notifications/{user_id}
# ────────────────────────────────────────────────────────────────────────────


@router.get(
    "/{user_id}",
    response_model=Page[NotificationResponse],
    summary="List all notifications for a user (newest first)",
)
async def list_notifications(
    user_id: str,
    page: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Page[NotificationResponse]:
    # Users can only see their own notifications
    if current_user.role == UserRole.STUDENT and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    items, total = await get_notifications_by_user(
        db, user_id, offset=page.offset, limit=page.limit
    )
    return Page(
        items=[NotificationResponse.model_validate(n) for n in items],
        total=total,
        offset=page.offset,
        limit=page.limit,
    )


# ────────────────────────────────────────────────────────────────────────────
# PATCH /notifications/{notification_id}/read
# ────────────────────────────────────────────────────────────────────────────


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
    summary="Mark a notification as read",
)
async def mark_read(
    notification_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NotificationResponse:
    notif = await get_notification(db, notification_id)
    if not notif:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found.")

    # Only owner can map as read
    if notif.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    updated = await update_notification(db, notif, NotificationUpdate(status=NotificationStatus.READ))
    return NotificationResponse.model_validate(updated)


# ────────────────────────────────────────────────────────────────────────────
# DELETE /notifications/{notification_id}
# ────────────────────────────────────────────────────────────────────────────


@router.delete(
    "/{notification_id}",
    status_code=status.HTTP_201_CREATED,
    summary="Delete a notification",
)
async def delete_one(
    notification_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    notif = await get_notification(db, notification_id)
    if not notif:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found.")

    # Only owner can delete
    if notif.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    await delete_notification(db, notif)
