# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.ext.asyncio import AsyncSession
# from database import get_db
# from utils.auth import get_current_user
# from models.user import User
# from models.group_member import MemberRole
# from schemas.group_playlist import (
#     GroupPlaylistCreate, GroupPlaylistUpdate, 
#     GroupPlaylistResponse, GroupPlaylistDetailResponse
# )
# from schemas.group_member import GroupMemberResponse, UpdateMemberRole
# from schemas.group_video import GroupVideoCreate, GroupVideoUpdate, GroupVideoResponse
# from schemas.group_invite import GroupInviteCreate, GroupInviteResponse, InviteActionResponse
# from crud.group_playlist import GroupPlaylistCRUD
# from crud.group_member import GroupMemberCRUD
# from crud.group_video import GroupVideoCRUD
# from crud.group_invite import GroupInviteCRUD
# from utils.group_permissions import GroupPermissions
# from typing import List

# router = APIRouter(prefix="/api/group-playlists", tags=["Group Playlists"])

# # ============ PLAYLIST CRUD ============

# @router.post("/", response_model=GroupPlaylistResponse, status_code=status.HTTP_201_CREATED)
# async def create_group_playlist(
#     playlist_data: GroupPlaylistCreate,
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     """Create a new group playlist (user becomes owner)"""
#     playlist = await GroupPlaylistCRUD.create(db, playlist_data, current_user.id)
#     return playlist

# @router.get("/", response_model=List[GroupPlaylistResponse])
# async def get_my_group_playlists(
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     """Get all group playlists where current user is a member"""
#     playlists = await GroupPlaylistCRUD.get_user_playlists(db, current_user.id)
#     return playlists

# @router.get("/owned", response_model=List[GroupPlaylistResponse])
# async def get_owned_playlists(
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     """Get all group playlists owned by current user"""
#     playlists = await GroupPlaylistCRUD.get_owned_playlists(db, current_user.id)
#     return playlists

# @router.get("/{playlist_id}", response_model=GroupPlaylistDetailResponse)
# async def get_group_playlist(
#     playlist_id: int,
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     """Get group playlist details"""
#     # Check if user is a member
#     is_member = await GroupMemberCRUD.is_member(db, playlist_id, current_user.id)
#     if not is_member:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="You are not a member of this group playlist"
#         )
    
#     playlist = await GroupPlaylistCRUD.get_by_id(db, playlist_id, load_members=True, load_videos=True)
#     if not playlist:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group playlist not found")
    
#     return playlist

# @router.patch("/{playlist_id}", response_model=GroupPlaylistResponse)
# async def update_group_playlist(
#     playlist_id: int,
#     playlist_data: GroupPlaylistUpdate,
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     """Update group playlist (owner/admin only)"""
#     # Check permission
#     member_role = await GroupMemberCRUD.get_member_role(db, playlist_id, current_user.id)
#     if not member_role or not GroupPermissions.can_update_playlist(member_role):
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Only owner and admin can update playlist details"
#         )
    
#     playlist = await GroupPlaylistCRUD.update(db, playlist_id, playlist_data)
#     if not playlist:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group playlist not found")
    
#     return playlist

# @router.delete("/{playlist_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_group_playlist(
#     playlist_id: int,
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     """Delete group playlist (owner only)"""
#     # Check permission
#     member_role = await GroupMemberCRUD.get_member_role(db, playlist_id, current_user.id)
#     if not member_role or not GroupPermissions.can_delete_playlist(member_role):
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Only owner can delete the playlist"
#         )
    
#     success = await GroupPlaylistCRUD.delete(db, playlist_id)
#     if not success:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group playlist not found")

# # ============ INVITE SYSTEM ============

# @router.post("/{playlist_id}/invite", response_model=GroupInviteResponse, status_code=status.HTTP_201_CREATED)
# async def invite_user(
#     playlist_id: int,
#     invite_data: GroupInviteCreate,
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     """Invite a user to group playlist (owner/admin only)"""
#     # Check if playlist exists
#     playlist = await GroupPlaylistCRUD.get_by_id(db, playlist_id)
#     if not playlist:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group playlist not found")
    
#     # Check permission
#     member_role = await GroupMemberCRUD.get_member_role(db, playlist_id, current_user.id)
#     if not member_role or not GroupPermissions.can_invite_members(member_role):
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Only owner and admin can invite members"
#         )
    
#     # Check if invitee is already a member
#     is_member = await GroupMemberCRUD.is_member(db, playlist_id, invite_data.invitee_id)
#     if is_member:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="User is already a member"
#         )
    
#     # Create invite
#     invite = await GroupInviteCRUD.create(
#         db, playlist_id, current_user.id, invite_data.invitee_id
#     )
#     if not invite:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Failed to create invite"
#         )
    
#     # Load relationships for response
#     invite = await GroupInviteCRUD.get_by_id(db, invite.id)
    
#     # Format response
#     return GroupInviteResponse(
#         id=invite.id,
#         group_playlist_id=invite.group_playlist_id,
#         inviter_id=invite.inviter_id,
#         invitee_id=invite.invitee_id,
#         status=invite.status,
#         created_at=invite.created_at,
#         expires_at=invite.expires_at,
#         responded_at=invite.responded_at,
#         group_playlist_title=invite.group_playlist.title,
#         inviter_username=invite.inviter.username,
#         invitee_username=invite.invitee.username
#     )

# @router.get("/invites/pending", response_model=List[GroupInviteResponse])
# async def get_pending_invites(
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     """Get all pending invites for current user"""
#     invites = await GroupInviteCRUD.get_user_pending_invites(db, current_user.id)
    
