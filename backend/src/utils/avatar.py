from typing import Optional
import hashlib

def get_avatar_url(user_id: str, size: int = 120) -> str:
    """
    Generate a MultiAvatar URL for a user based on their ID.
    
    Args:
        user_id: The unique identifier for the user
        size: The size of the avatar in pixels (default: 120)
    
    Returns:
        str: URL to the user's MultiAvatar
    """
    # Create a hash of the user ID for consistent avatar generation
    user_hash = hashlib.md5(user_id.encode('utf-8')).hexdigest()
    return f"https://api.multiavatar.com/{user_hash}.png?apikey=YOUR_API_KEY"
