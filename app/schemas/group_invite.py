from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from models.group_invite import InviteStatus

class GroupInviteCreate(BaseModel):
    invitee_id: int  # User ID to invite

class GroupInviteResponse(BaseModel):
    id: int
    group_playlist_id: int
    inviter_id: int
    invitee_id: int
    status: InviteStatus
    created_at: datetime
    expires_at: Optional[datetime]
    responded_at: Optional[datetime]
    
    # Additional details (populated from relationships)
    group_playlist_title: str
    inviter_username: str
    invitee_username: str
    
    class Config:
        from_attributes = True

class InviteActionResponse(BaseModel):
    message: str
    invite_id: int
    status: InviteStatus