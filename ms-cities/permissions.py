from fastapi import HTTPException, Depends
from auth import get_current_user

def admin_required(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Acceso denegado. Se requiere el rol de Administrador."
        )
    return current_user
