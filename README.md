# Airtable ↔ Trello Bi-Directional Sync

A Python-based automation system that keeps lead data synchronized between Airtable (Lead Tracker) and Trello (Work Tracker) in real-time.

**Author:** Anurag Jha  
**Role:** Software Engineer Intern - Automation & Integrations (Take-home Assignment)  
**Date:** December 2025

---

## 📹 Demo Video

**Watch the full walkthrough:** [Google Drive Link](https://drive.google.com/file/d/1xK9sHboKzRaNCDxhvy_rRSO8BdpMXyRX/view?usp=sharing)

*(10-minute video covering architecture, code walkthrough, setup, and live demo)*

---

## Overview

This project implements a two-way sync between:
- **Airtable** (Lead Tracker) - Stores lead information (name, email, status, source)
- **Trello** (Work Tracker) - Manages tasks/follow-ups for each lead

The sync ensures that when a lead's status changes in Airtable, the corresponding Trello card updates automatically. Similarly, when a task is marked complete in Trello, the lead status in Airtable is updated.

### Why These Tools?

I chose Airtable and Trello because:
1. Both have generous free tiers with full API access
2. Airtable provides a clean spreadsheet-like interface for lead data (familiar for sales teams)
3. Trello offers visual kanban boards for task management (familiar for dev/ops teams)
4. Real-world use case: Many startups use this exact stack

---

## Architecture

### High-Level Flow

```
┌─────────────────┐                    ┌─────────────────┐
│   AIRTABLE      │                    │     TRELLO      │
│  (Lead Tracker) │                    │ (Work Tracker)  │
│                 │                    │                 │
│  ┌───────────┐  │                    │  ┌──────────┐   │
│  │ John Doe  │  │                    │  │  TODO    │   │
│  │ Status:   │  │◄───────────────────┤  │          │   │
│  │ QUALIFIED │  │    Sync Status     │  │ ┌──────┐ │   │
│  │           │  │                    │  │ │ Jane │ │   │
│  └───────────┘  │                    │  │ └──────┘ │   │
│                 │                    │  │          │   │
│                 │    Create/Update   │  │  DONE    │   │
│                 │◄───────────────────┤  │          │   │ 
│                 │                    │  │ ┌──────┐ │   │
│                 │    Mark Complete   │  │ │ John │ │   │
│                 ├───────────────────►│  │ └──────┘ │   │
│                 │                    │  └──────────┘   │
└─────────────────┘                    └─────────────────┘
         ▲                                      ▲
         │                                      │
         └──────────────┐      ┌───────────────┘
                        │      │
                  ┌─────▼──────▼─────┐
                  │  Python Sync     │
                  │  Service         │
                  │  (Polling Loop)  │
                  └──────────────────┘
```

### Sync Direction Logic

**Direction 1: Airtable → Trello**
- Reads all leads from Airtable
- Creates Trello cards for new leads
- Updates card names/lists when lead status changes
- **Special case:** Won't move cards that are already in DONE list (respects manual completion)

**Direction 2: Trello → Airtable**
- Monitors Trello cards on the board
- When a card is moved to DONE list → Updates Airtable lead status to QUALIFIED
- Only updates if status actually changed (idempotency)

---

## Status Mapping

I designed the following mapping based on typical sales workflows:

| Airtable Status | Trello List | Reasoning |
|----------------|-------------|-----------|
| NEW | TODO | Fresh lead, needs initial outreach |
| CONTACTED | TODO | Still in active follow-up phase |
| IN_PROGRESS | TODO | Ongoing conversation/demo scheduled |
| QUALIFIED | DONE | Deal closed or moved to next stage |
| LOST | (No card) | No point tracking lost opportunities |

| Trello List | Airtable Status | Reasoning |
|------------|-----------------|-----------|
| DONE | QUALIFIED | Manual completion = qualified lead |

**Why DONE → QUALIFIED only?**

I considered mapping TODO list movements back to Airtable, but decided against it because:
1. Creates potential sync loops (Airtable changes → Trello moves → Airtable changes again)
2. Trello is primarily for task *visualization*, not status management
3. DONE is the only clear signal of completion that deserves an Airtable update
4. Sales teams should update lead status in Airtable (source of truth), not by dragging cards

---

## Project Structure

```
automation-two-way-sync-anurag-jha/
│
├── clients/
│   ├── airtable_client.py      # Airtable API wrapper
│   └── trello_client.py         # Trello API wrapper + metadata parsing
│
├── services/
│   └── sync_service.py          # Core sync logic
│
├── config.py                    # Environment config & validation
├── main.py                      # Entry point + CLI
├── test_trello_auth.py          # Auth testing utility
├── debug_airtable.py            # Field debugging utility
│
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
├── .env                         # Your credentials (DO NOT COMMIT)
├── .gitignore                   # Git ignore rules
│
└── README.md                    # This file
```

## Setup Instructions

### Prerequisites

- Python 3.8+ installed
- Airtable account (free tier)
- Trello account (free tier)
- 15 minutes for setup

### Step 1: Clone & Install

git clone https://github.com/4nxrag/automation-two-way-sync-anurag-jha.git
cd automation-two-way-sync-anurag-jha

Create virtual environment
python -m venv venv

Activate (Windows)
venv\Scripts\activate

Activate (Mac/Linux)
source venv/bin/activate

Install dependencies
pip install -r requirements.txt


### Step 2: Set Up Airtable

1. **Create a Base:**
   - Go to [Airtable](https://airtable.com)
   - Create a new base called "Lead Tracker"
   - Create a table with these fields:

   | Field Name | Field Type | Options |
   |-----------|------------|---------|
   | Name | Single line text | - |
   | Email | Email | - |
   | Status | Single select | NEW, CONTACTED, IN_PROGRESS, QUALIFIED, LOST |
   | Source | Single select | LinkedIn, Website, Referral, Cold Call, Other |
   | Description | Long text | - |

2. **Add Sample Data:**
   - Create 2-3 test records with different statuses

3. **Get API Credentials:**
   - Go to [Airtable Account](https://airtable.com/account)
   - Generate a Personal Access Token with these scopes:
     - `data.records:read`
     - `data.records:write`
     - `schema.bases:read`
   - Copy your Base ID from the URL: `https://airtable.com/appXXXXXXXXXXXXXX/...`

### Step 3: Set Up Trello

1. **Create a Board:**
   - Go to [Trello](https://trello.com)
   - Create a new board called "Work Tracker"
   - Create two lists: **TODO** and **DONE**

2. **Get API Credentials:**
   - Go to [Trello Power-Ups Admin](https://trello.com/power-ups/admin/)
   - Click "New" to create a new Power-Up
   - Fill in any details (name, workspace, email)
   - Go to "API Key" tab → "Generate a new API Key"
   - Copy your **API Key** (32 characters)

3. **Generate Token:**
   - Replace `YOUR_API_KEY` in this URL:

https://trello.com/1/authorize?expiration=never&scope=read,write&response_type=token&name=SyncTool&key=YOUR_API_KEY

- Open it in browser → Click "Allow"
- Copy the **Token** (64 characters)

4. **Get Board & List IDs:**
- Open your Trello board
- Add `.json` to the URL: `https://trello.com/b/YOUR_BOARD_ID.json`
- Find the `"id"` field at the top (24 characters) = **Board ID**
- Search for `"lists"` → Copy the IDs for TODO and DONE lists

### Step 4: Configure Environment

Copy example file
cp .env.example .env

Edit .env with your credentials

Your `.env` should look like this:

Airtable Configuration
AIRTABLE_API_KEY=patXXXXXXXXXXXXXXXXXX
AIRTABLE_BASE_ID=appXXXXXXXXXXXXXX
AIRTABLE_TABLE_NAME=Lead Tracker

Trello Configuration
TRELLO_API_KEY=your_32_char_api_key_here
TRELLO_TOKEN=your_64_char_token_here
TRELLO_BOARD_ID=your_24_char_board_id_here
TRELLO_LIST_TODO_ID=your_todo_list_id_here
TRELLO_LIST_DONE_ID=your_done_list_id_here

Sync Configuration
SYNC_INTERVAL_SECONDS=30

### Step 5: Test & Run

Test Trello authentication
python test_trello_auth.py

Run initial sync (creates cards for existing leads)
python main.py init

Start continuous sync
python main.py

---

## Usage

### Initial Sync

Run once to create Trello cards for all existing Airtable leads:

python main.py init


**What it does:**
- Fetches all leads from Airtable
- Skips leads with status = LOST
- Creates Trello cards (won't create duplicates if already exist)
- Embeds Airtable record ID in card description for tracking

### Continuous Sync

Run the polling loop (checks every 30 seconds):

python main.py


**What it does:**
- Every 30 seconds:
  1. Syncs Airtable → Trello (create/update cards)
  2. Syncs Trello → Airtable (mark completed leads)
  3. Logs all actions to console
- Press `Ctrl+C` to stop

### Demo Scenarios

**Scenario 1: New Lead Created**
1. Add a new record in Airtable (Name: "Test Lead", Status: "NEW")
2. Wait 30 seconds
3. See new card appear in Trello TODO list

**Scenario 2: Lead Status Updated**
1. Change a lead's status from "NEW" to "CONTACTED" in Airtable
2. Wait 30 seconds
3. Card name updates in Trello

**Scenario 3: Task Completed**
1. Drag a card to DONE list in Trello
2. Wait 30 seconds
3. Corresponding lead in Airtable changes to "QUALIFIED"

---

## Technical Decisions

### Code Documentation Philosophy

You'll notice the code has more comments than typical production code. This is a deliberate choice for this assignment to demonstrate:

1. **Clear thinking** - Comments show I understand *why* each piece exists, not just *what* it does
2. **Team collaboration** - In startups, PMs, sales ops, and founders often read automation code
3. **Maintainability** - If I get hit by a bus tomorrow, someone else can pick this up
4. **Learning resource** - Since this is an interview assignment, I wanted to show my thought process

In a production setting with an experienced team, I'd reduce comment density but keep the architectural explanations.

### Why Polling Instead of Webhooks?

I chose a **polling architecture** (check every 30 seconds) instead of webhooks because:

**Pros of Polling:**
- Simpler implementation - no need for public endpoint
- No webhook payload verification complexity
- Works locally without ngrok/tunneling
- Easier to debug (just read the logs)
- Both Airtable and Trello have different webhook implementations - polling unifies them

**Cons of Polling:**
- Slight delay (30 seconds) vs instant webhooks
- More API calls (but well within free tier limits)

For this assignment and typical use cases (small teams, non-time-critical updates), polling is perfectly acceptable. In production, I'd recommend webhooks for scale.

### Idempotency Strategy

**Problem:** How do we know if a Trello card already exists for an Airtable lead?

**Solution:** I embed the Airtable record ID in the card description using a metadata footer:

Email: john@example.com
Source: LinkedIn

---METADATA---
AIRTABLE_ID: recXXXXXXXXXXXXXX


**Why not use Trello Custom Fields?**
Custom Fields are a paid feature. The description-based approach:
- Works on free tier
- Easy to parse with regex
- Human-readable (can manually verify)
- Won't break if sync fails

### Error Handling Philosophy

I used a **fail-gracefully** approach:

try:
# Sync operations
except Exception as e:
print(f"Error: {e}")
# Log but don't crash - continue to next cycle

**Why?**
- One bad record shouldn't kill the entire sync
- Transient API errors (rate limits, timeouts) are common
- Better to log and continue than crash at 3 AM

In production, I'd add:
- Structured logging (not just prints)
- Exponential backoff for retries
- Dead letter queue for failed records
- Monitoring/alerting

---

## Assumptions & Limitations

### Assumptions

1. **Status field exists:** Airtable table must have a "Status" field with specific values
2. **Single workspace:** Only syncs one Airtable base and one Trello board
3. **Manual first setup:** User must create both accounts and configure credentials
4. **Lead names are unique-ish:** No special handling for duplicate lead names
5. **No deletion sync:** Deleting a lead in Airtable won't delete the Trello card (by design)

### Known Limitations

1. **No conflict resolution:** If both systems update simultaneously, last write wins
2. **Description overwrites:** If you manually edit a card description, sync might overwrite it
3. **One-directional status mapping:** Only DONE → QUALIFIED, not TODO → NEW
4. **No attachment sync:** Files/attachments don't transfer between systems
5. **Rate limiting:** No exponential backoff yet (relies on time.sleep)
6. **Single board only:** Can't sync multiple Trello boards to one Airtable base

### What I'd Add With More Time

- [ ] Web dashboard (FastAPI + React) to monitor sync status
- [ ] Webhook support for instant updates
- [ ] Conflict resolution strategy (timestamps + merge logic)
- [ ] Support for multiple boards/bases
- [ ] Unit tests (pytest) for core sync logic
- [ ] Docker containerization
- [ ] Proper logging with rotating file handlers
- [ ] Sync history/audit trail in SQLite
- [ ] Email notifications on sync failures

---

## Error Handling & Idempotency

### Idempotency Guarantees

**The system is idempotent**, meaning running sync multiple times produces the same result:

1. **Card creation:** Checks if Airtable ID exists in any card description before creating
2. **Status updates:** Only updates if current status ≠ desired status
3. **DONE list protection:** Won't move cards back from DONE (respects manual completion)

### Error Scenarios Handled

| Error | Handling |
|-------|----------|
| Invalid API credentials | Config validation at startup - fails fast with clear message |
| Network timeout | Logs error, continues to next cycle |
| Rate limit (429) | Logs error, continues (relies on sync interval to naturally back off) |
| Malformed data | Skips record, logs warning, continues with others |
| Missing fields | Uses default values (`'Unnamed Lead'`, empty string, etc.) |

### Logging Strategy

I kept it simple with print statements that show:
- ✓ Success actions (green checkmarks)
- ↻ Update actions (reload symbols)
- + Create actions (plus signs)
- ✗ Error actions (X marks)
- 🔒 Protection actions (lock symbols)

In production, I'd replace with:

import logging
logging.basicConfig(
level=logging.INFO,
format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
handlers=[
logging.FileHandler('sync.log'),
logging.StreamHandler()
]
)


---

## AI Usage Notes

### Tools Used

I used **ChatGPT (via Perplexity)** as a pair programming partner throughout this project.

### Where AI Helped

1. **API Documentation Summary**
   - Asked AI to explain Airtable and Trello REST API authentication
   - Used it to understand pagination in Airtable API

2. **Regex Pattern**
   - AI helped me write the regex for extracting Airtable IDs from descriptions
   - Pattern: `r'AIRTABLE_ID:\s*(rec[A-Za-z0-9]+)'`

3. **Error Handling Patterns**
   - Discussed try/except placement with AI
   - Asked about Python best practices for API error handling

4. **Code Structure**
   - Asked AI to review my module separation (clients vs services)
   - Got suggestions on where to put config validation

5. **Documentation**
   - Used AI to help format this README
   - Asked for markdown table formatting help

### What I Changed/Rejected

**Example 1: Sync Order**

AI initially suggested running `sync_trello_to_airtable()` first, then `sync_airtable_to_trello()`. I rejected this because:
- Created a race condition where cards in DONE list got moved back to TODO
- My solution: Added protection logic to skip cards already in DONE list

**Example 2: Error Handling**

AI suggested wrapping the entire sync in one try/except block. I changed it to:
- Separate try/except for each direction (Airtable→Trello, Trello→Airtable)
- Reason: One direction failing shouldn't block the other

**Example 3: Rate Limiting**

AI suggested using a third-party library for rate limiting. I rejected it because:
- Simple `time.sleep(0.5)` is sufficient for free tier limits
- No need to add dependencies for something this simple
- Assignment emphasizes using just `requests` library

### AI Chat Exports

*(If you saved chat transcripts, mention them here)*

I've included relevant AI chat snippets in `/ai-notes/` folder showing:
- Initial architecture discussion
- Debugging the "invalid key" Trello auth error
- Solving the DONE list sync conflict issue

---

## Dependencies

requests==2.31.0
python-dotenv==1.0.0


**Why so minimal?**
- Assignment specifically asked to use `requests` library (no fancy SDKs)
- `python-dotenv` for safe credential management
- Everything else is built from scratch to show understanding

---

## Testing

While I didn't write formal unit tests (time constraint), I manually tested:

**✅ Tested Scenarios:**
- [x] Initial sync creates cards for all leads
- [x] Initial sync skips LOST leads
- [x] Initial sync doesn't create duplicates on re-run
- [x] New lead in Airtable → Creates Trello card
- [x] Lead status change → Updates card name and list
- [x] Card moved to DONE → Updates Airtable to QUALIFIED
- [x] Card already QUALIFIED → Doesn't re-update (idempotent)
- [x] Card in DONE → Doesn't get moved back by Airtable sync
- [x] Invalid credentials → Fails with clear error message
- [x] Empty Airtable fields → Handles gracefully with defaults

**Future Testing:**
If I had more time, I'd add:
- `pytest` unit tests for regex extraction
- Mock API responses for client testing
- Integration tests with test Airtable/Trello accounts

---

## Deployment Considerations

This was built for local execution, but for production I'd recommend:

**Option 1: Docker + Cron**

FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "main.py"]


**Option 2: Heroku/Railway**
- Add `Procfile`: `worker: python main.py`
- Set environment variables in platform dashboard
- Free tier sufficient for this workload

**Option 3: AWS Lambda + EventBridge**
- Refactor to run as stateless function
- Trigger every minute via EventBridge schedule
- Most cost-effective for low-volume sync

---

## Contributing

This is a take-home assignment, so contributions aren't expected. However, if this were a real project, I'd welcome:

- Webhook implementation
- Additional SaaS integrations (HubSpot, Notion, etc.)
- Conflict resolution strategies
- Monitoring dashboard

---

## License

MIT License - Feel free to use this code for learning or building similar integrations.

---

## Contact

**Anurag Jha**  
Email: anuuragjha70@gmail.com 
GitHub: [@4nxrag](https://github.com/4nxrag)  
LinkedIn: [@4nxrag](https://linkedin.com/in/4nxrag)

---

## Acknowledgments

- Thanks to Airtable and Trello for providing free API access
- Assignment designed by DeepLogic AI Tech team
- Built with help from ChatGPT for documentation and debugging assistance

---

**Built with ❤️ and a lot of coffee ☕**
