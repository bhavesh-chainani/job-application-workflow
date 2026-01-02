"""
Email Processing Module
Main script to process emails from Gmail and update job application database
"""
import os
import time
from datetime import datetime
from googleapiclient.errors import HttpError
from gmail_auth import get_gmail_service
from llm_parser import parse_email_with_llm, find_related_application
from data_manager import DataManager
from config import EMAIL_SEARCH_QUERY, PROCESS_ONLY_UNREAD, MARK_AS_READ, GMAIL_API_TIMEOUT, GMAIL_API_MAX_RETRIES


def get_emails(service, query=EMAIL_SEARCH_QUERY, max_results=50):
    """Fetch emails from Gmail with retry logic and timeout handling"""
    for attempt in range(GMAIL_API_MAX_RETRIES):
        try:
            print(f"  Attempting to fetch emails (attempt {attempt + 1}/{GMAIL_API_MAX_RETRIES})...")
            
            # Build the request
            request = service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            )
            
            # Execute with timeout
            results = request.execute()
            
            messages = results.get('messages', [])
            print(f"  ✓ Successfully fetched {len(messages)} email(s)")
            return messages
            
        except HttpError as e:
            error_reason = e.error_details[0].get('reason', 'unknown') if e.error_details else 'unknown'
            error_status = e.resp.status if hasattr(e, 'resp') else 'unknown'
            
            if error_status == 404:
                print(f"  ⚠️  Label not found. The query '{query}' may reference a label that doesn't exist.")
                print(f"     Try creating the label in Gmail or updating EMAIL_SEARCH_QUERY in config.py")
                return []
            elif error_status == 403:
                print(f"  ❌ Permission denied. Check your Gmail API scopes and permissions.")
                return []
            elif attempt < GMAIL_API_MAX_RETRIES - 1:
                wait_time = (attempt + 1) * 2  # Exponential backoff: 2s, 4s, 6s
                print(f"  ⚠️  Error (attempt {attempt + 1}): {e}")
                print(f"     Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"  ❌ Error fetching emails after {GMAIL_API_MAX_RETRIES} attempts: {e}")
                print(f"     Status: {error_status}, Reason: {error_reason}")
                return []
                
        except Exception as e:
            error_msg = str(e).lower()
            if 'timeout' in error_msg or 'timed out' in error_msg:
                if attempt < GMAIL_API_MAX_RETRIES - 1:
                    wait_time = (attempt + 1) * 2
                    print(f"  ⚠️  Request timed out (attempt {attempt + 1})")
                    print(f"     Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print(f"  ❌ Request timed out after {GMAIL_API_MAX_RETRIES} attempts")
                    print(f"     This could be due to:")
                    print(f"     - Network connectivity issues")
                    print(f"     - Gmail API being slow or unavailable")
                    print(f"     - The query '{query}' taking too long to process")
                    print(f"     Try:")
                    print(f"     1. Check your internet connection")
                    print(f"     2. Try a simpler query in config.py (e.g., 'is:unread' instead of label)")
                    print(f"     3. Wait a few minutes and try again")
                    return []
            else:
                print(f"  ❌ Error fetching emails: {e}")
                return []
    
    return []


def get_email_details(service, msg_id):
    """Get full details of an email with retry logic"""
    for attempt in range(GMAIL_API_MAX_RETRIES):
        try:
            message = service.users().messages().get(
                userId='me',
                id=msg_id,
                format='full'
            ).execute()
            return message
        except HttpError as e:
            if attempt < GMAIL_API_MAX_RETRIES - 1:
                wait_time = (attempt + 1) * 2
                print(f"  ⚠️  Error fetching email details (attempt {attempt + 1}): {e}")
                print(f"     Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"  ❌ Error fetching email details after {GMAIL_API_MAX_RETRIES} attempts: {e}")
                return None
        except Exception as e:
            error_msg = str(e).lower()
            if 'timeout' in error_msg or 'timed out' in error_msg:
                if attempt < GMAIL_API_MAX_RETRIES - 1:
                    wait_time = (attempt + 1) * 2
                    time.sleep(wait_time)
                else:
                    print(f"  ❌ Timeout fetching email details: {e}")
                    return None
            else:
                print(f"  ❌ Error fetching email details: {e}")
                return None
    return None


def mark_as_read(service, msg_id):
    """Mark an email as read"""
    try:
        service.users().messages().modify(
            userId='me',
            id=msg_id,
            body={'removeLabelIds': ['UNREAD']}
        ).execute()
        return True
    except Exception as e:
        print(f"Error marking email as read: {e}")
        return False


def process_emails():
    """Main function to process emails"""
    print("Connecting to Gmail...")
    service = get_gmail_service()
    
    if not service:
        print("Failed to connect to Gmail. Please check your credentials.")
        return
    
    print(f"Fetching emails with query: '{EMAIL_SEARCH_QUERY}'...")
    messages = get_emails(service, query=EMAIL_SEARCH_QUERY)
    
    if not messages:
        print("\n⚠️  No emails found matching the query.")
        print(f"   Query used: '{EMAIL_SEARCH_QUERY}'")
        print("\n   Troubleshooting tips:")
        print("   1. Check if the label exists in your Gmail")
        print("   2. Try updating EMAIL_SEARCH_QUERY in config.py to:")
        print("      - 'is:unread' (for unread emails)")
        print("      - 'from:recruiter OR from:jobs' (for specific senders)")
        print("      - 'subject:application OR subject:interview' (for keywords)")
        print("   3. Make sure you have emails matching the query")
        return
    
    print(f"Found {len(messages)} emails to process")
    
    data_manager = DataManager()
    # Load existing applications once for LLM context
    existing_df = data_manager.load_data()
    
    processed_count = 0
    new_applications = 0
    updated_applications = 0
    skipped_count = 0
    
    for msg in messages:
        msg_id = msg['id']
        print(f"\nProcessing email {processed_count + 1}/{len(messages)}...")
        
        # Check if email was already processed BEFORE fetching details
        if data_manager.is_email_processed(msg_id):
            print(f"  ⏭️  Skipping: Email already processed")
            skipped_count += 1
            continue
        
        email_data = get_email_details(service, msg_id)
        if not email_data:
            continue
        
        try:
            # Parse email using LLM
            print("  🤖 Analyzing with LLM...")
            application_data = parse_email_with_llm(email_data, existing_df)
            
            # Check if this looks like a job application email
            if not application_data.get('company'):
                print("  ⚠ Skipping: No company identified")
                skipped_count += 1
                # Still mark as processed to avoid re-checking
                data_manager.mark_email_processed(msg_id)
                if MARK_AS_READ:
                    mark_as_read(service, msg_id)
                continue
            
            # Display LLM extraction results
            print(f"  📊 Extracted:")
            print(f"     Company: {application_data.get('company', 'N/A')}")
            print(f"     Role: {application_data.get('job_title', 'N/A')}")
            print(f"     Status: {application_data.get('status', 'N/A')}")
            print(f"     Location: {application_data.get('location', 'N/A')}")
            print(f"     Application Date: {application_data.get('application_date', 'N/A')}")
            if application_data.get('reasoning'):
                print(f"     Reasoning: {application_data.get('reasoning', '')[:100]}")
            
            # Check if this is a new application or update
            email_id = application_data.get('email_id')
            is_existing_application = email_id in existing_df['email_id'].values if not existing_df.empty else False
            
            if is_existing_application:
                print("  ↻ Updating existing application...")
                updated_applications += 1
            elif not application_data.get('is_new_application') and application_data.get('related_application_id'):
                print(f"  🔗 Linked to existing application")
                updated_applications += 1
            else:
                print("  ✓ New application detected")
                new_applications += 1
            
            # Add/update application to PostgreSQL database
            # (This will also mark the email as processed)
            print("  💾 Saving to PostgreSQL database...")
            data_manager.add_application(application_data)
            print("  ✓ Saved successfully")
            
            # Reload existing_df to include newly added applications
            existing_df = data_manager.load_data()
            
        except Exception as e:
            print(f"  ❌ Error processing email: {e}")
            skipped_count += 1
            # Mark as processed even on error to avoid infinite retries
            data_manager.mark_email_processed(msg_id)
            continue
        
        # Mark as read if configured
        if MARK_AS_READ:
            mark_as_read(service, msg_id)
        
        processed_count += 1
    
    print(f"\n{'='*50}")
    print(f"Processing complete!")
    print(f"  Total processed: {processed_count}")
    print(f"  New applications: {new_applications}")
    print(f"  Updated applications: {updated_applications}")
    if skipped_count > 0:
        print(f"  Skipped: {skipped_count}")
    print(f"{'='*50}")
    
    # Save last run timestamp
    try:
        last_run_file = os.path.join(os.path.dirname(__file__), '.last_run')
        with open(last_run_file, 'w') as f:
            f.write(datetime.now().isoformat())
    except Exception as e:
        print(f"Warning: Could not save last run timestamp: {e}")


if __name__ == '__main__':
    process_emails()

