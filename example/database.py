from typing import Optional, Any, List

# Pretend this is a real database


db = {
    "users": [
        {
            "id": 1,
            "name": "John Doe",
        },
        {
            "id": 2,
            "name": "Jane Doe"
        }
    ],
    "messages": [
        {
            "id": 1,
            "user_id": 1,
            "message": "Hello world!"
        },
        {
            "id": 2,
            "user_id": 1,
            "message": "How are you?"
        },
        {
            "id": 3,
            "user_id": 2,
            "message": "I am gooooood!"
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
    
async def get_messages(user_id: int) -> List[Any]:
    return list(filter(lambda entry: entry["user_id"] == user_id ,db["messages"]))
