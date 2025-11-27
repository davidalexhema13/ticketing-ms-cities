from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
import jwt

router = APIRouter(prefix="/auth", tags=["Authentication"])

SECRET_KEY = "SUPER_SECRET_KEY"
ALGORITHM = "HS256"

bearer_scheme = HTTPBearer()

# Dummy admin user (for the activity)
fake_user = {
    "username": "admin",
    "password": "admin123",
    "role": "admin"
}

def create_token(data: dict):
    to_encode = data.copy()
    to_encode["exp"] = datetime.utcnow() + timedelta(hours=2)
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/token")
def login(username: str, password: str):
    if username != fake_user["username"] or password != fake_user["password"]:
        raise HTTPException(status_code=400, detail="Credenciales inválidas.")
    token = create_token({"sub": username, "role": fake_user["role"]})
    return {"access_token": token, "token_type": "bearer"}

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido o expirado.")
