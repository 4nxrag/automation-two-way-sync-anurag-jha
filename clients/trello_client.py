import requests
import re
from config import Config

class TrelloClient:
    """
    Wrapper for Trello API operations.
    Includes special logic for parsing metadata from card descriptions.
    """
    
    def __init__(self):
        # Trello uses query parameters for auth (not headers)
        self.auth_params = {
            "key": Config.TRELLO_API_KEY,
            "token": Config.TRELLO_TOKEN
        }
        self.base_url = "https://api.trello.com/1"
    
    def get_all_cards_on_board(self):
        """
        Fetch all cards from the Trello board.
        Returns: List of card objects (Python list = JS array)
        
        In JS: const cards = await fetch(`/boards/${boardId}/cards`).then(r => r.json())
        """
        url = f"{self.base_url}/boards/{Config.TRELLO_BOARD_ID}/cards"
        
        try:
            response = requests.get(
                url,
                params=self.auth_params,
                timeout=10
            )
            
            response.raise_for_status()
            cards = response.json()
            print(f"✓ Fetched {len(cards)} cards from Trello")
            return cards
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Error fetching Trello cards: {e}")
            return []
    
    def extract_airtable_id_from_description(self, description):
        """
        Parse the Airtable ID from card description using regex.
        
        Regex Pattern Explanation:
        AIRTABLE_ID:\s*     -> Match "AIRTABLE_ID:" followed by optional whitespace
        (rec[A-Za-z0-9]+)   -> Capture group: "rec" + alphanumeric characters
        
        In JS: const match = description.match(r/AIRTABLE_ID:\s*(rec[A-Za-z0-9]+)/)
        Returns: Airtable ID string or None
        """
        if not description:
            return None
        
        # Compile regex pattern for better performance in loops
        pattern = r'AIRTABLE_ID:\s*(rec[A-Za-z0-9]+)'
        match = re.search(pattern, description)
        
        # In Python: match.group(1) gets first captured group
        # In JS: match[1] would get the same
        return match.group(1) if match else None
    
    def create_card(self, name, description, list_id):
        """
        Create a new Trello card.
        
        Args:
            name: Card title
            description: Card description (will contain metadata footer)
            list_id: Which list to create the card in
        
        In JS: await fetch('/cards', { method: 'POST', body: ... })
        """
        url = f"{self.base_url}/cards"
        
        # Merge auth params with card data
        # In Python: {**dict1, **dict2} is like {...obj1, ...obj2} in JS
        params = {
            **self.auth_params,
            "name": name,
            "desc": description,  # Trello API uses 'desc' not 'description'
            "idList": list_id
        }
        
        try:
            response = requests.post(
                url,
                params=params,
                timeout=10
            )
            
            response.raise_for_status()
            card = response.json()
            print(f"✓ Created Trello card: {name}")
            return card
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Error creating Trello card '{name}': {e}")
            return None
    
    def update_card(self, card_id, name=None, description=None, list_id=None):
        """
        Update an existing Trello card.
        
        Args are optional - only updates fields that are provided.
        In JS: await fetch(`/cards/${id}`, { method: 'PUT', body: ... })
        """
        url = f"{self.base_url}/cards/{card_id}"
        
        # Build params dict with only provided fields
        # In Python: dict comprehension filters out None values
        # In JS: Object.entries(obj).filter(([k,v]) => v !== null)
        params = {**self.auth_params}
        
        if name is not None:
            params["name"] = name
        if description is not None:
            params["desc"] = description
        if list_id is not None:
            params["idList"] = list_id
        
        try:
            response = requests.put(
                url,
                params=params,
                timeout=10
            )
            
            response.raise_for_status()
            print(f"✓ Updated Trello card: {card_id}")
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Error updating Trello card {card_id}: {e}")
            return None
    
    def build_card_description_with_metadata(self, content, airtable_id):
        """
        Build card description with metadata footer.
        
        Format:
        [User content]
        
        ---METADATA---
        AIRTABLE_ID: rec123abc
        
        In JS: return `${content}\n\n${METADATA_MARKER}\n${ID_PREFIX} ${id}`
        """
        metadata_footer = f"\n\n{Config.METADATA_MARKER}\n{Config.AIRTABLE_ID_PREFIX} {airtable_id}"
        return content + metadata_footer


