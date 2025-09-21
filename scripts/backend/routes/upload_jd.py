"""
Job description upload route handlers
"""
from fastapi import APIRouter, Form, HTTPException
import logging

from ..services.parser import parser
from ..models import db, JobDescription

router = APIRouter(prefix="/api/job-descriptions", tags=["job-descriptions"])
logger = logging.getLogger(__name__)

@router.post("/create")
async def create_job_description_endpoint(
    title: str = Form(...),
    company: str = Form(""),
    description: str = Form(...),
    location: str = Form("")
):
    """Create new job description"""
    try:
        # Parse the job description
        parsed_jd = parser.parse_job_description(description)
        
        # Create JobDescription object
        jd = JobDescription(
            title=title,
            company=company or parsed_jd.company,
            description=description,
            required_skills=parsed_jd.required_skills,
            preferred_skills=parsed_jd.preferred_skills,
            qualifications=parsed_jd.qualifications,
            location=location or parsed_jd.location
        )
        
        # Save to database
        jd_id = db.save_job_description(jd)
        
        logger.info(f"Created job description: {title}")
        
        return {
            "id": jd_id,
            "title": title,
            "company": jd.company,
            "skills_extracted": len(jd.required_skills + jd.preferred_skills),
            "message": "Job description created successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to create job description: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create job description: {str(e)}")