#     return [
#         GroupInviteResponse(
#             id=invite.id,
#             group_playlist_id=invite.group_playlist_id,
#             inviter_id=invite.inviter_id,
#             invitee_id=invite.invitee_id,
#             status=invite.status,
#             created_at=invite.created_at,
#             expires_at=invite.expires_at,
#             responded_at=invite.responded_at,
#             group_playlist_title=invite.group_playlist.title,
#             inviter_username=invite.inviter.username,
#             invitee_username=invite.invitee.username
#         )
#         for invite in invites
#     ]

# @router.post("/invites/{invite_id}/accept", response_model=InviteActionResponse)
# async def accept_invite(
#     invite_id: int,
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     """Accept an invite"""
#     invite = await GroupInviteCRUD.get_by_id(db, invite_id)
#     if not invite:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invite not found")
    
#     if invite.invitee_id != current_user.id:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="This invite is not for you"
#         )
    
#     # Accept invite
#     accepted_invite = await GroupInviteCRUD.accept_invite(db, invite_id)
#     if not accepted_invite:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invite already responded to or expired"
#         )
    
#     # Add user as member
#     await GroupMemberCRUD.add_member(
#         db, invite.group_playlist_id, current_user.id, MemberRole.MEMBER
#     )
    
#     return InviteActionResponse(
#         message="Invite accepted successfully",
#         invite_id=invite_id,
#         status=accepted_invite.status
#     )

# @router.post("/invites/{invite_id}/reject", response_model=InviteActionResponse)
# async def reject_invite(
#     invite_id: int,
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     """Reject an invite"""
#     invite = await GroupInviteCRUD.get_by_id(db, invite_id)
#     if not invite:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invite not found")
    
#     if invite.invitee_id != current_user.id:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="This invite is not for you"
#         )
    
#     rejected_invite = await GroupInviteCRUD.reject_invite(db, invite_id)
#     if not rejected_invite:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invite already responded to"
#         )
    
#     return InviteActionResponse(
#         message="Invite rejected",
#         invite_id=invite_id,
#         status=rejected_invite.status
#     )

# # ============ MEMBERS MANAGEMENT ============

# @router.get("/{playlist_id}/members", response_model=List[GroupMemberResponse])
# async def get_members(
#     playlist_id: int,
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     """Get all members of a group playlist"""
#     # Check if user is a member
#     is_member = await GroupMemberCRUD.is_member(db, playlist_id, current_user.id)
#     if not is_member:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="You are not a member of this group playlist"
#         )
    
#     members = await GroupMemberCRUD.get_all_members(db, playlist_id)
    
#     return [
#         GroupMemberResponse(
#             id=member.id,
#             group_playlist_id=member.group_playlist_id,
#             user_id=member.user_id,
#             role=member.role,
#             joined_at=member.joined_at,
#             username=member.user.username,
#             full_name=member.user.full_name,
#             profile_image=member.user.profile_image
#         )
#         for member in members
#     ]

# @router.patch("/{playlist_id}/members/{user_id}/role", response_model=GroupMemberResponse)
# async def update_member_role(
#     playlist_id: int,
#     user_id: int,
#     role_data: UpdateMemberRole,
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     """Update a member's role (owner only)"""
#     # Get requester's role
#     requester_role = await GroupMemberCRUD.get_member_role(db, playlist_id, current_user.id)
#     if not requester_role:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="You are not a member of this group playlist"
#         )
    
#     # Get target member
#     target_member = await GroupMemberCRUD.get_member(db, playlist_id, user_id)
#     if not target_member:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    
#     # Check permission
#     if not GroupPermissions.can_update_member_role(
#         requester_role, target_member.role, role_data.role
#     ):
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="You don't have permission to change this member's role"
#         )
    
#     # Update role
#     updated_member = await GroupMemberCRUD.update_role(db, playlist_id, user_id, role_data.role)
    
#     return GroupMemberResponse(
#         id=updated_member.id,
#         group_playlist_id=updated_member.group_playlist_id,
#         user_id=updated_member.user_id,
#         role=updated_member.role,
#         joined_at=updated_member.joined_at,
#         username=updated_member.user.username,
#         full_name=updated_member.user.full_name,
#         profile_image=updated_member.user.profile_image
#     )

# @router.delete("/{playlist_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def remove_member(
#     playlist_id: int,
#     user_id: int,
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     """Remove a member from group playlist"""
#     # Get requester's role
#     requester_role = await GroupMemberCRUD.get_member_role(db, playlist_id, current_user.id)
#     if not requester_role:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="You are not a member of this group playlist"
#         )
    
#     # Get target member
#     target_member = await GroupMemberCRUD.get_member(db, playlist_id, user_id)
#     if not target_member:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    
#     # Check permission
#     is_self = user_id == current_user.id
#     if not GroupPermissions.can_remove_member(requester_role, target_member.role, is_self):
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="You don't have permission to remove this member"
#         )
    
#     # Cannot remove owner
#     if target_member.role == MemberRole.OWNER:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Cannot remove the owner. Transfer ownership first or delete the playlist."
#         )
    
#     success = await GroupMemberCRUD.remove_member(db, playlist_id, user_id)
#     if not success:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")

# # ============ VIDEOS MANAGEMENT ============

# @router.post("/{playlist_id}/videos", response_model=GroupVideoResponse, status_code=status.HTTP_201_CREATED)
# async def add_video(
#     playlist_id: int,
#     video_data: GroupVideoCreate,
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     """Add a video to group playlist (all members can add)"""
#     # Check if user is a member and get role
#     member_role = await GroupMemberCRUD.get_member_role(db, playlist_id, current_user.id)
#     if not member_role:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="You are not a member of this group playlist"
#         )
    
#     # Check permission
#     if not GroupPermissions.can_add_video(member_role):
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="You don't have permission to add videos"
#         )
    
#     video = await GroupVideoCRUD.create(db, playlist_id, video_data, current_user.id)
    
