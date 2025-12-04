import time
import sys
from config import Config
from services.sync_service import SyncService

def main():
    """
    Entry point for Airtable ↔ Trello bi-directional sync.
    
    Modes:
    - python main.py init      : Run initial sync only
    - python main.py           : Run continuous sync loop
    """
    
    print("=" * 60)
    print("  AIRTABLE ↔ TRELLO BI-DIRECTIONAL SYNC")
    print("  Lead Tracker → Work Tracker Integration")
    print("=" * 60)
    
    # Validate configuration
    try:
        Config.validate()
        print("✓ Configuration validated\n")
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\nMake sure your .env file has all required variables.")
        return
    
    # Initialize sync service
    sync_service = SyncService()
    
    # Check if running in "init" mode
    if len(sys.argv) > 1 and sys.argv[1] == "init":
        print("Running INITIAL SYNC mode...\n")
        sync_service.initial_sync()
        print("\n✅ Initial sync complete. Exiting.")
        return
    
    # Continuous sync mode
    print(f"🔁 Starting continuous sync (interval: {Config.SYNC_INTERVAL_SECONDS}s)")
    print("   Press Ctrl+C to stop\n")
    
    cycle_count = 0
    
    try:
        while True:
            cycle_count += 1
            print(f"{'─' * 60}")
            print(f"CYCLE #{cycle_count} - {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'─' * 60}")
            
            sync_service.run_sync_cycle()
            
            print(f"⏳ Waiting {Config.SYNC_INTERVAL_SECONDS}s until next sync...")
            time.sleep(Config.SYNC_INTERVAL_SECONDS)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Sync stopped by user")
        print(f"   Total cycles: {cycle_count}")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")

if __name__ == "__main__":
    main()
