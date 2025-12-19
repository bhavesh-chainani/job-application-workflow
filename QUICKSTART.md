# Quick Start Guide

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Set Up Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select an existing one)
3. Enable the **Gmail API**:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"
4. Configure OAuth Consent Screen:
   - Navigate to "APIs & Services" > "OAuth consent screen"
   - Choose "External" as user type (unless you have a Google Workspace account)
   - Fill in the required fields:
     - App name: `job-app-workflow` (or any name you prefer)
     - User support email: Your email address
     - Developer contact information: Your email address
   - Click "Save and Continue" through the scopes and test users screens
   - **Important**: On the "Test users" screen, click "Add Users" and add your Gmail email address
     - This is required because the app is in testing mode
     - Only added test users can authenticate
5. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop app" as application type
   - Download the JSON file
5. Save the downloaded file as `credentials.json` in this project directory

## Step 3: Set Up PostgreSQL Database

The system uses PostgreSQL to store job application data. Set up your database:

1. **Install PostgreSQL** (if not already installed):
   - macOS: Download from [postgresql.org](https://www.postgresql.org/download/macosx/) or use Homebrew: `brew install postgresql@18`
   - Linux: `sudo apt-get install postgresql` (Ubuntu/Debian) or `sudo yum install postgresql` (RHEL/CentOS)
   - Windows: Download installer from [postgresql.org](https://www.postgresql.org/download/windows/)

2. **Start PostgreSQL service**:
   ```bash
   # macOS (PostgreSQL.app or command line)
   # If installed via PostgreSQL.app, it should start automatically
   # Or via command line:
   /Library/PostgreSQL/18/bin/pg_ctl -D /Library/PostgreSQL/18/data start
   
   # macOS (Homebrew)
   brew services start postgresql@18
   
   # Linux
   sudo systemctl start postgresql
   ```
   
   **Note for macOS PostgreSQL 18**: If you installed via the official installer, PostgreSQL may already be running. Check with:
   ```bash
   /Library/PostgreSQL/18/bin/pg_isready
   ```

3. **Add database credentials to `.env` file**:
   Create or update `.env` file in the project root:
   ```
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=job_applications
   DB_USER=postgres
   DB_PASSWORD=your_postgres_password
   ```
   
   **Default PostgreSQL 18 setup:**
   - Default user is usually `postgres`
   - Default port is `5432`
   - Password is set during installation
   - If you forgot your password, you can reset it or check PostgreSQL configuration

4. **Initialize the database**:
   ```bash
   python init_db.py
   ```
   This will create the database and table automatically.

## Step 4: Set Up OpenAI API Key

The system uses OpenAI's LLM to intelligently extract job application information. Set your API key:

Add to your `.env` file:
```
OPENAI_API_KEY=your-api-key-here
```

**Get your API key:**
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign in or create an account
3. Create a new API key
4. Copy and use it above

**Note:** The system uses `gpt-4o-mini` by default for cost efficiency. You can change this in `config.py` to `gpt-4` for better accuracy.

## Step 5: Authenticate

Run the authentication script:

```bash
python gmail_auth.py
```

This will:
- Open a browser window
- Ask you to sign in with your Google account
- Request permission to read your Gmail
- Save the authentication token to `token.json`

## Step 6: Configure Email Filtering (Optional)

Edit `config.py` to customize:

- **EMAIL_FOLDER**: Change from `'INBOX'` to a specific label like `'Job Applications'` if you use Gmail labels
- **EMAIL_SEARCH_QUERY**: Modify the search query (default: `'is:unread'`)
  - Examples:
    - `'label:job-applications'` - Only emails with this label
    - `'from:noreply@linkedin.com'` - Only emails from LinkedIn
    - `'subject:"application"'` - Only emails with "application" in subject

## Step 7: Process Emails

Run the email processor:

```bash
python process_emails.py
```

This will:
- Read emails from Gmail based on your configuration
- Extract job application information using LLM
- Save data to PostgreSQL database
- Mark emails as read (if configured)

## Step 8: View Dashboard

Launch the interactive dashboard:

```bash
streamlit run dashboard.py
```

The dashboard will open in your browser showing:
- Sankey diagram visualization
- Status breakdown charts
- Application details table
- Filters and statistics

## Step 9: Set Up Automation (Optional)

### Option A: Using Cron (macOS/Linux)

Run the setup script:

```bash
bash setup_automation.sh
```

Or manually add to crontab:

```bash
crontab -e
```

Add these lines (runs twice daily at 12pm and 12am):

```
0 12 * * * cd /path/to/job_app_workflow && python3 automate.py >> automation.log 2>&1
0 0 * * * cd /path/to/job_app_workflow && python3 automate.py >> automation.log 2>&1
```

Or use the setup script which will configure this automatically:

```bash
bash setup_automation.sh
```

### Option B: Using Task Scheduler (Windows)

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., daily at 9 AM)
4. Action: Start a program
5. Program: `python.exe`
6. Arguments: `C:\path\to\job_app_workflow\automate.py`
7. Start in: `C:\path\to\job_app_workflow`

## Tips

- **Better Email Organization**: Create a Gmail label called "Job Applications" and filter emails there
- **Manual Status Updates**: Use the dashboard filters or update directly in PostgreSQL
- **Data Backup**: The data is stored in PostgreSQL - use `pg_dump` to backup
- **Privacy**: Only emails matching your search query are processed

## Troubleshooting

**"credentials.json not found"**
- Make sure you downloaded the OAuth credentials from Google Cloud Console
- Save it as `credentials.json` in the project root

**"Authentication failed" or "Error 403: access_denied"**
- Make sure you've added your email address as a test user in the OAuth consent screen:
  - Go to "APIs & Services" > "OAuth consent screen" > "Test users"
  - Click "Add Users" and add your Gmail email address
- Delete `token.json` and run `gmail_auth.py` again
- Make sure Gmail API is enabled in your Google Cloud project
- Verify OAuth consent screen is configured (see Step 2)

**"OPENAI_API_KEY not set"**
- Set your OpenAI API key as an environment variable: `export OPENAI_API_KEY='your-key'`
- Or update `config.py` with your API key
- Make sure you have credits in your OpenAI account

**LLM extraction not working well**
- Check that your OpenAI API key is valid and has credits
- Try changing `OPENAI_MODEL` in `config.py` from `gpt-4o-mini` to `gpt-4` for better accuracy
- Check the console output for LLM reasoning to understand extraction decisions

**"No emails found"**
- Check your `EMAIL_SEARCH_QUERY` in `config.py`
- Try a broader query like `'is:unread'` or `'in:inbox'`

**Dashboard shows no data**
- Run `process_emails.py` first to populate the database
- Verify PostgreSQL connection: `python init_db.py`
- Check database: `psql -U your_username -d job_applications -c "SELECT COUNT(*) FROM job_applications;"`

**PostgreSQL connection errors**
- Ensure PostgreSQL is running: `pg_isready` or `brew services list` (macOS)
- Verify credentials in `.env` file match your PostgreSQL setup
- Check if database exists: `psql -U your_username -l`
- Run `python init_db.py` to create database and table