#     # Format response
#     return GroupVideoResponse(
#         id=video.id,
#         group_playlist_id=video.group_playlist_id,
#         youtube_id=video.youtube_id,
#         title=video.title,
#         channel_name=video.channel_name,
#         thumbnail=video.thumbnail,
#         views=video.views,
#         youtube_description=video.youtube_description,
#         user_description=video.user_description,
#         added_by_id=video.added_by_id,
#         position=video.position,
#         created_at=video.created_at,
#         updated_at=video.updated_at,
#         added_by_username=current_user.username
#     )

# @router.get("/{playlist_id}/videos", response_model=List[GroupVideoResponse])
# async def get_videos(
#     playlist_id: int,
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     """Get all videos in a group playlist"""
#     # Check if user is a member
#     is_member = await GroupMemberCRUD.is_member(db, playlist_id, current_user.id)
#     if not is_member:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="You are not a member of this group playlist"
#         )
    
#     videos = await GroupVideoCRUD.get_playlist_videos(db, playlist_id)
    
#     return [
#         GroupVideoResponse(
#             id=video.id,
#             group_playlist_id=video.group_playlist_id,
#             youtube_id=video.youtube_id,
#             title=video.title,
#             channel_name=video.channel_name,
#             thumbnail=video.thumbnail,
#             views=video.views,
#             youtube_description=video.youtube_description,
#             user_description=video.user_description,
#             added_by_id=video.added_by_id,
#             position=video.position,
#             created_at=video.created_at,
#             updated_at=video.updated_at,
#             added_by_username=video.added_by.username if video.added_by else None
#         )
#         for video in videos
#     ]

# @router.delete("/{playlist_id}/videos/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_video(
#     playlist_id: int,
#     video_id: int,
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     """Delete a video from group playlist (permission-based)"""
#     # Get member role
#     member_role = await GroupMemberCRUD.get_member_role(db, playlist_id, current_user.id)
#     if not member_role:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="You are not a member of this group playlist"
#         )
    
#     # Get video
#     video = await GroupVideoCRUD.get_by_id(db, video_id, load_added_by=True)
#     if not video or video.group_playlist_id != playlist_id:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    
#     # Check permission
#     if not GroupPermissions.can_delete_video(member_role, video, current_user.id):
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="You don't have permission to delete this video"
#         )
    
#     success = await GroupVideoCRUD.delete(db, video_id)
#     if not success:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db, async_session_maker
from utils.auth import get_current_user
from utils.youtube import get_video_metadata
from utils.background_tasks import import_playlist_task
from utils.cache import generate_cache_key, get_cached_data
from models.user import User
from models.group_member import MemberRole
from schemas.group_playlist import (
    GroupPlaylistCreate, GroupPlaylistUpdate, 
    GroupPlaylistResponse, GroupPlaylistDetailResponse,
    PlaylistImportRequest, PlaylistImportResponse, ImportStatusResponse
)
from schemas.group_member import GroupMemberResponse, UpdateMemberRole
from schemas.group_video import GroupVideoCreate, GroupVideoUpdate, GroupVideoResponse
from schemas.group_invite import GroupInviteCreate, GroupInviteResponse, InviteActionResponse
from crud.group_playlist import GroupPlaylistCRUD
from crud.group_member import GroupMemberCRUD
from crud.group_video import GroupVideoCRUD
from crud.group_invite import GroupInviteCRUD
from utils.group_permissions import GroupPermissions
from typing import List
import uuid
from utils.rate_limiter import rate_limit

router = APIRouter(prefix="/api/group-playlists", tags=["Group Playlists"])

# ============ PLAYLIST CRUD ============

@router.post("/", response_model=GroupPlaylistResponse, status_code=status.HTTP_201_CREATED)
async def create_group_playlist(
    playlist_data: GroupPlaylistCreate,
    current_user: User = Depends(rate_limit("create_group_playlist", 30, 60)),
    db: AsyncSession = Depends(get_db)
):
    """Create a new group playlist (user becomes owner)"""
    playlist = await GroupPlaylistCRUD.create(db, playlist_data, current_user.id)
    return playlist

