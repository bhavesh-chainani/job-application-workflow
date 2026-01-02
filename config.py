"""
Configuration file for Job Application Workflow Tracker
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file (override=True ensures .env takes precedence)
load_dotenv(override=True)

# Gmail API Configuration
GMAIL_CREDENTIALS_FILE = 'credentials.json'
GMAIL_TOKEN_FILE = 'token.json'
GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.modify']  # Allows reading and modifying emails (marking as read)

# Email Configuration
EMAIL_FOLDER = 'Job Applications'  # Change to specific label like 'Job Applications' if you use labels
EMAIL_SEARCH_QUERY = 'label:"Job Applications"'  # Query emails from Job Applications label

# PostgreSQL Database Configuration
# Loads from .env file - add these to your .env:
# DB_HOST=localhost
# DB_PORT=5432
# DB_NAME=job_applications
# DB_USER=your_username
# DB_PASSWORD=your_password
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'job_applications')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')

# Legacy CSV/Excel (kept for migration purposes)
DATA_FILE = 'job_applications.csv'
EXCEL_FILE = 'job_applications.xlsx'

# Status Options - Application Pipeline Stages
STATUSES = [
    'Applied',              # Initial application submitted
    'Recruiter Screen',    # Passed initial screening
    'Interview',           # Interview stage
    'Rejected',           # Final outcome: rejected
    'Ghosted',            # Final outcome: no response
    'Dropped',            # Final outcome: withdrew application
    'Offer'               # Final outcome: received offer
]

# Email Processing
PROCESS_ONLY_UNREAD = False # Set to False to process all emails matching query
MARK_AS_READ = True  # Mark processed emails as read

# Gmail API Timeout Configuration (in seconds)
GMAIL_API_TIMEOUT = 30  # Timeout for Gmail API requests
GMAIL_API_MAX_RETRIES = 3  # Maximum number of retry attempts

# OpenAI Configuration
# ONLY reads from .env file (override=True ensures .env file takes precedence over system env vars)
# Make sure your .env file contains: OPENAI_API_KEY=your-key-here
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')  # Reads from .env file only (due to override=True above)
OPENAI_MODEL = 'gpt-4o-mini'  # Using gpt-4o-mini for cost efficiency, change to 'gpt-4' for better accuracy

# Verify .env file is being read
if not OPENAI_API_KEY:
    import warnings
    warnings.warn("OPENAI_API_KEY not found in .env file. Please create a .env file with: OPENAI_API_KEY=your-key-here")

