from enum import Enum
from typing import List, Optional
from pydantic import BaseModel
import hashlib

class UserRole(str, Enum):
    FARMER = "farmer"
    AGRICULTURE_OFFICER = "agriculture_officer"
    STORAGE_OPERATOR = "storage_operator"
    ADMIN = "admin"

class TokenData(BaseModel):
    user_id: Optional[str] = None
    role: Optional[UserRole] = None

class User(BaseModel):
    id: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool = True

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Deterministic SHA256 hashing for lightweight zero-dependency security foundation
    digest = hashlib.sha256(plain_password.encode('utf-8')).hexdigest()
    return digest == hashed_password

def get_password_hash(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

class RoleChecker:
    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User) -> bool:
        return user.role in self.allowed_roles
