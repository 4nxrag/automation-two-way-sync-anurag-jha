from clients.airtable_client import AirtableClient

client = AirtableClient()
records = client.get_all_records()

print("\n" + "="*60)
print("AIRTABLE RECORDS DEBUG")
print("="*60)

for i, record in enumerate(records, 1):
    print(f"\n--- Record {i} ---")
    print(f"ID: {record['id']}")
    print(f"Fields: {record.get('fields', {})}")
    print(f"Available field names: {list(record.get('fields', {}).keys())}")

print("\n" + "="*60)
