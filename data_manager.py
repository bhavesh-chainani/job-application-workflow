"""
Data Manager Module
Handles storage and retrieval of job application data using PostgreSQL
"""
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import sql
from sqlalchemy import create_engine
from datetime import datetime
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

# Status hierarchy: higher number = more advanced status
STATUS_HIERARCHY = {
    'Applied': 0,
    'Recruiter Screen': 1,
    'Interview': 2,
    'Rejected': 3,  # Final status
    'Ghosted': 3,  # Final status
    'Dropped': 3,  # Final status
    'Offer': 4,  # Final status (highest)
}

def get_status_priority(status):
    """Get priority number for status (higher = more advanced)"""
    return STATUS_HIERARCHY.get(status, 0)

def should_update_status(current_status, new_status):
    """
    Determine if status should be updated.
    Rules:
    - Can always move forward (Applied -> Interview -> Offer)
    - Can move to final status from any stage (Applied -> Rejected)
    - Cannot move backward from final status (Rejected -> Applied)
    - Can move between final statuses only if new one is higher priority (Rejected -> Offer)
    """
    current_priority = get_status_priority(current_status)
    new_priority = get_status_priority(new_status)
    
    # If new status is higher priority, allow update
    if new_priority > current_priority:
        return True
    
    # If both are final statuses (priority 3), only allow if new one is higher
    if current_priority >= 3 and new_priority >= 3:
        return new_priority > current_priority
    
    # If current is final status and new is not, don't allow backward movement
    if current_priority >= 3 and new_priority < 3:
        return False
    
    # Allow forward movement within non-final statuses
    if current_priority < 3 and new_priority >= current_priority:
        return True
    
    return False


