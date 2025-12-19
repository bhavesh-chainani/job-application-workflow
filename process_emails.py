"""
Email Processing Module
Main script to process emails from Gmail and update job application database
"""
import os
from gmail_auth import get_gmail_service
from llm_parser import parse_email_with_llm, find_related_application
from data_manager import DataManager
from config import EMAIL_SEARCH_QUERY, PROCESS_ONLY_UNREAD, MARK_AS_READ


def get_emails(service, query=EMAIL_SEARCH_QUERY, max_results=50):
    """Fetch emails from Gmail"""
    try:
        results = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=max_results
        ).execute()
        
        messages = results.get('messages', [])
        return messages
    except Exception as e:
        print(f"Error fetching emails: {e}")
        return []


def get_email_details(service, msg_id):
    """Get full details of an email"""
    try:
        message = service.users().messages().get(
            userId='me',
            id=msg_id,
            format='full'
        ).execute()
        return message
    except Exception as e:
        print(f"Error fetching email details: {e}")
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
    
    print("Fetching emails...")
    messages = get_emails(service, query=EMAIL_SEARCH_QUERY)
    
    if not messages:
        print("No emails found matching the query.")
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
            
            # Check if email was already processed
            email_id = application_data.get('email_id')
            is_already_processed = email_id in existing_df['email_id'].values if not existing_df.empty else False
            
            if is_already_processed:
                print("  ↻ Already processed, updating...")
                updated_applications += 1
            elif not application_data.get('is_new_application') and application_data.get('related_application_id'):
                print(f"  🔗 Linked to existing application")
                updated_applications += 1
            else:
                print("  ✓ New application detected")
                new_applications += 1
            
            # Add/update application to PostgreSQL database
            print("  💾 Saving to PostgreSQL database...")
            data_manager.add_application(application_data)
            print("  ✓ Saved successfully")
            
            # Reload existing_df to include newly added applications
            existing_df = data_manager.load_data()
            
        except Exception as e:
            print(f"  ❌ Error processing email: {e}")
            skipped_count += 1
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


if __name__ == '__main__':
    process_emails()

