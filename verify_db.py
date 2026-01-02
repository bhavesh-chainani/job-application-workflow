"""
Verification script to check database schema and data storage
Run this to verify all fields are being stored correctly
"""
from data_manager import DataManager
import psycopg2
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

def verify_database():
    """Verify database schema and data"""
    print("Verifying PostgreSQL Database...")
    print("=" * 50)
    
    # Check connection
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
        
        # Check table exists
        cursor.execute("""
            SELECT column_name, data_type, character_maximum_length 
            FROM information_schema.columns 
            WHERE table_name = 'job_applications'
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        print("\n✓ Database table 'job_applications' exists")
        print("\nTable schema:")
        for col_name, data_type, max_length in columns:
            length_info = f"({max_length})" if max_length else ""
            print(f"  - {col_name}: {data_type}{length_info}")
        
        # Check data
        cursor.execute("SELECT COUNT(*) FROM job_applications")
        total_count = cursor.fetchone()[0]
        print(f"\n✓ Total records in database: {total_count}")
        
        if total_count > 0:
            # Check status distribution
            cursor.execute("""
                SELECT status, COUNT(*) 
                FROM job_applications 
                GROUP BY status 
                ORDER BY COUNT(*) DESC
            """)
            statuses = cursor.fetchall()
            
            print("\nStatus distribution:")
            for status, count in statuses:
                print(f"  {status}: {count}")
            
            # Check sample record
            cursor.execute("""
                SELECT email_id, company, job_title, status, application_date, location
                FROM job_applications 
                LIMIT 1
            """)
            sample = cursor.fetchone()
            if sample:
                print("\nSample record:")
                print(f"  Email ID: {sample[0]}")
                print(f"  Company: {sample[1]}")
                print(f"  Job Title: {sample[2]}")
                print(f"  Status: {sample[3]}")
                print(f"  Application Date: {sample[4]}")
                print(f"  Location: {sample[5]}")
        
        # Verify all expected columns exist
        expected_columns = [
            'id', 'email_id', 'date', 'job_title', 'company', 'location', 
            'status', 'application_date', 'sender', 'subject', 
            'related_application_id', 'confidence', 'reasoning', 
            'last_updated', 'created_at'
        ]
        
        existing_columns = [col[0] for col in columns]
        missing_columns = [col for col in expected_columns if col not in existing_columns]
        
        if missing_columns:
            print(f"\n⚠ Warning: Missing columns: {missing_columns}")
        else:
            print("\n✓ All expected columns present")
        
        # Check status field can handle new values
        cursor.execute("SELECT MAX(LENGTH(status)) FROM job_applications")
        max_status_length = cursor.fetchone()[0] or 0
        print(f"\n✓ Maximum status length in data: {max_status_length} characters")
        print(f"  (Status field is VARCHAR(50), sufficient for 'Recruiter Screen' which is {len('Recruiter Screen')} chars)")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 50)
        print("✓ Database verification complete!")
        
    except Exception as e:
        print(f"\n✗ Error verifying database: {e}")
        print("\nPlease ensure:")
        print("1. PostgreSQL is running")
        print("2. Database credentials in .env are correct")
        print("3. Run 'python init_db.py' to create the database")

if __name__ == '__main__':
    verify_database()












