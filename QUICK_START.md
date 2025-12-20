# Quick Start - One Command Dashboard

Start both backend and frontend servers with a single command!

## Option 1: Python Script (Recommended)

```bash
python start.py
```

This will:
- ✅ Check all dependencies
- ✅ Install frontend dependencies if needed
- ✅ Start backend server (port 8000)
- ✅ Start frontend server (port 3000)
- ✅ Open browser automatically
- ✅ Handle cleanup on exit

## Option 2: Shell Script

```bash
chmod +x start.sh
./start.sh
```

## Option 3: Manual Start (if scripts don't work)

**Terminal 1 - Backend:**
```bash
python backend/main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Then open http://localhost:3000 in your browser.

## First Time Setup

If this is your first time running:

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install frontend dependencies:**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

3. **Run the startup script:**
   ```bash
   python start.py
   ```

That's it! The dashboard will open automatically in your browser.

## Troubleshooting

- **Backend won't start**: Make sure PostgreSQL is running and `.env` file is configured
- **Frontend won't start**: Make sure Node.js 18+ is installed (`node --version`)
- **Port already in use**: Stop any existing servers on ports 8000 or 3000

## Access Points

- **Dashboard**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