@router.get("/", response_model=List[GroupPlaylistResponse])
async def get_my_group_playlists(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all group playlists where current user is a member"""
    playlists = await GroupPlaylistCRUD.get_user_playlists(db, current_user.id)
    return playlists

@router.get("/owned", response_model=List[GroupPlaylistResponse])
async def get_owned_playlists(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all group playlists owned by current user"""
    playlists = await GroupPlaylistCRUD.get_owned_playlists(db, current_user.id)
    return playlists

@router.get("/{playlist_id}", response_model=GroupPlaylistDetailResponse)
async def get_group_playlist(
    playlist_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get group playlist details"""
    # Check if user is a member
    is_member = await GroupMemberCRUD.is_member(db, playlist_id, current_user.id)
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this group playlist"
        )
    
    playlist = await GroupPlaylistCRUD.get_by_id(db, playlist_id, load_members=True, load_videos=True)
    if not playlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group playlist not found")
    
    return playlist

@router.patch("/{playlist_id}", response_model=GroupPlaylistResponse)
async def update_group_playlist(
    playlist_id: int,
    playlist_data: GroupPlaylistUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update group playlist (owner/admin only)"""
    # Check permission
    member_role = await GroupMemberCRUD.get_member_role(db, playlist_id, current_user.id)
    if not member_role or not GroupPermissions.can_update_playlist(member_role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owner and admin can update playlist details"
        )
    
    playlist = await GroupPlaylistCRUD.update(db, playlist_id, playlist_data)
    if not playlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group playlist not found")
    
    return playlist

@router.delete("/{playlist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group_playlist(
    playlist_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete group playlist (owner only)"""
    # Check permission
    member_role = await GroupMemberCRUD.get_member_role(db, playlist_id, current_user.id)
    if not member_role or not GroupPermissions.can_delete_playlist(member_role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owner can delete the playlist"
        )
    
    success = await GroupPlaylistCRUD.delete(db, playlist_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group playlist not found")

# ============ INVITE SYSTEM ============

@router.post("/{playlist_id}/invite", response_model=GroupInviteResponse, status_code=status.HTTP_201_CREATED)
async def invite_user(
    playlist_id: int,
    invite_data: GroupInviteCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Invite a user to group playlist (owner/admin only)"""
    # Check if playlist exists
    playlist = await GroupPlaylistCRUD.get_by_id(db, playlist_id)
    if not playlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group playlist not found")
    
    # Check permission
    member_role = await GroupMemberCRUD.get_member_role(db, playlist_id, current_user.id)
    if not member_role or not GroupPermissions.can_invite_members(member_role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owner and admin can invite members"
        )
    
    # Check if invitee is already a member
    is_member = await GroupMemberCRUD.is_member(db, playlist_id, invite_data.invitee_id)
    if is_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member"
        )
    
    # Create invite
    invite = await GroupInviteCRUD.create(
        db, playlist_id, current_user.id, invite_data.invitee_id
    )
    if not invite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create invite"
        )
    
    # Load relationships for response
    invite = await GroupInviteCRUD.get_by_id(db, invite.id)
    
    # Format response
    return GroupInviteResponse(
        id=invite.id,
        group_playlist_id=invite.group_playlist_id,
        inviter_id=invite.inviter_id,
        invitee_id=invite.invitee_id,
        status=invite.status,
        created_at=invite.created_at,
        expires_at=invite.expires_at,
        responded_at=invite.responded_at,
        group_playlist_title=invite.group_playlist.title,
        inviter_username=invite.inviter.username,
        invitee_username=invite.invitee.username
    )

@router.get("/invites/pending", response_model=List[GroupInviteResponse])
async def get_pending_invites(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all pending invites for current user"""
    invites = await GroupInviteCRUD.get_user_pending_invites(db, current_user.id)
    
    return [
        GroupInviteResponse(
            id=invite.id,
            group_playlist_id=invite.group_playlist_id,
            inviter_id=invite.inviter_id,
            invitee_id=invite.invitee_id,
            status=invite.status,
            created_at=invite.created_at,
            expires_at=invite.expires_at,
            responded_at=invite.responded_at,
            group_playlist_title=invite.group_playlist.title,
            inviter_username=invite.inviter.username,
            invitee_username=invite.invitee.username
        )
        for invite in invites
    ]

@router.post("/invites/{invite_id}/accept", response_model=InviteActionResponse)
async def accept_invite(
    invite_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Accept an invite"""
    invite = await GroupInviteCRUD.get_by_id(db, invite_id)
    if not invite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invite not found")
    
    if invite.invitee_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This invite is not for you"
        )
    
    # Accept invite
    accepted_invite = await GroupInviteCRUD.accept_invite(db, invite_id)
    if not accepted_invite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invite already responded to or expired"
        )
    
    # Add user as member
    await GroupMemberCRUD.add_member(
        db, invite.group_playlist_id, current_user.id, MemberRole.MEMBER
    )
    
    return InviteActionResponse(
        message="Invite accepted successfully",
        invite_id=invite_id,
        status=accepted_invite.status
    )

@router.post("/invites/{invite_id}/reject", response_model=InviteActionResponse)
async def reject_invite(
    invite_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Reject an invite"""
    invite = await GroupInviteCRUD.get_by_id(db, invite_id)
    if not invite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invite not found")
    
    if invite.invitee_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This invite is not for you"
        )
    
    rejected_invite = await GroupInviteCRUD.reject_invite(db, invite_id)
    if not rejected_invite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invite already responded to"
        )
    
    return InviteActionResponse(
        message="Invite rejected",
        invite_id=invite_id,
        status=rejected_invite.status
    )

# ============ MEMBERS MANAGEMENT ============

@router.get("/{playlist_id}/members", response_model=List[GroupMemberResponse])
async def get_members(
    playlist_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all members of a group playlist"""
    # Check if user is a member
    is_member = await GroupMemberCRUD.is_member(db, playlist_id, current_user.id)
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this group playlist"
        )
    
    members = await GroupMemberCRUD.get_all_members(db, playlist_id)
    
    return [
        GroupMemberResponse(
            id=member.id,
            group_playlist_id=member.group_playlist_id,
            user_id=member.user_id,
            role=member.role,
            joined_at=member.joined_at,
            username=member.user.username,
            full_name=member.user.full_name,
            profile_image=member.user.profile_image
        )
        for member in members
    ]

@router.patch("/{playlist_id}/members/{user_id}/role", response_model=GroupMemberResponse)
async def update_member_role(
    playlist_id: int,
    user_id: int,
    role_data: UpdateMemberRole,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a member's role (owner only)"""
    # Get requester's role
    requester_role = await GroupMemberCRUD.get_member_role(db, playlist_id, current_user.id)
    if not requester_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this group playlist"
        )
    
    # Get target member
    target_member = await GroupMemberCRUD.get_member(db, playlist_id, user_id)
    if not target_member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    
    # Check permission
    if not GroupPermissions.can_update_member_role(
        requester_role, target_member.role, role_data.role
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to change this member's role"
        )
    
    # Update role
    updated_member = await GroupMemberCRUD.update_role(db, playlist_id, user_id, role_data.role)
    
    return GroupMemberResponse(
        id=updated_member.id,
        group_playlist_id=updated_member.group_playlist_id,
        user_id=updated_member.user_id,
        role=updated_member.role,
        joined_at=updated_member.joined_at,
        username=updated_member.user.username,
        full_name=updated_member.user.full_name,
        profile_image=updated_member.user.profile_image
    )

