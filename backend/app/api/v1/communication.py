from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_role
from app.crud.crud_misc import create_notification
from app.models import NotificationType, User, UserRole
from app.schemas.misc import NotificationCreate, ParentMessageRequest, ParentMessageResponse

router = APIRouter(prefix="/communication", tags=["communication"])


@router.post(
    "/parent-email",
    response_model=ParentMessageResponse,
    summary="Dispatch parent communication message and log notifications",
)
async def dispatch_parent_email(
    payload: ParentMessageRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.EDUCATOR)),
) -> ParentMessageResponse:
    accepted = 0
    failed = 0

    for student_id in set(payload.student_ids):
        try:
            await create_notification(
                db,
                NotificationCreate(
                    user_id=student_id,
                    message=f"[Parent Message] {payload.subject}: {payload.body}",
                    notification_type=NotificationType.GENERAL,
                ),
            )
            accepted += 1
        except Exception:
            failed += 1

    return ParentMessageResponse(
        accepted=accepted,
        failed=failed,
        message="Parent communication request processed.",
    )
