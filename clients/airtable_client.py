import requests
from config import Config

class AirtableClient:
    """
    Wrapper for Airtable API operations.
    In JS/TS, this is like a class with async methods for API calls.
    """
    
    def __init__(self):
        self.base_url = f"https://api.airtable.com/v0/{Config.AIRTABLE_BASE_ID}/{Config.AIRTABLE_TABLE_NAME}"
        self.headers = {
            "Authorization": f"Bearer {Config.AIRTABLE_API_KEY}",
            "Content-Type": "application/json"
        }
    
    def get_all_records(self):
        """
        Fetch all records from Airtable with pagination handling.
        Returns: List of all records (Python list = JS array)
        
        Note: Airtable paginates at 100 records per request.
        In JS this would be like: const records = await fetchAllPages()
        """
        all_records = []
        offset = None
        
        try:
            while True:
                # Build URL with optional offset parameter for pagination
                params = {"offset": offset} if offset else {}
                
                response = requests.get(
                    self.base_url,
                    headers=self.headers,
                    params=params,
                    timeout=10
                )
                
                # Raise exception for 4xx/5xx status codes
                # Similar to: if (!response.ok) throw new Error()
                response.raise_for_status()
                
                data = response.json()
                records = data.get('records', [])
                all_records.extend(records)  # Like: allRecords.push(...records) in JS
                
                # Check if there are more pages
                offset = data.get('offset')
                if not offset:
                    break
            
            print(f"✓ Fetched {len(all_records)} records from Airtable")
            return all_records
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Error fetching Airtable records: {e}")
            return []
    
    def update_record_status(self, record_id, status):
        """
        Update a single record's status field.
        Args:
            record_id: The Airtable record ID (like rec123abc)
            status: New status value (e.g., "QUALIFIED")
        
        In JS: await fetch(url, { method: 'PATCH', body: JSON.stringify(data) })
        """
        url = f"{self.base_url}/{record_id}"
        
        # Payload structure: {"fields": {"Status": "QUALIFIED"}}
        payload = {
            "fields": {
                "Status": status
            }
        }
        
        try:
            response = requests.patch(
                url,
                headers=self.headers,
                json=payload,  # 'json' parameter auto-serializes dict to JSON
                timeout=10
            )
            
            response.raise_for_status()
            print(f"✓ Updated Airtable record {record_id} to status: {status}")
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Error updating Airtable record {record_id}: {e}")
            return None
