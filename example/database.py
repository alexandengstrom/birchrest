from typing import Optional, Any, List

# Pretend this is a real database


db = {
    "users": [
        {
            "id": 1,
            "name": "John Doe"
        },
        {
            "id": 2,
            "name": "Jane Doe"
        }
    ]
}

async def get_user(user_id: int) -> Optional[Any]:
    users = db["users"]
    
    for user in users:
        if user.get("id") == user_id:
            return user
        
    return None

async def get_users() -> List[Any]:
    return db.get("users", [])

async def create_user(user: Any) -> None:
    db["users"].append(user)
