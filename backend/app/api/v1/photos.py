from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.schemas.common import APIResponse
from app.services.storage_service import StorageService
from app.repositories.toilet_repository import ToiletRepository
from app.core.exceptions import ToiletNotFoundException, ForbiddenException, ValidationException
from app.db.models.toilet_photo import ToiletPhoto

router = APIRouter()

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


@router.post("/{toilet_id}/photos", response_model=APIResponse)
async def upload_photo(
    toilet_id: UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise ValidationException("지원하지 않는 파일 형식입니다. (jpeg, png, webp만 허용)")

    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE:
        raise ValidationException("파일 크기는 5MB 이하여야 합니다.")

    repo = ToiletRepository(db)
    toilet = await repo.get_by_id(str(toilet_id))
    if not toilet:
        raise ToiletNotFoundException()

    # 최대 5장 확인
    if len(toilet.photos) >= 5:
        raise ValidationException("화장실당 최대 5장의 사진만 등록할 수 있습니다.")

    storage_service = StorageService()
    upload_result = await storage_service.upload_toilet_photo(
        str(toilet_id), file_bytes, file.content_type
    )

    photo = ToiletPhoto(
        toilet_id=toilet_id,
        image_url=upload_result["image_url"],
        storage_path=upload_result["storage_path"],
        display_order=len(toilet.photos),
        uploaded_by=current_user.id,
    )
    db.add(photo)
    await db.commit()
    await db.refresh(photo)

    return APIResponse.ok({
        "id": str(photo.id),
        "image_url": photo.image_url,
        "display_order": photo.display_order,
    })


@router.delete("/{toilet_id}/photos/{photo_id}", response_model=APIResponse)
async def delete_photo(
    toilet_id: UUID,
    photo_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    from sqlalchemy import select
    result = await db.execute(
        select(ToiletPhoto).where(
            ToiletPhoto.id == photo_id,
            ToiletPhoto.toilet_id == toilet_id,
        )
    )
    photo = result.scalar_one_or_none()
    if not photo:
        raise ValidationException("사진을 찾을 수 없습니다.")
    if str(photo.uploaded_by) != str(current_user.id):
        raise ForbiddenException("본인이 업로드한 사진만 삭제할 수 있습니다.")

    storage_service = StorageService()
    await storage_service.delete_photo(photo.storage_path)

    await db.delete(photo)
    await db.commit()
    return APIResponse.ok({"message": "사진이 삭제되었습니다."})
