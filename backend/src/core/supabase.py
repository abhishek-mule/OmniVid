import os

from dotenv import load_dotenv
from supabase import Client, create_client

# Load environment variables
load_dotenv()

# Initialize Supabase client
url: str = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
key: str = os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")
service_key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

# Create clients
supabase: Client = create_client(url, key)
supabase_admin: Client = create_client(url, service_key)


def get_supabase() -> Client:
    """Get Supabase client for regular operations."""
    return supabase


def get_supabase_admin() -> Client:
    """Get Supabase client for admin operations."""
    return supabase_admin
