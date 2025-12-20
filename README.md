# Job Application Workflow Tracker

An automated system that tracks job applications from Gmail and visualizes them in a Sankey diagram dashboard.

## Features

- **Automated Email Reading**: Connects to Gmail API to read emails from inbox or specific folder
- **Smart Parsing**: Extracts job title, company, location, and status from emails
- **Data Storage**: Stores application data in CSV/Excel format
- **Interactive Dashboard**: Beautiful Sankey diagram visualization showing application flow
- **Status Tracking**: Tracks statuses: Applied, In Progress, Withdrawn, Rejected

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Gmail API Setup**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Gmail API
   - Create OAuth 2.0 credentials (Desktop app)
   - Download credentials JSON file
   - Save it as `credentials.json` in the project root

3. **First-time Authentication**:
   ```bash
   python gmail_auth.py
   ```
   This will open a browser window for authentication and save the token.

4. **Run the email processor**:
   ```bash
   python process_emails.py
   ```
   This will read emails and update the database.

5. **Launch the dashboard**:
   ```bash
   python start.py
   ```
   This starts both backend and frontend automatically and opens your browser.

## Configuration

Edit `config.py` to customize:
- Email folder/label to monitor (default: "INBOX")
- Email search query
- Data file location

## Automation

Set up a cron job or scheduled task to run `automate.py` periodically:
```bash
# Run twice daily (12pm and 12am)
0 12 * * * cd /path/to/project && python3 automate.py >> automation.log 2>&1
0 0 * * * cd /path/to/project && python3 automate.py >> automation.log 2>&1
```

Or use the automated setup script:
```bash
bash setup_automation.sh
```

