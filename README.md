# Job Application Workflow Tracker

A comprehensive system for tracking and visualizing job applications from Gmail. Automatically extracts application details, stores them in PostgreSQL, and provides an interactive dashboard with funnel visualization.

## 🚀 Features

- **Automated Email Processing**: Connects to Gmail API to read and parse job application emails
- **Smart Parsing**: Uses LLM to extract job title, company, location, and status from emails
- **PostgreSQL Storage**: Robust database storage with deduplication and status tracking
- **Modern Dashboard**: React + FastAPI dashboard with funnel visualization
- **Real-time Updates**: Filter, edit, and track applications in real-time
- **Automated Processing**: Optional cron-based automation for daily email processing

## 📋 Prerequisites

- Python 3.8+
- Node.js 18+ and npm
- PostgreSQL database
- Gmail API credentials (see [Setup Guide](QUICKSTART.md))
- OpenAI API key (for LLM parsing)

## 🏗️ Project Structure

```
job-app-workflow/
├── backend/              # FastAPI backend server
│   └── main.py          # REST API endpoints
├── frontend/            # React frontend application
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── App.tsx     # Main app component
│   │   └── api.ts      # API client
│   └── package.json
├── scripts/             # Utility scripts
│   ├── add_sample_data.py
│   └── delete_sample_data.py
├── config.py           # Configuration
├── data_manager.py     # Database operations
├── email_parser.py     # Email parsing logic
├── llm_parser.py       # LLM-based extraction
├── process_emails.py   # Email processing
├── gmail_auth.py       # Gmail authentication
├── automate.py         # Automation script
├── init_db.py          # Database initialization
├── start.py            # One-command startup script
└── requirements.txt    # Python dependencies
```

## ⚡ Quick Start

### 1. Clone and Install

```bash
# Clone the repository
git clone <your-repo-url>
cd job-app-workflow

# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### 2. Configure Environment

Create a `.env` file in the project root:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=job_applications
DB_USER=your_username
DB_PASSWORD=your_password

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Gmail API (credentials.json should be in project root)
```

### 3. Set Up Gmail API

See [QUICKSTART.md](QUICKSTART.md) for detailed Gmail API setup instructions.

### 4. Initialize Database

```bash
python init_db.py
```

### 5. Authenticate Gmail

```bash
python gmail_auth.py
```

### 6. Process Emails (Optional)

```bash
python process_emails.py
```

### 7. Launch Dashboard

```bash
python start.py
```

The dashboard will open automatically at `http://localhost:3000`

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Detailed setup guide including Gmail API configuration
- **[DASHBOARD_SETUP.md](DASHBOARD_SETUP.md)** - Dashboard setup and features
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture and data flow
- **[SECURITY_CHECKLIST.md](SECURITY_CHECKLIST.md)** - Security best practices

## 🎯 Usage

### Processing Emails

```bash
# Process emails manually
python process_emails.py

# Set up automated processing (runs twice daily)
bash setup_automation.sh
```

### Dashboard Features

- **Funnel Visualization**: See your application pipeline flow
- **Metrics**: Track total applications, companies, locations
- **Filtering**: Filter by status or company
- **Inline Editing**: Update status and location directly in the table

### Sample Data

```bash
# Add sample data for testing
python scripts/add_sample_data.py

# Remove sample data
python scripts/delete_sample_data.py
```

**Note**: Sample data scripts are located in the `scripts/` folder.

## 🔧 Configuration

Edit `config.py` to customize:

- Email search query and labels
- Status definitions
- Processing options (mark as read, process only unread)

## 🔄 Automation

Set up automated email processing:

```bash
bash setup_automation.sh
```

This creates cron jobs to run `automate.py` twice daily (12pm and 12am).

## 🛠️ Development

### Backend API

```bash
python backend/main.py
# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### Frontend Development

```bash
cd frontend
npm run dev
# Frontend at http://localhost:3000
```

### Building for Production

```bash
cd frontend
npm run build
# Built files in frontend/dist/
```

## 📊 Status Pipeline

Applications progress through these stages:

1. **Applied** - Initial application submitted
2. **Recruiter Screen** - Passed initial screening
3. **Interview** - Interview stage
4. **Outcomes**:
   - **Offer** - Received offer
   - **Rejected** - Application rejected
   - **Ghosted** - No response
   - **Dropped** - Withdrew application

## 🔒 Security

- Never commit `credentials.json`, `token.json`, or `.env` files
- All sensitive data is stored in environment variables
- See [SECURITY_CHECKLIST.md](SECURITY_CHECKLIST.md) for details

## 📝 License

This project is for personal use. Modify as needed for your requirements.

## 🤝 Contributing

This is a personal project, but suggestions and improvements are welcome!

## 📧 Support

For issues or questions:
- Check the documentation files
- Review API docs at `http://localhost:8000/docs`
- Check browser console for frontend errors

---

**Built by Bhavesh Chainani** - Job Application Pipeline Management System
