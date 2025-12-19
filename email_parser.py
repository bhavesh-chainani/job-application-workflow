"""
Email Parser Module
Extracts job application information from email content
"""
import re
from email.utils import parsedate_to_datetime
from bs4 import BeautifulSoup
from datetime import datetime


def extract_text_from_html(html_content):
    """Extract plain text from HTML email content"""
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.get_text()


def parse_email_for_job_application(email_data):
    """
    Parse email to extract job application information
    
    Returns dict with:
    - job_title: Extracted from subject or body
    - company: Extracted from sender or body
    - location: Extracted from body
    - status: Default 'Applied' or inferred from email
    - date: Email date
    - email_id: Gmail message ID
    """
    result = {
        'job_title': None,
        'company': None,
        'location': None,
        'status': 'Applied',  # Default status
        'date': None,
        'email_id': None,
        'sender': None,
        'subject': None
    }
    
    # Extract basic email info
    headers = email_data.get('payload', {}).get('headers', [])
    for header in headers:
        name = header.get('name', '').lower()
        value = header.get('value', '')
        
        if name == 'subject':
            result['subject'] = value
        elif name == 'from':
            result['sender'] = value
        elif name == 'date':
            try:
                result['date'] = parsedate_to_datetime(value).isoformat()
            except:
                result['date'] = datetime.now().isoformat()
    
    result['email_id'] = email_data.get('id', '')
    
    # Extract body content (handles nested parts recursively)
    def extract_body_recursive(payload):
        body_text = ""
        if 'parts' in payload:
            for part in payload['parts']:
                body_text += extract_body_recursive(part)
        else:
            body = payload.get('body', {}).get('data', '')
            mime_type = payload.get('mimeType', '')
            if body:
                import base64
                try:
                    decoded = base64.urlsafe_b64decode(body).decode('utf-8', errors='ignore')
                    if 'html' in mime_type.lower():
                        body_text += extract_text_from_html(decoded) + "\n"
                    else:
                        body_text += decoded + "\n"
                except Exception as e:
                    pass
        
        # Also check if there's a body directly in this payload
        body = payload.get('body', {}).get('data', '')
        if body and not body_text:
            import base64
            try:
                decoded = base64.urlsafe_b64decode(body).decode('utf-8', errors='ignore')
                mime_type = payload.get('mimeType', '')
                if 'html' in mime_type.lower():
                    body_text = extract_text_from_html(decoded)
                else:
                    body_text = decoded
            except:
                pass
        
        return body_text
    
    payload = email_data.get('payload', {})
    body_text = extract_body_recursive(payload)
    
    # Extract job title from subject or body
    subject = result['subject'] or ""
    body_lower = body_text.lower()
    subject_lower = subject.lower()
    
    # Common patterns for job titles
    job_title_patterns = [
        r'application.*?for\s+(.+?)(?:\s+at|\s+-|\s+\(|$)',
        r'position.*?:\s*(.+?)(?:\s+at|\s+-|\s+\(|$)',
        r'role.*?:\s*(.+?)(?:\s+at|\s+-|\s+\(|$)',
        r'job.*?:\s*(.+?)(?:\s+at|\s+-|\s+\(|$)',
        r'(.+?)\s+position',
        r'(.+?)\s+role',
    ]
    
    for pattern in job_title_patterns:
        match = re.search(pattern, subject, re.IGNORECASE)
        if match:
            result['job_title'] = match.group(1).strip()
            break
    
    # If not found in subject, try body
    if not result['job_title']:
        for pattern in job_title_patterns:
            match = re.search(pattern, body_text, re.IGNORECASE)
            if match:
                result['job_title'] = match.group(1).strip()
                break
    
    # Extract company name from sender or body
    sender = result['sender'] or ""
    # Extract from sender email (e.g., "noreply@company.com" -> "company")
    company_match = re.search(r'@([^.]+)', sender)
    if company_match:
        result['company'] = company_match.group(1).title()
    
    # Also try to extract from subject (e.g., "Job at Company Name")
    company_patterns = [
        r'at\s+([A-Z][a-zA-Z\s&]+?)(?:\s+-|\s+\(|$)',
        r'@\s*([A-Z][a-zA-Z\s&]+?)(?:\s+-|\s+\(|$)',
        r'from\s+([A-Z][a-zA-Z\s&]+?)(?:\s+-|\s+\(|$)',
    ]
    
    for pattern in company_patterns:
        match = re.search(pattern, subject, re.IGNORECASE)
        if match:
            result['company'] = match.group(1).strip()
            break
    
    # Extract location from body or subject
    location_patterns = [
        r'location[:\s]+([A-Z][a-zA-Z\s,]+?)(?:\s+[A-Z]|\s*$|\s*\n)',
        r'in\s+([A-Z][a-zA-Z\s,]+?)(?:\s+[A-Z]|\s*$|\s*\n)',
        r'\(([A-Z][a-zA-Z\s,]+?)\)',  # Location in parentheses
    ]
    
    for pattern in location_patterns:
        match = re.search(pattern, body_text, re.IGNORECASE)
        if match:
            location = match.group(1).strip()
            # Filter out common false positives
            if len(location) < 50 and not any(word in location.lower() for word in ['job', 'position', 'role', 'application']):
                result['location'] = location
                break
    
    # Determine status from email content
    status_keywords = {
        'rejected': ['rejected', 'not selected', 'unfortunately', 'not moving forward', 'declined'],
        'in progress': ['interview', 'next step', 'screening', 'shortlisted', 'reviewing'],
        'withdrawn': ['withdrawn', 'withdraw', 'cancelled']
    }
    
    email_content = (subject + " " + body_text).lower()
    for status, keywords in status_keywords.items():
        if any(keyword in email_content for keyword in keywords):
            result['status'] = status.title()
            break
    
    # Clean up extracted fields
    if result['job_title']:
        result['job_title'] = result['job_title'][:200]  # Limit length
    if result['company']:
        result['company'] = result['company'][:100]
    if result['location']:
        result['location'] = result['location'][:100]
    
    return result

