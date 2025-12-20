# Architecture Overview

## System Components

### 1. **Gmail Authentication** (`gmail_auth.py`)
- Handles OAuth 2.0 authentication with Gmail API
- Manages token storage and refresh
- Returns authenticated Gmail service object

### 2. **Email Parser** (`email_parser.py`)
- Extracts job application information from emails:
  - **Job Title**: Parsed from subject/body using regex patterns
  - **Company**: Extracted from sender email domain or email content
  - **Location**: Found in email body using location patterns
  - **Status**: Inferred from keywords (Applied, In Progress, Rejected, Withdrawn)
- Handles both plain text and HTML emails
- Recursively processes multipart email structures

### 3. **Data Manager** (`data_manager.py`)
- Manages job application data storage
- Uses CSV for primary storage, Excel for export
- Provides CRUD operations:
  - Add/update applications
  - Update status
  - Get statistics
- Prevents duplicates using email_id as unique identifier

### 4. **Email Processor** (`process_emails.py`)
- Main orchestration script
- Fetches emails from Gmail based on search query
- Processes each email through the parser
- Updates database with new/updated applications
- Optionally marks emails as read

### 5. **Dashboard** (React + FastAPI)
- **Backend** (`backend/main.py`): FastAPI REST API server
  - Provides endpoints for applications, statistics, and funnel data
  - Handles status and location updates
  - Auto-generated API documentation at `/docs`
- **Frontend** (`frontend/`): React + TypeScript web application
  - **Funnel Visualization**: Horizontal bar charts showing application pipeline flow
  - **Metrics Dashboard**: Key statistics (total apps, companies, locations, in-progress)
  - **Application Table**: Filterable, editable table with inline status/location updates
  - **Filters**: Filter by status and company
  - Modern UI with Tailwind CSS

### 6. **Automation** (`automate.py`)
- Wrapper script for scheduled execution
- Includes error handling and logging
- Designed for cron/scheduled task integration

### 7. **Configuration** (`config.py`)
- Centralized configuration
- Gmail API settings
- Email filtering options
- Data file paths
- Status definitions

## Data Flow

```
Gmail API → Email Processor → Email Parser → Data Manager → PostgreSQL
                                                      ↓
                                              FastAPI Backend → React Frontend
```

## Workflow

1. **Initial Setup**:
   - User sets up Gmail API credentials
   - Runs `gmail_auth.py` to authenticate
   - Configures email filters in `config.py`

2. **Email Processing**:
   - `process_emails.py` fetches emails from Gmail
   - Each email is parsed for job application data
   - Extracted data is stored/updated in CSV/Excel

3. **Visualization**:
   - User launches dashboard with `python start.py`
   - Backend API serves data from PostgreSQL
   - React frontend displays interactive visualizations
   - User can filter, explore, and update applications in real-time

4. **Automation**:
   - `automate.py` runs periodically (via cron/scheduler)
   - Automatically processes new emails
   - Updates database without user intervention

## Data Schema

Each job application record contains:
- `email_id`: Unique Gmail message ID
- `date`: Email date
- `job_title`: Extracted job title
- `company`: Company name
- `location`: Job location
- `status`: Application status (Applied, In Progress, Withdrawn, Rejected)
- `sender`: Email sender
- `subject`: Email subject
- `last_updated`: Timestamp of last update

## Sankey Diagram Structure

The Sankey diagram shows a three-stage flow:

1. **Source Nodes**: Companies (where applications were sent)
2. **Intermediate Nodes**: Locations (where jobs are located)
3. **Target Nodes**: Statuses (current application status)

Flow width represents the number of applications flowing through each path.

## Extensibility

The system is designed to be easily extended:

- **Add new fields**: Modify `email_parser.py` to extract additional data
- **Custom statuses**: Update `STATUSES` in `config.py`
- **New visualizations**: Add components to `frontend/src/components/`
- **Different email sources**: Extend `process_emails.py` to support other APIs
- **Database backend**: Replace CSV storage in `data_manager.py` with SQL database

## Security Considerations

- Gmail credentials (`credentials.json`, `token.json`) are excluded from version control
- OAuth 2.0 provides secure, token-based authentication
- Read-only Gmail API access (no ability to send/delete emails)
- Local data storage (no cloud dependencies)

