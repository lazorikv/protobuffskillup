from typing import Dict, Optional, Any
import bcrypt
from .database import DatabaseService


class UserService(DatabaseService):
    
    def get_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        return self.fetch_one(
            "SELECT * FROM users WHERE username = ?", 
            (username,)
        )
    
    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        return self.fetch_one(
            "SELECT * FROM users WHERE email = ?", 
            (email,)
        )
    
    def get_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        return self.fetch_one(
            "SELECT * FROM users WHERE id = ?", 
            (user_id,)
        )
    
    def create(self, username: str, email: str, password: str) -> Dict[str, Any]:
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode(), salt).decode()
        
        user_id = self.execute(
            "INSERT INTO users (username, email, hashed_password, disabled) VALUES (?, ?, ?, ?)",
            (username, email, hashed_password, False)
        )
        
        return {
            "id": user_id,
            "username": username,
            "email": email,
            "hashed_password": hashed_password,
            "disabled": False
        }
    
    def update(self, user_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        set_parts = []
        values = []
        
        for key, value in data.items():
            if key in ["username", "email", "disabled"]:
                set_parts.append(f"{key} = ?")
                values.append(value)
            elif key == "password":
                set_parts.append("hashed_password = ?")
                salt = bcrypt.gensalt()
                hashed_password = bcrypt.hashpw(value.encode(), salt).decode()
                values.append(hashed_password)
        
        if not set_parts:
            return None
        
        values.append(user_id)
        
        affected_rows = self.execute_update(
            f"UPDATE users SET {', '.join(set_parts)} WHERE id = ?",
            tuple(values)
        )
        
        if affected_rows == 0:
            return None
        return self.get_by_id(user_id)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


user_service = UserService()
