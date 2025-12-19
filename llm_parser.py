"""
LLM-based Email Parser Module
Uses OpenAI to intelligently extract job application information from emails
"""
import json
import re
from email.utils import parsedate_to_datetime
from bs4 import BeautifulSoup
from datetime import datetime
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL


def extract_text_from_html(html_content):
    """Extract plain text from HTML email content"""
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, 'html.parser')
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()
    return soup.get_text(separator='\n', strip=True)


def extract_email_body(email_data):
    """Extract full email body text from Gmail API response"""
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
    return extract_body_recursive(payload).strip()


def extract_email_headers(email_data):
    """Extract email headers"""
    headers = {}
    for header in email_data.get('payload', {}).get('headers', []):
        name = header.get('name', '').lower()
        value = header.get('value', '')
        headers[name] = value
    return headers


def parse_email_with_llm(email_data, existing_applications=None):
    """
    Parse email using OpenAI LLM to extract job application information
    
    Args:
        email_data: Gmail API email data
        existing_applications: List of existing applications to help detect duplicates
    
    Returns:
        dict with extracted information
    """
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not set. Please set it in config.py or as environment variable.")
    
    # Extract email content
    headers = extract_email_headers(email_data)
    subject = headers.get('subject', '')
    sender = headers.get('from', '')
    date_str = headers.get('date', '')
    email_id = email_data.get('id', '')
    
    # Parse date
    try:
        email_date = parsedate_to_datetime(date_str).isoformat() if date_str else datetime.now().isoformat()
    except:
        email_date = datetime.now().isoformat()
    
    # Extract body
    body_text = extract_email_body(email_data)
    
    # Prepare existing applications context for duplicate detection
    existing_context = ""
    if existing_applications is not None and not existing_applications.empty:
        existing_context = "\n\nExisting job applications in database:\n"
        for _, app in existing_applications.iterrows():
            existing_context += f"- Company: {app.get('company', 'N/A')}, Role: {app.get('job_title', 'N/A')}, "
            existing_context += f"Status: {app.get('status', 'N/A')}, Application Date: {app.get('application_date', 'N/A')}\n"
    
    # Prepare prompt for LLM
    prompt = f"""You are an expert at extracting job application information from emails. Analyze the following email and extract structured information.

Email Subject: {subject}
Email From: {sender}
Email Date: {date_str}
Email Body:
{body_text[:4000]}
{existing_context}

Extract the following information:
1. **Company**: The company name (e.g., "Google", "Microsoft", "DoorDash")
2. **Application Date**: The date when the application was submitted (not the email date). Look for phrases like "applied on", "application submitted", "thank you for applying on". If not found, use the email date.
3. **Role/Job Title**: The specific job title or role (e.g., "Software Engineer", "Data Analyst", "Product Manager")
4. **Status**: Current status of the application. Must be one of: "Applied", "Recruiter Screen", "Interview", "Rejected", "Ghosted", "Dropped", "Offer"
   - "Applied": Initial application confirmation
   - "Recruiter Screen": Passed initial screening, recruiter contacted, phone screen scheduled
   - "Interview": Interview scheduled or in progress, technical interview, final round
   - "Rejected": Not selected, declined, unfortunately, application not moving forward
   - "Ghosted": No response after application or follow-up, radio silence
   - "Dropped": Application cancelled or withdrawn by applicant
   - "Offer": Job offer received, offer extended, congratulations on offer
5. **Location**: Job location (city, state, country, or remote). Can be "Remote" if mentioned.

Additionally, determine if this email is related to an existing application in the database. Consider:
- Same company AND same role = same application
- Same company with similar role = likely same application
- Different company OR clearly different role = new application

Return a JSON object with this exact structure:
{{
    "company": "Company Name or null",
    "application_date": "YYYY-MM-DD or null",
    "role": "Job Title or null",
    "status": "Applied|Recruiter Screen|Interview|Rejected|Ghosted|Dropped|Offer",
    "location": "Location or null",
    "is_new_application": true or false,
    "related_application_id": "email_id of related application or null",
    "confidence": "high|medium|low",
    "reasoning": "Brief explanation of extraction and linking decision"
}}

Be precise and extract only information that is clearly stated in the email. If information is not available, use null."""

    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a precise data extraction assistant. Always return valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,  # Low temperature for consistent extraction
            response_format={"type": "json_object"}
        )
        
        # Parse LLM response
        content = response.choices[0].message.content
        parsed_data = json.loads(content)
        
        # Build result dictionary
        result = {
            'email_id': email_id,
            'date': email_date,
            'job_title': parsed_data.get('role'),
            'company': parsed_data.get('company'),
            'location': parsed_data.get('location'),
            'status': parsed_data.get('status', 'Applied'),
            'application_date': parsed_data.get('application_date'),
            'sender': sender,
            'subject': subject,
            'is_new_application': parsed_data.get('is_new_application', True),
            'related_application_id': parsed_data.get('related_application_id'),
            'confidence': parsed_data.get('confidence', 'medium'),
            'reasoning': parsed_data.get('reasoning', ''),
        }
        
        # Clean up extracted fields
        for field in ['job_title', 'company', 'location']:
            if result.get(field):
                result[field] = result[field][:200] if len(result[field]) > 200 else result[field]
        
        return result
        
    except json.JSONDecodeError as e:
        print(f"Error parsing LLM JSON response: {e}")
        print(f"Response was: {content[:500]}")
        # Fallback to basic extraction
        return create_fallback_result(email_id, email_date, subject, sender, body_text)
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        # Fallback to basic extraction
        return create_fallback_result(email_id, email_date, subject, sender, body_text)


