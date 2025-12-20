"""
Migration script to update existing status values to new pipeline stages
Run this once to migrate existing data to the new status system
"""
from data_manager import DataManager
import psycopg2
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

def migrate_statuses():
    """Migrate old status values to new pipeline stages"""
    conn_params = {
        'host': DB_HOST,
        'port': DB_PORT,
        'database': DB_NAME,
        'user': DB_USER,
        'password': DB_PASSWORD
    }
    
    try:
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        
        # Status mapping: old -> new
        status_mapping = {
            'In Progress': 'Recruiter Screen',
            'Withdrawn': 'Dropped',
            # Keep these as-is: Applied, Rejected, Interview, Recruiter Screen, Ghosted, Dropped, Offer
        }
        
        print("Migrating status values...")
        
        for old_status, new_status in status_mapping.items():
            cursor.execute(
                "UPDATE job_applications SET status = %s WHERE status = %s",
                (new_status, old_status)
            )
            count = cursor.rowcount
            if count > 0:
                print(f"  ✓ Updated {count} records: '{old_status}' → '{new_status}'")
        
        conn.commit()
        print("\n✓ Migration complete!")
        
        # Show current status distribution
        cursor.execute("SELECT status, COUNT(*) FROM job_applications GROUP BY status ORDER BY COUNT(*) DESC")
        results = cursor.fetchall()
        
        if results:
            print("\nCurrent status distribution:")
            for status, count in results:
                print(f"  {status}: {count}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"✗ Error during migration: {e}")
        if conn:
            conn.rollback()

if __name__ == '__main__':
    print("Status Migration Script")
    print("=" * 50)
    migrate_statuses()


