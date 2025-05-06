import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class SupabaseConfig:
    """
    Supabase configuration class for managing Supabase client and authentication.
    """

    # Supabase credentials from environment variables
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

    @classmethod
    def get_client(cls) -> Client:
        """
        Get a Supabase client instance using the anon key.

        Returns:
            Client: A Supabase client instance.
        """
        if not cls.SUPABASE_URL or not cls.SUPABASE_KEY:
            raise ValueError("Supabase URL and key must be set in environment variables")

        return create_client(cls.SUPABASE_URL, cls.SUPABASE_KEY)

    @classmethod
    def get_admin_client(cls) -> Client:
        """
        Get a Supabase client instance using the service role key for admin operations.

        Returns:
            Client: A Supabase client instance with admin privileges.
        """
        if not cls.SUPABASE_URL or not cls.SUPABASE_SERVICE_KEY:
            raise ValueError("Supabase URL and service key must be set in environment variables")

        return create_client(cls.SUPABASE_URL, cls.SUPABASE_SERVICE_KEY)