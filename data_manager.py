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
        
        CREATE INDEX IF NOT EXISTS idx_email_id ON job_applications(email_id);
        CREATE INDEX IF NOT EXISTS idx_company ON job_applications(company);
        CREATE INDEX IF NOT EXISTS idx_status ON job_applications(status);
        CREATE INDEX IF NOT EXISTS idx_related_app ON job_applications(related_application_id);
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
        """Add or update a job application with smart deduplication"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            email_id = application_data.get('email_id')
            related_app_id = application_data.get('related_application_id')
            
            # Check if this email was already processed
            cursor.execute("SELECT id FROM job_applications WHERE email_id = %s", (email_id,))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing record
                valid_columns = [
                    'date', 'job_title', 'company', 'location', 'status',
                    'application_date', 'sender', 'subject', 'related_application_id',
                    'confidence', 'reasoning'
                ]
                update_fields = []
                update_values = []
                
                for key, value in application_data.items():
                    if key in valid_columns and value is not None:
                        update_fields.append(f"{key} = %s")
                        update_values.append(value)
                
                update_values.append(email_id)
                update_query = f"""
                    UPDATE job_applications 
                    SET {', '.join(update_fields)}, last_updated = CURRENT_TIMESTAMP
                    WHERE email_id = %s
                """
                cursor.execute(update_query, update_values)
                conn.commit()
                return self.load_data()
            
            # Check if this is linked to an existing application
            if related_app_id:
                cursor.execute(
                    "SELECT id FROM job_applications WHERE email_id = %s",
                    (related_app_id,)
                )
                related_app = cursor.fetchone()
                
                if related_app:
                    # Update the related application
                    update_fields = []
                    update_values = []
                    
                    valid_columns = [
                        'date', 'job_title', 'company', 'location', 'status',
                        'application_date', 'sender', 'subject', 'related_application_id',
                        'confidence', 'reasoning'
                    ]
                    for key, value in application_data.items():
                        if key in valid_columns and value is not None:
                            # For status, only update if it's more advanced
                            if key == 'status' and value:
                                cursor.execute(
                                    "SELECT status FROM job_applications WHERE email_id = %s",
                                    (related_app_id,)
                                )
                                result = cursor.fetchone()
                                current_status = result[0] if result else None
                                status_order = {'Applied': 0, 'In Progress': 1, 'Rejected': 2, 'Withdrawn': 3}
                                if current_status and status_order.get(value, 0) <= status_order.get(current_status, 0):
                                    continue
                            
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
                    return self.load_data()
            
            # Check for fuzzy matches (same company + similar role)
            company = application_data.get('company', '').lower() if application_data.get('company') else None
            role = application_data.get('job_title', '').lower() if application_data.get('job_title') else None
            
            if company:
                cursor.execute(
                    "SELECT email_id, company, job_title FROM job_applications WHERE LOWER(company) LIKE %s",
                    (f'%{company}%',)
                )
                matches = cursor.fetchall()
                
                for match in matches:
                    existing_email_id, existing_company, existing_role = match
                    existing_company_lower = str(existing_company).lower() if existing_company else ''
                    existing_role_lower = str(existing_role).lower() if existing_role else ''
                    
                    # Same company and similar role
                    if company in existing_company_lower or existing_company_lower in company:
                        if role and existing_role_lower:
                            role_words = set(role.split())
                            existing_role_words = set(existing_role_lower.split())
                            if len(role_words & existing_role_words) >= 1:
                                # Likely same application - update instead of creating new
                                update_fields = []
                                update_values = []
                                
                                for key, value in application_data.items():
                                    if key not in ['email_id'] and value is not None:
                                        # Use parameterized query with column name validation
                                        valid_columns = ['date', 'job_title', 'company', 'location', 'status', 
                                                        'application_date', 'sender', 'subject', 'related_application_id',
                                                        'confidence', 'reasoning']
                                        if key in valid_columns:
                                            cursor.execute(
                                                sql.SQL("SELECT {} FROM job_applications WHERE email_id = %s").format(
                                                    sql.Identifier(key)
                                                ),
                                                (existing_email_id,)
                                            )
                                            existing_value = cursor.fetchone()
                                            if not existing_value or not existing_value[0]:
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
