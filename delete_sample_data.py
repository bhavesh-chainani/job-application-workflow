"""
Delete Sample Data
Removes all sample job applications from the database
Run this when you're done testing and want to remove the proxy data
"""
from data_manager import DataManager
import psycopg2
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

def delete_sample_data():
    """Delete all sample applications (those with email_id starting with 'sample_')"""
    print("Deleting sample job application data...")
    print("=" * 50)
    
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
        
        # Count sample records before deletion
        cursor.execute("SELECT COUNT(*) FROM job_applications WHERE email_id LIKE 'sample_%'")
        count_before = cursor.fetchone()[0]
        
        if count_before == 0:
            print("ℹ️  No sample data found to delete.")
            cursor.close()
            conn.close()
            return
        
        # Confirm deletion
        print(f"Found {count_before} sample application(s) to delete.")
        print("\n⚠️  This will permanently delete all sample data!")
        
        # Delete sample records
        cursor.execute("DELETE FROM job_applications WHERE email_id LIKE 'sample_%'")
        deleted_count = cursor.rowcount
        conn.commit()
        
        print(f"\n✓ Successfully deleted {deleted_count} sample application(s)")
        
        # Show remaining records
        cursor.execute("SELECT COUNT(*) FROM job_applications")
        remaining_count = cursor.fetchone()[0]
        print(f"  Remaining applications in database: {remaining_count}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 50)
        print("✓ Sample data deletion complete!")
        
    except Exception as e:
        print(f"\n✗ Error deleting sample data: {e}")
        if conn:
            conn.rollback()

if __name__ == '__main__':
    delete_sample_data()


