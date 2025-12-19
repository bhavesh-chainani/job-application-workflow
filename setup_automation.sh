#!/bin/bash

# Setup script for automating email processing
# This creates a cron job to run the automation script periodically

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Detect Python path (prefer venv if it exists)
if [ -f "$SCRIPT_DIR/venv/bin/python3" ]; then
    PYTHON_PATH="$SCRIPT_DIR/venv/bin/python3"
    echo "Using virtual environment Python: $PYTHON_PATH"
elif [ -f "$SCRIPT_DIR/venv/bin/python" ]; then
    PYTHON_PATH="$SCRIPT_DIR/venv/bin/python"
    echo "Using virtual environment Python: $PYTHON_PATH"
else
    PYTHON_PATH=$(which python3)
    echo "Using system Python: $PYTHON_PATH"
fi

echo "Setting up automation for Job Application Workflow..."
echo "Script directory: $SCRIPT_DIR"
echo "Python path: $PYTHON_PATH"

# Create cron jobs (runs twice daily: 12pm and 12am)
# Note: Cron jobs run independently - Cursor/IDE doesn't need to be open
CRON_JOB_NOON="0 12 * * * cd $SCRIPT_DIR && $PYTHON_PATH automate.py >> $SCRIPT_DIR/automation.log 2>&1"
CRON_JOB_MIDNIGHT="0 0 * * * cd $SCRIPT_DIR && $PYTHON_PATH automate.py >> $SCRIPT_DIR/automation.log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "automate.py"; then
    echo "Cron job(s) already exist. Removing old entries..."
    crontab -l 2>/dev/null | grep -v "automate.py" | crontab -
fi

# Add new cron jobs
(crontab -l 2>/dev/null; echo "$CRON_JOB_NOON"; echo "$CRON_JOB_MIDNIGHT") | crontab -

echo "✓ Cron jobs added successfully!"
echo ""
echo "The automation will run twice daily:"
echo "  - 12:00 PM (noon)"
echo "  - 12:00 AM (midnight)"
echo ""
echo "⚠️  IMPORTANT NOTES:"
echo "  - Cron jobs run independently - Cursor/IDE doesn't need to be open"
echo "  - Your computer must be on and logged in for cron to run"
echo "  - The script will automatically load your .env file for API keys"
echo ""
echo "Useful commands:"
echo "  - View cron jobs: crontab -l"
echo "  - Remove automation: crontab -e (then delete the lines)"
echo "  - View logs: tail -f $SCRIPT_DIR/automation.log"
echo "  - Test manually: cd $SCRIPT_DIR && $PYTHON_PATH automate.py"

