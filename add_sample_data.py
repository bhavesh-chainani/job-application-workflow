"""
Sample Data Generator
Adds sample job applications at different pipeline stages for testing/demo purposes
Run this to populate the database with sample data to visualize the Sankey diagram
"""
from data_manager import DataManager
from datetime import datetime, timedelta
import random

def add_sample_data():
    """Add sample job applications at various stages"""
    print("Adding sample job application data...")
    print("=" * 50)
    
    data_manager = DataManager()
    
    # Sample companies
    companies = [
        "Google", "Microsoft", "Amazon", "Meta", "Apple", 
        "Netflix", "Uber", "Airbnb", "Stripe", "Shopify",
        "DoorDash", "LinkedIn", "Salesforce", "Oracle", "IBM"
    ]
    
    # Sample locations
    locations = [
        "Singapore", "USA", "Netherlands", "UK", "Canada",
        "Australia", "Germany", "France", "Japan", "Remote"
    ]
    
    # Sample job titles
    job_titles = [
        "Software Engineer", "Data Analyst", "Product Manager",
        "Data Scientist", "Backend Engineer", "Frontend Engineer",
        "DevOps Engineer", "ML Engineer", "Business Analyst",
        "Product Designer", "UX Designer", "Engineering Manager"
    ]
    
    # Sample data with different stages
    sample_applications = [
        # Applied stage (5 applications)
        {"company": "Google", "job_title": "Software Engineer", "location": "Singapore", "status": "Applied"},
        {"company": "Microsoft", "job_title": "Data Analyst", "location": "USA", "status": "Applied"},
        {"company": "Amazon", "job_title": "Product Manager", "location": "Remote", "status": "Applied"},
        {"company": "Meta", "job_title": "Data Scientist", "location": "UK", "status": "Applied"},
        {"company": "Apple", "job_title": "Backend Engineer", "location": "Netherlands", "status": "Applied"},
        
        # Recruiter Screen stage (4 applications)
        {"company": "Netflix", "job_title": "Frontend Engineer", "location": "USA", "status": "Recruiter Screen"},
        {"company": "Uber", "job_title": "DevOps Engineer", "location": "Canada", "status": "Recruiter Screen"},
        {"company": "Airbnb", "job_title": "ML Engineer", "location": "Australia", "status": "Recruiter Screen"},
        {"company": "Stripe", "job_title": "Business Analyst", "location": "Germany", "status": "Recruiter Screen"},
        
        # Interview stage (3 applications)
        {"company": "Shopify", "job_title": "Product Designer", "location": "Remote", "status": "Interview"},
        {"company": "LinkedIn", "job_title": "UX Designer", "location": "USA", "status": "Interview"},
        {"company": "Salesforce", "job_title": "Engineering Manager", "location": "Singapore", "status": "Interview"},
        
        # Rejected outcomes - some from Applied, some from Recruiter Screen (4 applications)
        {"company": "Oracle", "job_title": "Software Engineer", "location": "France", "status": "Rejected"},  # From Applied
        {"company": "IBM", "job_title": "Data Analyst", "location": "Japan", "status": "Rejected"},  # From Applied
        {"company": "Google", "job_title": "Product Manager", "location": "UK", "status": "Rejected"},  # From Recruiter Screen
        {"company": "Microsoft", "job_title": "Backend Engineer", "location": "Netherlands", "status": "Rejected"},  # From Recruiter Screen
        
        # Ghosted outcomes - some from Applied, some from Recruiter Screen (3 applications)
        {"company": "Amazon", "job_title": "Frontend Engineer", "location": "Canada", "status": "Ghosted"},  # From Applied
        {"company": "Meta", "job_title": "DevOps Engineer", "location": "Australia", "status": "Ghosted"},  # From Applied
        {"company": "Netflix", "job_title": "ML Engineer", "location": "Germany", "status": "Ghosted"},  # From Recruiter Screen
        
        # Dropped outcomes - some from Applied, some from Recruiter Screen (2 applications)
        {"company": "Uber", "job_title": "Business Analyst", "location": "Remote", "status": "Dropped"},  # From Applied
        {"company": "Airbnb", "job_title": "Product Designer", "location": "USA", "status": "Dropped"},  # From Recruiter Screen
        
        # Offer outcomes (2 applications)
        {"company": "Stripe", "job_title": "Software Engineer", "location": "Singapore", "status": "Offer"},
        {"company": "Shopify", "job_title": "Data Scientist", "location": "USA", "status": "Offer"},
    ]
    
    added_count = 0
    skipped_count = 0
    
    for app in sample_applications:
        # Generate unique email_id for each sample
        email_id = f"sample_{app['company'].lower().replace(' ', '_')}_{app['job_title'].lower().replace(' ', '_')}_{random.randint(1000, 9999)}"
        
        # Generate random dates within the last 3 months
        days_ago = random.randint(0, 90)
        app_date = datetime.now() - timedelta(days=days_ago)
        application_date = app_date.date()
        
        application_data = {
            'email_id': email_id,
            'date': app_date.isoformat(),
            'job_title': app['job_title'],
            'company': app['company'],
            'location': app['location'],
            'status': app['status'],
            'application_date': application_date.isoformat(),
            'sender': f"noreply@{app['company'].lower().replace(' ', '')}.com",
            'subject': f"Application for {app['job_title']} at {app['company']}",
            'confidence': 'high',
            'reasoning': 'Sample data for testing Sankey diagram visualization'
        }
        
        try:
            data_manager.add_application(application_data)
            added_count += 1
            print(f"✓ Added: {app['company']} - {app['job_title']} ({app['status']})")
        except Exception as e:
            skipped_count += 1
            print(f"✗ Skipped: {app['company']} - {app['job_title']} (Error: {e})")
    
    print("\n" + "=" * 50)
    print(f"Sample data generation complete!")
    print(f"  Added: {added_count} applications")
    print(f"  Skipped: {skipped_count} applications")
    print("\nStatus breakdown:")
    
    # Show status distribution
    df = data_manager.load_data()
    if not df.empty and 'status' in df.columns:
        status_counts = df['status'].value_counts()
        for status, count in status_counts.items():
            print(f"  {status}: {count}")
    
    print("\n💡 You can now view the Sankey diagram in the dashboard!")
    print("   Run: streamlit run dashboard.py")
    print("\n⚠️  Remember: This is sample data. Delete it when done testing.")

if __name__ == '__main__':
    add_sample_data()