@router.delete("/{playlist_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    playlist_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove a member from group playlist"""
    # Get requester's role
    requester_role = await GroupMemberCRUD.get_member_role(db, playlist_id, current_user.id)
    if not requester_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this group playlist"
        )
    
    # Get target member
    target_member = await GroupMemberCRUD.get_member(db, playlist_id, user_id)
    if not target_member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    
    # Check permission
    is_self = user_id == current_user.id
    if not GroupPermissions.can_remove_member(requester_role, target_member.role, is_self):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to remove this member"
        )
    
    # Cannot remove owner
    if target_member.role == MemberRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove the owner. Transfer ownership first or delete the playlist."
        )
    
    success = await GroupMemberCRUD.remove_member(db, playlist_id, user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")

# ============ VIDEOS MANAGEMENT ============

@router.post("/{playlist_id}/videos/youtube", response_model=GroupVideoResponse, status_code=status.HTTP_201_CREATED)
async def add_video_from_youtube(
    playlist_id: int,
    youtube_url: str,
    user_description: str = None,
    current_user: User = Depends(rate_limit("add_video_group", 60, 60)),
    db: AsyncSession = Depends(get_db)
):
    """Add video to group playlist from YouTube URL (all members can add)"""
    # Check if user is a member and get role
    member_role = await GroupMemberCRUD.get_member_role(db, playlist_id, current_user.id)
    if not member_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this group playlist"
        )
    
    # Check permission
    if not GroupPermissions.can_add_video(member_role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to add videos"
        )
    
    # Fetch video metadata from YouTube
    try:
        video_data = await get_video_metadata(youtube_url)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    # Check for duplicates
    if await GroupVideoCRUD.check_duplicate(db, playlist_id, video_data["youtube_id"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Video already exists in this group playlist"
        )
    
    # Create video entry
    video_create = GroupVideoCreate(
        **video_data,
        user_description=user_description,
        position=0
    )
    
    video = await GroupVideoCRUD.create(db, playlist_id, video_create, current_user.id)
    
    # Format response
    return GroupVideoResponse(
        id=video.id,
        group_playlist_id=video.group_playlist_id,
        youtube_id=video.youtube_id,
        title=video.title,
        channel_name=video.channel_name,
        thumbnail=video.thumbnail,
        views=video.views,
        youtube_description=video.youtube_description,
        user_description=video.user_description,
        added_by_id=video.added_by_id,
        position=video.position,
        created_at=video.created_at,
        updated_at=video.updated_at,
        added_by_username=current_user.username
    )

@router.post("/{playlist_id}/videos", response_model=GroupVideoResponse, status_code=status.HTTP_201_CREATED)
async def add_video(
    playlist_id: int,
    video_data: GroupVideoCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add a video to group playlist (all members can add)"""
    # Check if user is a member and get role
    member_role = await GroupMemberCRUD.get_member_role(db, playlist_id, current_user.id)
    if not member_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this group playlist"
        )
    
    # Check permission
    if not GroupPermissions.can_add_video(member_role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to add videos"
        )
    
    video = await GroupVideoCRUD.create(db, playlist_id, video_data, current_user.id)
    
    # Format response
    return GroupVideoResponse(
        id=video.id,
        group_playlist_id=video.group_playlist_id,
        youtube_id=video.youtube_id,
        title=video.title,
        channel_name=video.channel_name,
        thumbnail=video.thumbnail,
        views=video.views,
        youtube_description=video.youtube_description,
        user_description=video.user_description,
        added_by_id=video.added_by_id,
        position=video.position,
        created_at=video.created_at,
        updated_at=video.updated_at,
        added_by_username=current_user.username
    )

@router.get("/{playlist_id}/videos", response_model=List[GroupVideoResponse])
async def get_videos(
    playlist_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all videos in a group playlist"""
    # Check if user is a member
    is_member = await GroupMemberCRUD.is_member(db, playlist_id, current_user.id)
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this group playlist"
        )
    
    videos = await GroupVideoCRUD.get_playlist_videos(db, playlist_id)
    
    return [
        GroupVideoResponse(
            id=video.id,
            group_playlist_id=video.group_playlist_id,
            youtube_id=video.youtube_id,
            title=video.title,
            channel_name=video.channel_name,
            thumbnail=video.thumbnail,
            views=video.views,
            youtube_description=video.youtube_description,
            user_description=video.user_description,
            added_by_id=video.added_by_id,
            position=video.position,
            created_at=video.created_at,
            updated_at=video.updated_at,
            added_by_username=video.added_by.username if video.added_by else None
        )
        for video in videos
    ]

@router.delete("/{playlist_id}/videos/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_video(
    playlist_id: int,
    video_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a video from group playlist (permission-based)"""
    # Get member role
    member_role = await GroupMemberCRUD.get_member_role(db, playlist_id, current_user.id)
    if not member_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this group playlist"
        )
    
    # Get video
    video = await GroupVideoCRUD.get_by_id(db, video_id, load_added_by=True)
    if not video or video.group_playlist_id != playlist_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    
    # Check permission
    if not GroupPermissions.can_delete_video(member_role, video, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this video"
        )
    
    success = await GroupVideoCRUD.delete(db, video_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")

# ============ BULK PLAYLIST IMPORT ============

@router.post("/{playlist_id}/videos/import-playlist", response_model=PlaylistImportResponse)
async def import_youtube_playlist(
    playlist_id: int,
    import_data: PlaylistImportRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(rate_limit("import_playlist", 5, 3600)),
    db: AsyncSession = Depends(get_db)
):
    """
    Import entire YouTube playlist (runs in background)
    Returns immediately with task_id for progress tracking
    """
    # Check if user is a member and get role
    member_role = await GroupMemberCRUD.get_member_role(db, playlist_id, current_user.id)
    if not member_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this group playlist"
        )
    
    # Check permission
    if not GroupPermissions.can_add_video(member_role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to add videos"
        )
    
    # Check if playlist exists
    playlist = await GroupPlaylistCRUD.get_by_id(db, playlist_id)
    if not playlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group playlist not found")
    
    # Generate unique task ID
    task_id = f"import_{uuid.uuid4().hex[:12]}"
    
    # Quick validation of YouTube playlist URL
    if "list=" not in import_data.youtube_playlist_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid YouTube playlist URL"
        )
    
    # Add background task (creates new DB session internally)
    async def run_import_task():
        async with async_session_maker() as new_db:
            await import_playlist_task(
                db=new_db,
                task_id=task_id,
                playlist_id=playlist_id,
                youtube_playlist_url=import_data.youtube_playlist_url,
                added_by_id=current_user.id,
                max_videos=import_data.max_videos
            )
    
    background_tasks.add_task(run_import_task)
    
    return PlaylistImportResponse(
        message="Playlist import started in background",
        task_id=task_id,
        estimated_videos=import_data.max_videos,
        status_endpoint=f"/api/group-playlists/import-status/{task_id}"
    )

@router.get("/import-status/{task_id}", response_model=ImportStatusResponse)
async def get_import_status(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get the status of a playlist import task"""
    cache_key = generate_cache_key("import_task", task_id)
    progress = get_cached_data(cache_key)
    
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Import task not found or expired"
        )
    
    return ImportStatusResponse(**progress)
# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.ext.asyncio import AsyncSession
# from database import get_db
# from utils.auth import get_current_user
# from utils.youtube import get_video_metadata
# from models.user import User
# from models.group_member import MemberRole
# from schemas.group_playlist import (
#     GroupPlaylistCreate, GroupPlaylistUpdate, 
#     GroupPlaylistResponse, GroupPlaylistDetailResponse
# )
# from schemas.group_member import GroupMemberResponse, UpdateMemberRole
# from schemas.group_video import GroupVideoCreate, GroupVideoUpdate, GroupVideoResponse
# from schemas.group_invite import GroupInviteCreate, GroupInviteResponse, InviteActionResponse
# from crud.group_playlist import GroupPlaylistCRUD
# from crud.group_member import GroupMemberCRUD
# from crud.group_video import GroupVideoCRUD
# from crud.group_invite import GroupInviteCRUD
# from utils.group_permissions import GroupPermissions
# from typing import List

# router = APIRouter(prefix="/api/group-playlists", tags=["Group Playlists"])

# # ============ PLAYLIST CRUD ============

# @router.post("/", response_model=GroupPlaylistResponse, status_code=status.HTTP_201_CREATED)
# async def create_group_playlist(
#     playlist_data: GroupPlaylistCreate,
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     """Create a new group playlist (user becomes owner)"""
#     playlist = await GroupPlaylistCRUD.create(db, playlist_data, current_user.id)
#     return playlist

# @router.get("/", response_model=List[GroupPlaylistResponse])
# async def get_my_group_playlists(
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     """Get all group playlists where current user is a member"""
#     playlists = await GroupPlaylistCRUD.get_user_playlists(db, current_user.id)
#     return playlists

# @router.get("/owned", response_model=List[GroupPlaylistResponse])
# async def get_owned_playlists(
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     """Get all group playlists owned by current user"""
#     playlists = await GroupPlaylistCRUD.get_owned_playlists(db, current_user.id)
#     return playlists

# @router.get("/{playlist_id}", response_model=GroupPlaylistDetailResponse)
# async def get_group_playlist(
#     playlist_id: int,
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     """Get group playlist details"""
#     # Check if user is a member
#     is_member = await GroupMemberCRUD.is_member(db, playlist_id, current_user.id)
#     if not is_member:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="You are not a member of this group playlist"
#         )
    
#     playlist = await GroupPlaylistCRUD.get_by_id(db, playlist_id, load_members=True, load_videos=True)
#     if not playlist:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group playlist not found")
    
#     return playlist

# @router.patch("/{playlist_id}", response_model=GroupPlaylistResponse)
# async def update_group_playlist(
#     playlist_id: int,
#     playlist_data: GroupPlaylistUpdate,
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     """Update group playlist (owner/admin only)"""
#     # Check permission
#     member_role = await GroupMemberCRUD.get_member_role(db, playlist_id, current_user.id)
#     if not member_role or not GroupPermissions.can_update_playlist(member_role):
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Only owner and admin can update playlist details"
#         )
    
#     playlist = await GroupPlaylistCRUD.update(db, playlist_id, playlist_data)
#     if not playlist:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group playlist not found")
    
#     return playlist

# @router.delete("/{playlist_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_group_playlist(
#     playlist_id: int,
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     """Delete group playlist (owner only)"""
#     # Check permission
#     member_role = await GroupMemberCRUD.get_member_role(db, playlist_id, current_user.id)
#     if not member_role or not GroupPermissions.can_delete_playlist(member_role):
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Only owner can delete the playlist"
#         )
    
#     success = await GroupPlaylistCRUD.delete(db, playlist_id)
#     if not success:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group playlist not found")

# # ============ INVITE SYSTEM ============

# @router.post("/{playlist_id}/invite", response_model=GroupInviteResponse, status_code=status.HTTP_201_CREATED)
# async def invite_user(
#     playlist_id: int,
#     invite_data: GroupInviteCreate,
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     """Invite a user to group playlist (owner/admin only)"""
#     # Check if playlist exists
#     playlist = await GroupPlaylistCRUD.get_by_id(db, playlist_id)
#     if not playlist:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group playlist not found")
    
#     # Check permission
#     member_role = await GroupMemberCRUD.get_member_role(db, playlist_id, current_user.id)
#     if not member_role or not GroupPermissions.can_invite_members(member_role):
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Only owner and admin can invite members"
#         )
    
#     # Check if invitee is already a member
#     is_member = await GroupMemberCRUD.is_member(db, playlist_id, invite_data.invitee_id)
#     if is_member:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="User is already a member"
#         )
    
#     # Create invite
#     invite = await GroupInviteCRUD.create(
#         db, playlist_id, current_user.id, invite_data.invitee_id
#     )
#     if not invite:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Failed to create invite"
#         )
    
#     # Load relationships for response
#     invite = await GroupInviteCRUD.get_by_id(db, invite.id)
    
#     # Format response
#     return GroupInviteResponse(
#         id=invite.id,
#         group_playlist_id=invite.group_playlist_id,
#         inviter_id=invite.inviter_id,
#         invitee_id=invite.invitee_id,
#         status=invite.status,
#         created_at=invite.created_at,
#         expires_at=invite.expires_at,
#         responded_at=invite.responded_at,
#         group_playlist_title=invite.group_playlist.title,
#         inviter_username=invite.inviter.username,
#         invitee_username=invite.invitee.username
#     )

# @router.get("/invites/pending", response_model=List[GroupInviteResponse])
# async def get_pending_invites(
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     """Get all pending invites for current user"""
#     invites = await GroupInviteCRUD.get_user_pending_invites(db, current_user.id)
    
#     return [
#         GroupInviteResponse(
#             id=invite.id,
#             group_playlist_id=invite.group_playlist_id,
#             inviter_id=invite.inviter_id,
#             invitee_id=invite.invitee_id,
#             status=invite.status,
#             created_at=invite.created_at,
#             expires_at=invite.expires_at,
#             responded_at=invite.responded_at,
#             group_playlist_title=invite.group_playlist.title,
#             inviter_username=invite.inviter.username,
#             invitee_username=invite.invitee.username
#         )
#         for invite in invites
#     ]

# @router.post("/invites/{invite_id}/accept", response_model=InviteActionResponse)
# async def accept_invite(
#     invite_id: int,
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     """Accept an invite"""
#     invite = await GroupInviteCRUD.get_by_id(db, invite_id)
#     if not invite:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invite not found")
    
#     if invite.invitee_id != current_user.id:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="This invite is not for you"
#         )
    
#     # Accept invite
#     accepted_invite = await GroupInviteCRUD.accept_invite(db, invite_id)
#     if not accepted_invite:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invite already responded to or expired"
#         )
    
#     # Add user as member
#     await GroupMemberCRUD.add_member(
#         db, invite.group_playlist_id, current_user.id, MemberRole.MEMBER
#     )
    
#     return InviteActionResponse(
#         message="Invite accepted successfully",
#         invite_id=invite_id,
#         status=accepted_invite.status
#     )

# @router.post("/invites/{invite_id}/reject", response_model=InviteActionResponse)
# async def reject_invite(
#     invite_id: int,
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     """Reject an invite"""
#     invite = await GroupInviteCRUD.get_by_id(db, invite_id)
#     if not invite:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invite not found")
    
#     if invite.invitee_id != current_user.id:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="This invite is not for you"
#         )
    
#     rejected_invite = await GroupInviteCRUD.reject_invite(db, invite_id)
#     if not rejected_invite:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invite already responded to"
#         )
    
#     return InviteActionResponse(
#         message="Invite rejected",
#         invite_id=invite_id,
#         status=rejected_invite.status
#     )

# # ============ MEMBERS MANAGEMENT ============

# @router.get("/{playlist_id}/members", response_model=List[GroupMemberResponse])
# async def get_members(
#     playlist_id: int,
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     """Get all members of a group playlist"""
#     # Check if user is a member
#     is_member = await GroupMemberCRUD.is_member(db, playlist_id, current_user.id)
#     if not is_member:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="You are not a member of this group playlist"
#         )
    
#     members = await GroupMemberCRUD.get_all_members(db, playlist_id)
    
#     return [
#         GroupMemberResponse(
#             id=member.id,
#             group_playlist_id=member.group_playlist_id,
#             user_id=member.user_id,
#             role=member.role,
#             joined_at=member.joined_at,
#             username=member.user.username,
#             full_name=member.user.full_name,
#             profile_image=member.user.profile_image
#         )
#         for member in members
#     ]

# @router.patch("/{playlist_id}/members/{user_id}/role", response_model=GroupMemberResponse)
# async def update_member_role(
#     playlist_id: int,
#     user_id: int,
#     role_data: UpdateMemberRole,
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     """Update a member's role (owner only)"""
#     # Get requester's role
#     requester_role = await GroupMemberCRUD.get_member_role(db, playlist_id, current_user.id)
#     if not requester_role:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="You are not a member of this group playlist"
#         )
    
#     # Get target member
#     target_member = await GroupMemberCRUD.get_member(db, playlist_id, user_id)
#     if not target_member:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    
#     # Check permission
#     if not GroupPermissions.can_update_member_role(
#         requester_role, target_member.role, role_data.role
#     ):
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="You don't have permission to change this member's role"
#         )
    
#     # Update role
#     updated_member = await GroupMemberCRUD.update_role(db, playlist_id, user_id, role_data.role)
    
#     return GroupMemberResponse(
#         id=updated_member.id,
#         group_playlist_id=updated_member.group_playlist_id,
#         user_id=updated_member.user_id,
#         role=updated_member.role,
#         joined_at=updated_member.joined_at,
#         username=updated_member.user.username,
#         full_name=updated_member.user.full_name,
#         profile_image=updated_member.user.profile_image
#     )

# @router.delete("/{playlist_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def remove_member(
#     playlist_id: int,
#     user_id: int,
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     """Remove a member from group playlist"""
#     # Get requester's role
#     requester_role = await GroupMemberCRUD.get_member_role(db, playlist_id, current_user.id)
#     if not requester_role:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="You are not a member of this group playlist"
#         )
    
#     # Get target member
#     target_member = await GroupMemberCRUD.get_member(db, playlist_id, user_id)
#     if not target_member:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    
#     # Check permission
#     is_self = user_id == current_user.id
#     if not GroupPermissions.can_remove_member(requester_role, target_member.role, is_self):
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="You don't have permission to remove this member"
#         )
    
#     # Cannot remove owner
#     if target_member.role == MemberRole.OWNER:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Cannot remove the owner. Transfer ownership first or delete the playlist."
#         )
    
#     success = await GroupMemberCRUD.remove_member(db, playlist_id, user_id)
#     if not success:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")

# # ============ VIDEOS MANAGEMENT ============

# @router.post("/{playlist_id}/videos/youtube", response_model=GroupVideoResponse, status_code=status.HTTP_201_CREATED)
# async def add_video_from_youtube(
#     playlist_id: int,
#     youtube_url: str,
#     user_description: str = None,
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     """Add video to group playlist from YouTube URL (all members can add)"""
#     # Check if user is a member and get role
#     member_role = await GroupMemberCRUD.get_member_role(db, playlist_id, current_user.id)
#     if not member_role:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="You are not a member of this group playlist"
#         )
    
#     # Check permission
#     if not GroupPermissions.can_add_video(member_role):
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="You don't have permission to add videos"
#         )
    
#     # Fetch video metadata from YouTube
#     try:
#         video_data = await get_video_metadata(youtube_url)
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
#     # Check for duplicates
#     if await GroupVideoCRUD.check_duplicate(db, playlist_id, video_data["youtube_id"]):
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Video already exists in this group playlist"
#         )
    
#     # Create video entry
#     video_create = GroupVideoCreate(
#         **video_data,
#         user_description=user_description,
#         position=0
#     )
    
#     video = await GroupVideoCRUD.create(db, playlist_id, video_create, current_user.id)
    
#     # Format response
#     return GroupVideoResponse(
#         id=video.id,
#         group_playlist_id=video.group_playlist_id,
#         youtube_id=video.youtube_id,
#         title=video.title,
#         channel_name=video.channel_name,
#         thumbnail=video.thumbnail,
#         views=video.views,
#         youtube_description=video.youtube_description,
#         user_description=video.user_description,
#         added_by_id=video.added_by_id,
#         position=video.position,
#         created_at=video.created_at,
#         updated_at=video.updated_at,
#         added_by_username=current_user.username
#     )

# @router.post("/{playlist_id}/videos", response_model=GroupVideoResponse, status_code=status.HTTP_201_CREATED)
# async def add_video(
#     playlist_id: int,
#     video_data: GroupVideoCreate,
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     """Add a video to group playlist (all members can add)"""
#     # Check if user is a member and get role
#     member_role = await GroupMemberCRUD.get_member_role(db, playlist_id, current_user.id)
#     if not member_role:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="You are not a member of this group playlist"
#         )
    
#     # Check permission
#     if not GroupPermissions.can_add_video(member_role):
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="You don't have permission to add videos"
#         )
    
#     video = await GroupVideoCRUD.create(db, playlist_id, video_data, current_user.id)
    
#     # Format response
#     return GroupVideoResponse(
#         id=video.id,
#         group_playlist_id=video.group_playlist_id,
#         youtube_id=video.youtube_id,
#         title=video.title,
#         channel_name=video.channel_name,
#         thumbnail=video.thumbnail,
#         views=video.views,
#         youtube_description=video.youtube_description,
#         user_description=video.user_description,
#         added_by_id=video.added_by_id,
#         position=video.position,
#         created_at=video.created_at,
#         updated_at=video.updated_at,
#         added_by_username=current_user.username
#     )

# @router.get("/{playlist_id}/videos", response_model=List[GroupVideoResponse])
# async def get_videos(
#     playlist_id: int,
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     """Get all videos in a group playlist"""
#     # Check if user is a member
#     is_member = await GroupMemberCRUD.is_member(db, playlist_id, current_user.id)
#     if not is_member:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="You are not a member of this group playlist"
#         )
    
#     videos = await GroupVideoCRUD.get_playlist_videos(db, playlist_id)
    
#     return [
#         GroupVideoResponse(
#             id=video.id,
#             group_playlist_id=video.group_playlist_id,
#             youtube_id=video.youtube_id,
#             title=video.title,
#             channel_name=video.channel_name,
#             thumbnail=video.thumbnail,
#             views=video.views,
#             youtube_description=video.youtube_description,
#             user_description=video.user_description,
#             added_by_id=video.added_by_id,
#             position=video.position,
#             created_at=video.created_at,
#             updated_at=video.updated_at,
#             added_by_username=video.added_by.username if video.added_by else None
#         )
#         for video in videos
#     ]

# @router.delete("/{playlist_id}/videos/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_video(
#     playlist_id: int,
#     video_id: int,
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     """Delete a video from group playlist (permission-based)"""
#     # Get member role
#     member_role = await GroupMemberCRUD.get_member_role(db, playlist_id, current_user.id)
#     if not member_role:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="You are not a member of this group playlist"
#         )
    
#     # Get video
#     video = await GroupVideoCRUD.get_by_id(db, video_id, load_added_by=True)
#     if not video or video.group_playlist_id != playlist_id:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    
#     # Check permission
#     if not GroupPermissions.can_delete_video(member_role, video, current_user.id):
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="You don't have permission to delete this video"
#         )
    
#     success = await GroupVideoCRUD.delete(db, video_id)
#     if not success:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")