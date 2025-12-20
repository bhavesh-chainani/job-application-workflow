# Modern Dashboard Setup Guide

This guide will help you set up the new React + FastAPI dashboard for your job application workflow.

## Tech Stack

- **Backend**: FastAPI (Python) - Modern, fast, async API
- **Frontend**: React + TypeScript - Component-based UI
- **Visualization**: Recharts - Beautiful funnel charts
- **Styling**: Tailwind CSS - Modern, responsive design
- **Database**: PostgreSQL (existing)

## Prerequisites

- Python 3.8+
- Node.js 18+ and npm
- PostgreSQL database (already configured)

## Setup Instructions

### 1. Install Backend Dependencies

```bash
# Activate your virtual environment if not already active
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install new dependencies
pip install -r requirements.txt
```

### 2. Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

### 3. Start the Backend Server

```bash
# From project root
python backend/main.py
```

Or using uvicorn directly:
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`
API documentation at `http://localhost:8000/docs`

### 4. Start the Frontend Development Server

```bash
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:3000`

### 5. Access the Dashboard

Open your browser and navigate to `http://localhost:3000`

## Features

### 📊 Funnel Visualization
- Clear visual representation of your application pipeline
- Shows progression: Applied → Recruiter Screen → Interview
- Displays outcomes: Rejected, Ghosted, Dropped, Offer

### 📈 Key Metrics
- Total Applications
- Unique Companies
- Unique Locations
- In Progress (Recruiter Screen + Interview)

### 🔍 Filtering
- Filter by status
- Filter by company
- Real-time updates

### ✏️ Editable Table
- Update application status inline
- Update location information
- Save changes instantly

## API Endpoints

- `GET /api/applications` - Get all applications (with optional filters)
- `GET /api/statistics` - Get statistics
- `GET /api/funnel` - Get funnel data for visualization
- `PUT /api/applications/status` - Update application status
- `PUT /api/applications/location` - Update application location

## Development

### Backend Development

The backend uses FastAPI with automatic API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Frontend Development

The frontend uses Vite for fast development:
- Hot module replacement (HMR)
- TypeScript support
- Tailwind CSS for styling

### Building for Production

```bash
# Build frontend
cd frontend
npm run build

# The built files will be in frontend/dist/
```

## Troubleshooting

### Backend won't start
- Make sure PostgreSQL is running
- Check your `.env` file has correct database credentials
- Verify all Python dependencies are installed

### Frontend won't start
- Make sure Node.js 18+ is installed
- Run `npm install` in the frontend directory
- Check that port 3000 is available

### API connection errors
- Ensure backend is running on port 8000
- Check CORS settings in `backend/main.py` if accessing from different origin
- Verify proxy settings in `frontend/vite.config.ts`

## Notes

The new React dashboard uses the same PostgreSQL database as the previous system, so all your existing data is automatically available.

## Next Steps

1. Customize colors and styling in `frontend/tailwind.config.js`
2. Add more visualizations as needed
3. Deploy to production (see deployment guide)

## Support

For issues or questions, check:
- API docs at `http://localhost:8000/docs`
- Browser console for frontend errors
- Backend logs in terminal

