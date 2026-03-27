"""
app/api/v1/materials.py
-----------------------
Endpoints to manipulate individual material entries embedded in Module.materials
(a JSON column containing a list of MaterialItem dictionaries).

Routes:
  PATCH  /materials/{module_id}/{material_id}   – update one material field
  DELETE /materials/{module_id}/{material_id}   – delete one material from the list
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_role
from app.crud import get_module, update_module
from app.models import User, UserRole
from app.schemas.workshop import (
    MaterialItem,
    MaterialItemUpdate,
    ModuleResponse,
    ModuleUpdate,
)

router = APIRouter(prefix="/materials", tags=["materials"])

_WRITE_ROLES = (UserRole.ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.EDUCATOR)


# ────────────────────────────────────────────────────────────────────────────
# PATCH /materials/{module_id}/{material_id}
# ────────────────────────────────────────────────────────────────────────────


@router.patch(
    "/{module_id}/{material_id}",
    response_model=ModuleResponse,
    summary="Update a single material item inside a module (staff only)",
)
async def patch_material(
    module_id: str,
    material_id: str,
    payload: MaterialItemUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(*_WRITE_ROLES)),
) -> ModuleResponse:
    module = await get_module(db, module_id)
    if not module:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found.")

    materials: list[dict] = list(module.materials or [])
    updated_any = False
    new_materials: list[MaterialItem] = []

    for raw in materials:
        item = MaterialItem(**raw) if isinstance(raw, dict) else raw
        if item.id == material_id:
            # Apply partial update
            patch = payload.model_dump(exclude_unset=True)
            item = item.model_copy(update=patch)
            updated_any = True
        new_materials.append(item)

    if not updated_any:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Material '{material_id}' not found in module '{module_id}'.",
        )

    updated_module = await update_module(db, module, ModuleUpdate(materials=new_materials))
    return ModuleResponse.model_validate(updated_module)


# ────────────────────────────────────────────────────────────────────────────
# DELETE /materials/{module_id}/{material_id}
# ────────────────────────────────────────────────────────────────────────────


@router.delete(
    "/{module_id}/{material_id}",
    response_model=ModuleResponse,
    summary="Remove a single material item from a module (staff only)",
)
async def delete_material(
    module_id: str,
    material_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(*_WRITE_ROLES)),
) -> ModuleResponse:
    module = await get_module(db, module_id)
    if not module:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found.")

    materials: list[dict] = list(module.materials or [])
    original_count = len(materials)

    filtered: list[MaterialItem] = [
        MaterialItem(**m) if isinstance(m, dict) else m
        for m in materials
        if (m.get("id") if isinstance(m, dict) else m.id) != material_id
    ]

    if len(filtered) == original_count:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Material '{material_id}' not found in module '{module_id}'.",
        )

    updated_module = await update_module(db, module, ModuleUpdate(materials=filtered))
    return ModuleResponse.model_validate(updated_module)
