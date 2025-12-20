"""
FastAPI Backend for Job Application Workflow Dashboard
Provides REST API endpoints for the React frontend
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date
import sys
import os
import pandas as pd

# Add parent directory to path to import data_manager
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_manager import DataManager

app = FastAPI(title="Job Application Workflow API", version="1.0.0")

# CORS middleware to allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize data manager
data_manager = DataManager()


class ApplicationResponse(BaseModel):
    email_id: str
    date: Optional[datetime]
    job_title: Optional[str]
    company: Optional[str]
    location: Optional[str]
    status: str
    application_date: Optional[str]
    sender: Optional[str]
    subject: Optional[str]
    last_updated: Optional[datetime]


class StatusUpdate(BaseModel):
    email_id: str
    status: str


class LocationUpdate(BaseModel):
    email_id: str
    location: Optional[str]


class StatisticsResponse(BaseModel):
    total: int
    by_status: dict
    by_company: dict
    by_location: dict


class FunnelData(BaseModel):
    stage: str
    count: int
    percentage: float


def convert_date_to_string(value):
    """Convert date/datetime objects to ISO format strings"""
    if value is None or pd.isna(value):
        return None
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return str(value) if value else None


@app.get("/")
def root():
    return {"message": "Job Application Workflow API", "version": "1.0.0"}


@app.get("/api/applications", response_model=List[ApplicationResponse])
def get_applications(status: Optional[str] = None, company: Optional[str] = None):
    """Get all applications with optional filters"""
    try:
        df = data_manager.get_applications()
        
        if df.empty:
            return []
        
        # Apply filters
        if status:
            df = df[df['status'] == status]
        if company:
            df = df[df['company'] == company]
        
        # Convert to list of dictionaries and process date fields
        applications = df.to_dict('records')
        
        # Convert date objects to strings
        for app in applications:
            if 'application_date' in app:
                app['application_date'] = convert_date_to_string(app['application_date'])
            if 'date' in app:
                app['date'] = convert_date_to_string(app['date'])
            if 'last_updated' in app:
                app['last_updated'] = convert_date_to_string(app['last_updated'])
        
        return applications
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/statistics", response_model=StatisticsResponse)
def get_statistics():
    """Get statistics about applications"""
    try:
        stats = data_manager.get_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/funnel", response_model=List[FunnelData])
def get_funnel_data():
    """Get funnel data for visualization"""
    try:
        df = data_manager.get_applications()
        
        if df.empty:
            return []
        
        # Define funnel stages in order
        stages = ['Applied', 'Recruiter Screen', 'Interview']
        outcomes = ['Rejected', 'Ghosted', 'Dropped', 'Offer']
        
        # Normalize status values
        status_mapping = {
            'In Progress': 'Recruiter Screen',
            'Withdrawn': 'Dropped',
        }
        df['status'] = df['status'].replace(status_mapping)
        
        # Count applications at each stage
        funnel_data = []
        total = len(df)
        
        if total == 0:
            return []
        
        # Count active stages
        for stage in stages:
            count = len(df[df['status'] == stage])
            percentage = (count / total) * 100 if total > 0 else 0
            funnel_data.append({
                "stage": stage,
                "count": count,
                "percentage": round(percentage, 1)
            })
        
        # Count outcomes
        for outcome in outcomes:
            count = len(df[df['status'] == outcome])
            percentage = (count / total) * 100 if total > 0 else 0
            funnel_data.append({
                "stage": outcome,
                "count": count,
                "percentage": round(percentage, 1)
            })
        
        return funnel_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/applications/status")
def update_status(update: StatusUpdate):
    """Update application status"""
    try:
        success = data_manager.update_status(update.email_id, update.status)
        if success:
            return {"message": "Status updated successfully", "email_id": update.email_id}
        else:
            raise HTTPException(status_code=404, detail="Application not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/applications/location")
def update_location(update: LocationUpdate):
    """Update application location"""
    try:
        success = data_manager.update_location(update.email_id, update.location)
        if success:
            return {"message": "Location updated successfully", "email_id": update.email_id}
        else:
            raise HTTPException(status_code=404, detail="Application not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

