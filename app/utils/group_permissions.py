from models.group_member import MemberRole
from models.group_playlist import GroupPlaylist
from models.group_video import GroupPlaylistVideo
from models.group_member import GroupPlaylistMember
from typing import Optional

class GroupPermissions:
    """Permission checker for group playlists"""
    
    @staticmethod
    def can_delete_video(
        member_role: MemberRole,
        video: GroupPlaylistVideo,
        current_user_id: int
    ) -> bool:
        """
        Check if user can delete a video from group playlist
        - OWNER and ADMIN: can delete any video
        - MEMBER: can only delete videos they added
        """
        if member_role in [MemberRole.OWNER, MemberRole.ADMIN]:
            return True
        
        if member_role == MemberRole.MEMBER:
            return video.added_by_id == current_user_id
        
        return False
    
    @staticmethod
    def can_add_video(member_role: MemberRole) -> bool:
        """
        Check if user can add video to group playlist
        - All members (OWNER, ADMIN, MEMBER) can add videos
        """
        return member_role in [MemberRole.OWNER, MemberRole.ADMIN, MemberRole.MEMBER]
    
    @staticmethod
    def can_invite_members(member_role: MemberRole) -> bool:
        """
        Check if user can invite new members
        - OWNER and ADMIN can invite
        - MEMBER cannot invite
        """
        return member_role in [MemberRole.OWNER, MemberRole.ADMIN]
    
    @staticmethod
    def can_remove_member(
        requester_role: MemberRole,
        target_role: MemberRole,
        is_self: bool = False
    ) -> bool:
        """
        Check if user can remove a member
        - OWNER can remove anyone except themselves
        - ADMIN can remove MEMBER only
        - MEMBER can leave (remove themselves)
        """
        # Members can always leave voluntarily
        if is_self and target_role == MemberRole.MEMBER:
            return True
        
        # Owner can remove ADMIN or MEMBER (but not themselves as owner)
        if requester_role == MemberRole.OWNER and target_role != MemberRole.OWNER:
            return True
        
        # Admin can only remove MEMBER
        if requester_role == MemberRole.ADMIN and target_role == MemberRole.MEMBER:
            return True
        
        return False
    
    @staticmethod
    def can_update_member_role(
        requester_role: MemberRole,
        target_current_role: MemberRole,
        target_new_role: MemberRole
    ) -> bool:
        """
        Check if user can update another member's role
        - Only OWNER can change roles
        - Cannot change OWNER role
        - Cannot promote to OWNER
        """
        if requester_role != MemberRole.OWNER:
            return False
        
        # Cannot change the owner
        if target_current_role == MemberRole.OWNER:
            return False
        
        # Cannot promote someone to owner
        if target_new_role == MemberRole.OWNER:
            return False
        
        return True
    
    @staticmethod
    def can_delete_playlist(member_role: MemberRole) -> bool:
        """
        Check if user can delete the entire group playlist
        - Only OWNER can delete the playlist
        """
        return member_role == MemberRole.OWNER
    
    @staticmethod
    def can_update_playlist(member_role: MemberRole) -> bool:
        """
        Check if user can update playlist details (title, description, etc.)
        - OWNER and ADMIN can update
        """
        return member_role in [MemberRole.OWNER, MemberRole.ADMIN]