"""
Database Initialization Script
Creates the PostgreSQL database and table if they don't exist
Compatible with PostgreSQL 18
"""
from data_manager import DataManager
import sys

if __name__ == '__main__':
    print("Initializing PostgreSQL database...")
    print("(Compatible with PostgreSQL 18)")
    print()
    
    try:
        dm = DataManager()
        print("✓ Database initialized successfully!")
        print(f"✓ Table 'job_applications' is ready")
        
        # Test connection
        df = dm.load_data()
        print(f"✓ Connection test successful. Found {len(df)} existing applications.")
        print()
        print("You can now run: python process_emails.py")
    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        print()
        print("Troubleshooting:")
        print("1. Check if PostgreSQL 18 is running:")
        print("   /Library/PostgreSQL/18/bin/pg_isready")
        print()
        print("2. Verify database credentials in .env file:")
        print("   DB_HOST=localhost")
        print("   DB_PORT=5432")
        print("   DB_NAME=job_applications")
        print("   DB_USER=postgres")
        print("   DB_PASSWORD=your_password")
        print()
        print("3. Test connection manually:")
        print("   /Library/PostgreSQL/18/bin/psql -U postgres -d postgres")
        print()
        print("4. If connection fails, check PostgreSQL logs:")
        print("   /Library/PostgreSQL/18/data/log/")
        sys.exit(1)

