from clients.airtable_client import AirtableClient
from clients.trello_client import TrelloClient
from config import Config
import time

class SyncService:
    """
    Core bi-directional sync logic between Airtable (Lead Tracker) 
    and Trello (Work Tracker).
    
    Status Mapping:
    - Airtable NEW/CONTACTED/IN_PROGRESS → Trello TODO list
    - Airtable QUALIFIED → Trello DONE list
    - Airtable LOST → No task created
    - Trello DONE → Airtable QUALIFIED
    """
    
    def __init__(self):
        self.airtable = AirtableClient()
        self.trello = TrelloClient()
        
        # Status mapping: Airtable → Trello List
        self.status_to_list_map = {
            "NEW": Config.TRELLO_LIST_TODO_ID,
            "CONTACTED": Config.TRELLO_LIST_TODO_ID,
            "IN_PROGRESS": Config.TRELLO_LIST_TODO_ID,
            "QUALIFIED": Config.TRELLO_LIST_DONE_ID,
        }
        
        # Reverse mapping: Trello List → Airtable Status
        self.list_to_status_map = {
            Config.TRELLO_LIST_DONE_ID: "QUALIFIED",
        }
    
    def initial_sync(self):
        """
        INITIAL SYNC: Create tasks in Trello for all existing Airtable leads.
        
        This is run once at startup or manually to establish the baseline.
        Idempotent: Won't create duplicates if tasks already exist.
        """
        print("\n" + "="*60)
        print("🚀 INITIAL SYNC: Airtable → Trello")
        print("="*60)
        
        try:
            # Fetch all leads from Airtable
            airtable_records = self.airtable.get_all_records()
            
            # Fetch existing Trello cards to check for duplicates
            trello_cards = self.trello.get_all_cards_on_board()
            
            # Build map of existing Airtable IDs in Trello
            existing_airtable_ids = set()
            for card in trello_cards:
                airtable_id = self.trello.extract_airtable_id_from_description(
                    card.get('desc', '')
                )
                if airtable_id:
                    existing_airtable_ids.add(airtable_id)
            
            print(f"Found {len(airtable_records)} leads in Airtable")
            print(f"Found {len(existing_airtable_ids)} already synced to Trello\n")
            
            created_count = 0
            skipped_count = 0
            
            # Process each lead
            for record in airtable_records:
                record_id = record['id']
                fields = record.get('fields', {})
                
                # Extract lead data
                lead_name = fields.get('Name', 'Unnamed Lead')
                lead_status = fields.get('Status', 'NEW')
                lead_email = fields.get('Email', '')
                lead_source = fields.get('Source', '')
                
                # Skip if status is LOST (per assignment requirements)
                if lead_status == "LOST":
                    print(f"  ⊝ Skipping LOST lead: {lead_name}")
                    skipped_count += 1
                    continue
                
                # IDEMPOTENCY CHECK: Skip if already exists
                if record_id in existing_airtable_ids:
                    print(f"  ✓ Already synced: {lead_name}")
                    skipped_count += 1
                    continue
                
                # Determine which Trello list to use
                target_list_id = self.status_to_list_map.get(
                    lead_status,
                    Config.TRELLO_LIST_TODO_ID  # Default to TODO
                )
                
                # Build card description with lead details
                card_description = self._build_task_description(
                    email=lead_email,
                    source=lead_source,
                    airtable_id=record_id
                )
                
                # Create Trello card (task)
                card_title = f"{lead_name} - {lead_status}"
                print(f"  + Creating task: {card_title}")
                
                result = self.trello.create_card(
                    name=card_title,
                    description=card_description,
                    list_id=target_list_id
                )
                
                if result:
                    created_count += 1
                
                # Rate limiting: Be gentle with APIs
                time.sleep(0.5)
            
            print(f"\n✅ Initial sync complete:")
            print(f"   - Created: {created_count} tasks")
            print(f"   - Skipped: {skipped_count} (already synced or LOST)")
            
        except Exception as e:
            print(f"\n❌ Initial sync failed: {e}")
            raise
    
    def sync_airtable_to_trello(self):
        """
        CONTINUOUS SYNC: Airtable → Trello
        
        Updates existing tasks when lead status changes.
        Creates new tasks for new leads.
        
        IMPORTANT: Does NOT move cards that are already in DONE list
        (DONE list = user manually marked complete, takes priority)
        """
        print("\n🔄 Syncing: Airtable → Trello...")
        
        try:
            airtable_records = self.airtable.get_all_records()
            trello_cards = self.trello.get_all_cards_on_board()
            
            # Build lookup map: {airtable_id: trello_card}
            trello_card_map = {}
            for card in trello_cards:
                airtable_id = self.trello.extract_airtable_id_from_description(
                    card.get('desc', '')
                )
                if airtable_id:
                    trello_card_map[airtable_id] = card
            
            for record in airtable_records:
                record_id = record['id']
                fields = record.get('fields', {})
                
                lead_name = fields.get('Name', 'Unnamed Lead')
                lead_status = fields.get('Status', 'NEW')
                lead_email = fields.get('Email', '')
                lead_source = fields.get('Source', '')
                
                # Skip LOST leads
                if lead_status == "LOST":
                    continue
                
                # Determine target list based on Airtable status
                target_list_id = self.status_to_list_map.get(
                    lead_status,
                    Config.TRELLO_LIST_TODO_ID
                )
                
                if record_id in trello_card_map:
                    # EXISTS - check if update needed
                    existing_card = trello_card_map[record_id]
                    current_list_id = existing_card.get('idList')
                    current_name = existing_card.get('name', '')
                    
                    # 🔥 KEY FIX: Don't touch cards that are in DONE list
                    # User manually moved them there - respect that decision
                    if current_list_id == Config.TRELLO_LIST_DONE_ID:
                        print(f"  🔒 Skipping (in DONE list): {lead_name}")
                        continue
                    
                    new_name = f"{lead_name} - {lead_status}"
                    
                    # Update if status changed (list or name different)
                    needs_update = (
                        current_list_id != target_list_id or
                        current_name != new_name
                    )
                    
                    if needs_update:
                        print(f"  ↻ Updating: {lead_name} (status: {lead_status})")
                        self.trello.update_card(
                            card_id=existing_card['id'],
                            name=new_name,
                            list_id=target_list_id
                        )
                    else:
                        print(f"  ✓ Up-to-date: {lead_name}")
                else:
                    # DOESN'T EXIST - create new
                    print(f"  + Creating: {lead_name} - {lead_status}")
                    
                    card_description = self._build_task_description(
                        email=lead_email,
                        source=lead_source,
                        airtable_id=record_id
                    )
                    
                    self.trello.create_card(
                        name=f"{lead_name} - {lead_status}",
                        description=card_description,
                        list_id=target_list_id
                    )
                    
                    time.sleep(0.5)  # Rate limiting
            
        except Exception as e:
            print(f"✗ Airtable → Trello sync error: {e}")
    
    def sync_trello_to_airtable(self):
        """
        REVERSE SYNC: Trello → Airtable
        
        When a task is moved to DONE list, mark the lead as QUALIFIED.
        Implements idempotency: Won't update if already QUALIFIED.
        """
        print("\n🔄 Syncing: Trello → Airtable...")
        
        try:
            trello_cards = self.trello.get_all_cards_on_board()
            airtable_records = self.airtable.get_all_records()
            
            # Build status lookup
            airtable_status_map = {
                record['id']: record.get('fields', {}).get('Status')
                for record in airtable_records
            }
            
            # Process each card
            for card in trello_cards:
                card_name = card.get('name', 'Unknown')
                card_list_id = card.get('idList')
                card_description = card.get('desc', '')
                
                # Extract linked Airtable ID
                airtable_id = self.trello.extract_airtable_id_from_description(
                    card_description
                )
                
                if not airtable_id:
                    continue
                
                # Check if this list triggers a status update
                if card_list_id not in self.list_to_status_map:
                    continue
                
                desired_status = self.list_to_status_map[card_list_id]
                current_status = airtable_status_map.get(airtable_id)
                
                # IDEMPOTENCY: Only update if different
                if current_status == desired_status:
                    print(f"  ✓ Already {desired_status}: {card_name}")
                    continue
                
                # Update Airtable
                print(f"  ↻ Marking as {desired_status}: {card_name}")
                self.airtable.update_record_status(
                    record_id=airtable_id,
                    status=desired_status
                )
                
                time.sleep(0.5)  # Rate limiting
            
        except Exception as e:
            print(f"✗ Trello → Airtable sync error: {e}")
    
    def _build_task_description(self, email, source, airtable_id):
        """
        Build task description with lead details and metadata footer.
        
        Format:
        Email: john@example.com
        Source: LinkedIn
        
        ---METADATA---
        AIRTABLE_ID: rec123abc
        """
        parts = []
        
        if email:
            parts.append(f"Email: {email}")
        if source:
            parts.append(f"Source: {source}")
        
        content = "\n".join(parts) if parts else "No additional details"
        
        return self.trello.build_card_description_with_metadata(
            content=content,
            airtable_id=airtable_id
        )
    
    def run_sync_cycle(self):
        """
        Execute one complete bi-directional sync cycle.
        """
        try:
            self.sync_airtable_to_trello()
            self.sync_trello_to_airtable()
            print("\n✅ Sync cycle completed\n")
        except Exception as e:
            print(f"\n❌ Sync cycle error: {e}\n")
            # Log but don't crash - continue to next cycle
