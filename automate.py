"""
Automation Script
Run this script periodically (via cron, scheduled task, or systemd timer)
to automatically process new emails

Note: This script runs independently - Cursor/IDE doesn't need to be open.
Cron jobs run as background system processes.
"""
import sys
import os

# Ensure we're in the script directory (important for cron jobs)
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv(override=True)

from process_emails import process_emails
from datetime import datetime

def main():
    """Main automation function"""
    print(f"{'='*60}")
    print(f"Job Application Workflow - Automated Processing")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    try:
        process_emails()
        print(f"\n✓ Automation completed successfully at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return 0
    except Exception as e:
        print(f"\n✗ Error during automation: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)

