from dataclasses import dataclass, field
from typing import List

@dataclass
class UserId:
    id: int = field(metadata={"min_value": 1})
    
@dataclass
class UserModel:
    name: str = field(metadata={"min_length": 5, "max_length": 10})
    age: int = field(metadata={"min_value": 18})
    
@dataclass
class UserResponseModel:
    name: str = field(metadata={"min_length": 5, "max_length": 10})
    id: int = field(metadata={"min_value": 1})
    
@dataclass
class UsersModel:
    data: List[UserResponseModel]