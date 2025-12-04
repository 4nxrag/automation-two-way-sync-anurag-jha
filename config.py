import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """
    Central configuration class for all API credentials and settings.
    Think of this like exporting const CONFIG in JS.
    """
    
    # Airtable Settings
    AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
    AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
    AIRTABLE_TABLE_NAME = os.getenv('AIRTABLE_TABLE_NAME', 'Leads')
    
    # Trello Settings
    TRELLO_API_KEY = os.getenv('TRELLO_API_KEY')
    TRELLO_TOKEN = os.getenv('TRELLO_TOKEN')
    TRELLO_BOARD_ID = os.getenv('TRELLO_BOARD_ID')
    TRELLO_LIST_TODO_ID = os.getenv('TRELLO_LIST_TODO_ID')
    TRELLO_LIST_DONE_ID = os.getenv('TRELLO_LIST_DONE_ID')
    
    # Sync Settings
    SYNC_INTERVAL_SECONDS = int(os.getenv('SYNC_INTERVAL_SECONDS', 30))
    
    # Metadata identifier used in Trello card descriptions
    METADATA_MARKER = "---METADATA---"
    AIRTABLE_ID_PREFIX = "AIRTABLE_ID:"
    
    @classmethod
    def validate(cls):
        """
        Validates that all required environment variables are set.
        Similar to checking if(config.apiKey) in JS before starting app.
        """
        required_vars = {
            'AIRTABLE_API_KEY': cls.AIRTABLE_API_KEY,
            'AIRTABLE_BASE_ID': cls.AIRTABLE_BASE_ID,
            'TRELLO_API_KEY': cls.TRELLO_API_KEY,
            'TRELLO_TOKEN': cls.TRELLO_TOKEN,
            'TRELLO_BOARD_ID': cls.TRELLO_BOARD_ID,
            'TRELLO_LIST_TODO_ID': cls.TRELLO_LIST_TODO_ID,
            'TRELLO_LIST_DONE_ID': cls.TRELLO_LIST_DONE_ID,
        }
        
        missing = [key for key, value in required_vars.items() if not value]
        
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        return True
