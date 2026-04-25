from pydantic import BaseModel
from datetime import datetime
from models.group_member import MemberRole

class GroupMemberResponse(BaseModel):
    id: int
    group_playlist_id: int
    user_id: int
    role: MemberRole
    joined_at: datetime
    
    # User details (will be populated from relationship)
    username: str
    full_name: str | None
    profile_image: str | None
    
    class Config:
        from_attributes = True

class UpdateMemberRole(BaseModel):
    role: MemberRole