def create_fallback_result(email_id, email_date, subject, sender, body_text):
    """Create a basic result when LLM fails"""
    # Extract company from sender email
    company = None
    company_match = re.search(r'@([^.]+)', sender)
    if company_match:
        company = company_match.group(1).title()
    
    # Basic status detection
    status = 'Applied'
    content_lower = (subject + " " + body_text).lower()
    if any(word in content_lower for word in ['offer', 'congratulations', 'we are pleased', 'job offer']):
        status = 'Offer'
    elif any(word in content_lower for word in ['rejected', 'not selected', 'unfortunately', 'declined', 'not moving forward']):
        status = 'Rejected'
    elif any(word in content_lower for word in ['interview', 'technical interview', 'final round', 'interview scheduled']):
        status = 'Interview'
    elif any(word in content_lower for word in ['recruiter', 'phone screen', 'initial screening', 'screening call']):
        status = 'Recruiter Screen'
    elif any(word in content_lower for word in ['withdrawn', 'withdraw', 'cancelled', 'cancel']):
        status = 'Dropped'
    elif any(word in content_lower for word in ['no response', 'ghosted', 'radio silence']):
        status = 'Ghosted'
    
    return {
        'email_id': email_id,
        'date': email_date,
        'job_title': None,
        'company': company,
        'location': None,
        'status': status,
        'application_date': email_date.split('T')[0] if email_date else None,
        'sender': sender,
        'subject': subject,
        'is_new_application': True,
        'related_application_id': None,
        'confidence': 'low',
        'reasoning': 'LLM parsing failed, using fallback extraction',
    }


def find_related_application(parsed_data, existing_applications):
    """
    Find if this email is related to an existing application
    Uses LLM reasoning plus fuzzy matching
    """
    if existing_applications is None or existing_applications.empty or not parsed_data.get('is_new_application'):
        return None
    
    company = parsed_data.get('company', '').lower()
    role = parsed_data.get('job_title', '').lower()
    
    if not company:
        return None
    
    # Look for matches
    for _, app in existing_applications.iterrows():
        existing_company = str(app.get('company', '')).lower()
        existing_role = str(app.get('job_title', '')).lower()
        
        # Same company and similar role
        if company in existing_company or existing_company in company:
            if role and existing_role:
                # Check if roles are similar (simple word overlap)
                role_words = set(role.split())
                existing_role_words = set(existing_role.split())
                if len(role_words & existing_role_words) >= 1:  # At least one word in common
                    return app.get('email_id')
            elif company == existing_company:  # Same company, no role info
                return app.get('email_id')
    
    return None