class DataManager:
    def __init__(self):
        self.conn_params = {
            'host': DB_HOST,
            'port': DB_PORT,
            'database': DB_NAME,
            'user': DB_USER,
            'password': DB_PASSWORD
        }
        self._ensure_database_exists()
        self._ensure_table_exists()
    
    def _get_connection(self):
        """Get database connection"""
        try:
            return psycopg2.connect(**self.conn_params)
        except psycopg2.Error as e:
            print(f"Error connecting to PostgreSQL: {e}")
            raise
    
    def _ensure_database_exists(self):
        """Create database if it doesn't exist"""
        # Connect to postgres database to create our database
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                database='postgres',  # Connect to default postgres database
                user=DB_USER,
                password=DB_PASSWORD
            )
            conn.autocommit = True
            cursor = conn.cursor()
            
            # Check if database exists
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (DB_NAME,)
            )
            exists = cursor.fetchone()
            
            if not exists:
                cursor.execute(sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(DB_NAME)
                ))
                print(f"✓ Created database: {DB_NAME}")
            
            cursor.close()
            conn.close()
        except psycopg2.Error as e:
            # If we can't create database, assume it exists or will be created manually
            print(f"Note: Could not create database automatically: {e}")
            print(f"Please ensure database '{DB_NAME}' exists or create it manually.")
    
    def _ensure_table_exists(self):
        """Create table if it doesn't exist"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        create_table_query = """
        CREATE TABLE IF NOT EXISTS job_applications (
            id SERIAL PRIMARY KEY,
            email_id VARCHAR(255) UNIQUE NOT NULL,
            date TIMESTAMP,
            job_title VARCHAR(500),
            company VARCHAR(255),
            location VARCHAR(255),
            status VARCHAR(50) DEFAULT 'Applied',
            -- Status can be: Applied, Recruiter Screen, Interview, Rejected, Ghosted, Dropped, Offer
            application_date DATE,
            sender VARCHAR(500),
            subject TEXT,
            related_application_id VARCHAR(255),
            confidence VARCHAR(20),
            reasoning TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS processed_emails (
            email_id VARCHAR(255) PRIMARY KEY,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            application_id INTEGER REFERENCES job_applications(id) ON DELETE SET NULL
        );
        
        CREATE INDEX IF NOT EXISTS idx_email_id ON job_applications(email_id);
        CREATE INDEX IF NOT EXISTS idx_company ON job_applications(company);
        CREATE INDEX IF NOT EXISTS idx_status ON job_applications(status);
        CREATE INDEX IF NOT EXISTS idx_related_app ON job_applications(related_application_id);
        CREATE INDEX IF NOT EXISTS idx_company_job ON job_applications(company, job_title);
        CREATE INDEX IF NOT EXISTS idx_processed_email ON processed_emails(email_id);
        """
        
        try:
            cursor.execute(create_table_query)
            conn.commit()
        except psycopg2.Error as e:
            print(f"Error creating table: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
    
    def is_email_processed(self, email_id):
        """Check if an email has already been processed"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT 1 FROM processed_emails WHERE email_id = %s", (email_id,))
            return cursor.fetchone() is not None
        except psycopg2.Error as e:
            print(f"Error checking processed email: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    
    def mark_email_processed(self, email_id, application_id=None):
        """Mark an email as processed"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """INSERT INTO processed_emails (email_id, application_id) 
                   VALUES (%s, %s) 
                   ON CONFLICT (email_id) DO UPDATE SET processed_at = CURRENT_TIMESTAMP""",
                (email_id, application_id)
            )
            conn.commit()
        except psycopg2.Error as e:
            print(f"Error marking email as processed: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
    
    def load_data(self):
        """Load all applications from database as DataFrame"""
        try:
            query = """
            SELECT 
                email_id, date, job_title, company, location, status,
                application_date, sender, subject, related_application_id,
                confidence, reasoning, last_updated
            FROM job_applications
            ORDER BY date DESC
            """
            # Use SQLAlchemy connection to avoid pandas warning and ensure proper connection handling
            connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
            engine = create_engine(connection_string)
            df = pd.read_sql_query(query, engine)
            engine.dispose()  # Properly close the engine
            return df
        except Exception as e:
            print(f"Error loading data from PostgreSQL: {e}")
            return pd.DataFrame()
    
    def add_application(self, application_data):
        """Add or update a job application with smart deduplication and status hierarchy"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            email_id = application_data.get('email_id')
            related_app_id = application_data.get('related_application_id')
            
            # Check if this email was already processed
            cursor.execute("SELECT id, status FROM job_applications WHERE email_id = %s", (email_id,))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing record, but respect status hierarchy
                existing_id, current_status = existing
                new_status = application_data.get('status')
                
                valid_columns = [
                    'date', 'job_title', 'company', 'location', 'status',
                    'application_date', 'sender', 'subject', 'related_application_id',
                    'confidence', 'reasoning'
                ]
                update_fields = []
                update_values = []
                
                for key, value in application_data.items():
                    if key in valid_columns and value is not None:
                        # Special handling for status updates
                        if key == 'status' and new_status:
                            if should_update_status(current_status, new_status):
                                update_fields.append(f"{key} = %s")
                                update_values.append(value)
                            else:
                                print(f"  ⚠️  Skipping status update: {current_status} -> {new_status} (would be backward)")
                        else:
                            update_fields.append(f"{key} = %s")
                            update_values.append(value)
                
                if update_fields:
                    update_values.append(email_id)
                    update_query = f"""
                        UPDATE job_applications 
                        SET {', '.join(update_fields)}, last_updated = CURRENT_TIMESTAMP
                        WHERE email_id = %s
                    """
                    cursor.execute(update_query, update_values)
                    conn.commit()
                
                # Mark email as processed
                self.mark_email_processed(email_id, existing_id)
                return self.load_data()
            
            # Check if this is linked to an existing application
            if related_app_id:
                cursor.execute(
                    "SELECT id, status FROM job_applications WHERE email_id = %s",
                    (related_app_id,)
                )
                related_app = cursor.fetchone()
                
                if related_app:
                    # Update the related application with status hierarchy check
                    related_id, current_status = related_app
                    new_status = application_data.get('status')
                    
                    update_fields = []
                    update_values = []
                    
                    valid_columns = [
                        'date', 'job_title', 'company', 'location', 'status',
                        'application_date', 'sender', 'subject', 'related_application_id',
                        'confidence', 'reasoning'
                    ]
                    for key, value in application_data.items():
                        if key in valid_columns and value is not None:
                            # For status, use status hierarchy to prevent backward movement
                            if key == 'status' and new_status:
                                if should_update_status(current_status, new_status):
                                    update_fields.append(f"{key} = %s")
                                    update_values.append(value)
                                else:
                                    print(f"  ⚠️  Skipping status update on related app: {current_status} -> {new_status}")
                            else:
                                update_fields.append(f"{key} = %s")
                                update_values.append(value)
                    
                    if update_fields:
                        update_values.append(related_app_id)
                        update_query = f"""
                            UPDATE job_applications 
                            SET {', '.join(update_fields)}, last_updated = CURRENT_TIMESTAMP
                            WHERE email_id = %s
                        """
                        cursor.execute(update_query, update_values)
                        conn.commit()
                    
                    # Mark this email as processed and linked to the related application
                    self.mark_email_processed(email_id, related_id)
                    return self.load_data()
            
            # Check for fuzzy matches (same company + similar role + similar application date)
            company = application_data.get('company', '').lower() if application_data.get('company') else None
            role = application_data.get('job_title', '').lower() if application_data.get('job_title') else None
            app_date = application_data.get('application_date')
            
            if company:
                # Find potential matches: same company
                cursor.execute(
                    """SELECT email_id, company, job_title, status, application_date 
                       FROM job_applications 
                       WHERE LOWER(company) LIKE %s 
                       ORDER BY application_date DESC NULLS LAST, date DESC""",
                    (f'%{company}%',)
                )
                matches = cursor.fetchall()
                
                for match in matches:
                    existing_email_id, existing_company, existing_role, existing_status, existing_app_date = match
                    existing_company_lower = str(existing_company).lower() if existing_company else ''
                    existing_role_lower = str(existing_role).lower() if existing_role else ''
                    
                    # Check if companies match
                    company_match = (company in existing_company_lower or existing_company_lower in company or 
                                   company == existing_company_lower)
                    
                    if not company_match:
                        continue
                    
                    # Check role similarity
                    role_match = False
                    if role and existing_role_lower:
                        role_words = set(role.split())
                        existing_role_words = set(existing_role_lower.split())
                        # At least 2 words in common for better matching
                        common_words = role_words & existing_role_words
                        if len(common_words) >= 2 or (len(common_words) >= 1 and len(role_words) <= 3):
                            role_match = True
                    elif not role or not existing_role_lower:
                        # If one is missing, still consider it a match if company matches
                        role_match = True
                    
                    # Check application date similarity (within 30 days)
                    date_match = True
                    if app_date and existing_app_date:
                        try:
                            from datetime import datetime, timedelta
                            app_date_obj = datetime.strptime(app_date, '%Y-%m-%d') if isinstance(app_date, str) else app_date
                            existing_date_obj = existing_app_date if isinstance(existing_app_date, datetime) else datetime.strptime(str(existing_app_date), '%Y-%m-%d')
                            date_diff = abs((app_date_obj - existing_date_obj).days)
                            date_match = date_diff <= 30  # Within 30 days
                        except:
                            date_match = True  # If date parsing fails, assume match
                    
                    # If company + role match (and optionally date), it's likely the same application
                    if company_match and role_match and date_match:
                        print(f"  🔗 Found matching application: {existing_company} - {existing_role}")
                        # Update the existing application with new information
                        cursor.execute("SELECT status FROM job_applications WHERE email_id = %s", (existing_email_id,))
                        current_status_result = cursor.fetchone()
                        current_status = current_status_result[0] if current_status_result else None
                        new_status = application_data.get('status')
                        
                        update_fields = []
                        update_values = []
                        
                        valid_columns = ['date', 'job_title', 'company', 'location', 'status', 
                                        'application_date', 'sender', 'subject', 'related_application_id',
                                        'confidence', 'reasoning']
                        
                        for key, value in application_data.items():
                            if key in valid_columns and value is not None:
                                # Check status hierarchy
                                if key == 'status' and new_status and current_status:
                                    if should_update_status(current_status, new_status):
                                        update_fields.append(f"{key} = %s")
                                        update_values.append(value)
                                    else:
                                        print(f"  ⚠️  Skipping status update: {current_status} -> {new_status}")
                                else:
                                    # For other fields, update if missing or if new value is more complete
                                    cursor.execute(
                                        sql.SQL("SELECT {} FROM job_applications WHERE email_id = %s").format(
                                            sql.Identifier(key)
                                        ),
                                        (existing_email_id,)
                                    )
                                    existing_value = cursor.fetchone()
                                    if not existing_value or not existing_value[0] or value:
                                        update_fields.append(f"{key} = %s")
                                        update_values.append(value)
                        
                        if update_fields:
                            update_values.append(existing_email_id)
                            update_query = f"""
                                UPDATE job_applications 
                                SET {', '.join(update_fields)}, last_updated = CURRENT_TIMESTAMP
                                WHERE email_id = %s
                            """
                            cursor.execute(update_query, update_values)
                            conn.commit()
                        
                        # Link this email to the existing application
                        cursor.execute("SELECT id FROM job_applications WHERE email_id = %s", (existing_email_id,))
                        app_id_result = cursor.fetchone()
                        app_id = app_id_result[0] if app_id_result else None
                        
                        # Mark this email as processed and linked
                        self.mark_email_processed(email_id, app_id)
                        
                        # Update related_application_id to link them
                        cursor.execute(
                            "UPDATE job_applications SET related_application_id = %s WHERE email_id = %s",
                            (existing_email_id, email_id)
                        )
                        conn.commit()
                        
                        return self.load_data()
            
            # New application - insert it
            # Define valid database columns (exclude metadata fields like 'is_new_application')
            valid_columns = [
                'email_id', 'date', 'job_title', 'company', 'location', 'status',
                'application_date', 'sender', 'subject', 'related_application_id',
                'confidence', 'reasoning'
            ]
            
            insert_fields = []
            insert_values = []
            placeholders = []
            
            for key, value in application_data.items():
                # Only include valid database columns
                if key in valid_columns and value is not None:
                    insert_fields.append(key)
                    insert_values.append(value)
                    placeholders.append('%s')
            
            # Build UPDATE clause for ON CONFLICT (update all fields except email_id)
            update_clauses = [f"{field} = EXCLUDED.{field}" for field in insert_fields if field != 'email_id']
            update_clauses.append("last_updated = CURRENT_TIMESTAMP")
            
            insert_query = f"""
                INSERT INTO job_applications ({', '.join(insert_fields)})
                VALUES ({', '.join(placeholders)})
                ON CONFLICT (email_id) DO UPDATE SET
                    {', '.join(update_clauses)}
            """
            
            cursor.execute(insert_query, insert_values)
            conn.commit()
            
            # Get the ID of the newly inserted application
            cursor.execute("SELECT id FROM job_applications WHERE email_id = %s", (email_id,))
            app_id_result = cursor.fetchone()
            app_id = app_id_result[0] if app_id_result else None
            
            # Mark email as processed
            self.mark_email_processed(email_id, app_id)
            
            return self.load_data()
            
        except psycopg2.Error as e:
            print(f"Error adding application: {e}")
            conn.rollback()
            return pd.DataFrame()
        finally:
            cursor.close()
            conn.close()
    
    def get_applications(self):
        """Get all applications"""
        return self.load_data()
    
    def update_status(self, email_id, new_status):
        """Update status of a specific application"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "UPDATE job_applications SET status = %s, last_updated = CURRENT_TIMESTAMP WHERE email_id = %s",
                (new_status, email_id)
            )
            conn.commit()
            return cursor.rowcount > 0
        except psycopg2.Error as e:
            print(f"Error updating status: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()
    
    def update_location(self, email_id, new_location):
        """Update location of a specific application"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "UPDATE job_applications SET location = %s, last_updated = CURRENT_TIMESTAMP WHERE email_id = %s",
                (new_location, email_id)
            )
            conn.commit()
            return cursor.rowcount > 0
        except psycopg2.Error as e:
            print(f"Error updating location: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()
    
    def get_statistics(self):
        """Get statistics about applications"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            stats = {}
            
            # Total count
            cursor.execute("SELECT COUNT(*) FROM job_applications")
            stats['total'] = cursor.fetchone()[0]
            
            # By status
            cursor.execute("""
                SELECT status, COUNT(*) as count 
                FROM job_applications 
                GROUP BY status
            """)
            stats['by_status'] = {row[0]: row[1] for row in cursor.fetchall()}
            
            # By company (top 10)
            cursor.execute("""
                SELECT company, COUNT(*) as count 
                FROM job_applications 
                WHERE company IS NOT NULL
                GROUP BY company 
                ORDER BY count DESC 
                LIMIT 10
            """)
            stats['by_company'] = {row[0]: row[1] for row in cursor.fetchall()}
            
            # By location (top 10)
            cursor.execute("""
                SELECT location, COUNT(*) as count 
                FROM job_applications 
                WHERE location IS NOT NULL
                GROUP BY location 
                ORDER BY count DESC 
                LIMIT 10
            """)
            stats['by_location'] = {row[0]: row[1] for row in cursor.fetchall()}
            
            return stats
            
        except psycopg2.Error as e:
            print(f"Error getting statistics: {e}")
            return {
                'total': 0,
                'by_status': {},
                'by_company': {},
                'by_location': {}
            }
        finally:
            cursor.close()
            conn.close()
