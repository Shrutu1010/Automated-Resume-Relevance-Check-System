"""
Resume upload route handlers
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
import tempfile
import os
import shutil
import logging

from ..services.parser import parser
from ..models import db, Resume

router = APIRouter(prefix="/api/resumes", tags=["resumes"])
logger = logging.getLogger(__name__)

@router.post("/upload")
async def upload_resume_file(file: UploadFile = File(...)):
    """Upload and parse resume file"""
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.pdf', '.docx', '.doc')):
            raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_path = tmp_file.name
        
        try:
            # Parse the resume
            parsed_resume = parser.parse_resume(tmp_path, file.filename)
            
            # Create Resume object
            resume = Resume(
                filename=file.filename,
                candidate_name=parsed_resume.candidate_name,
                email=parsed_resume.email,
                phone=parsed_resume.phone,
                location=parsed_resume.location,
                raw_text=parsed_resume.raw_text,
                skills=parsed_resume.skills,
                projects=parsed_resume.projects,
                education=parsed_resume.education,
                certifications=parsed_resume.certifications,
                experience_years=parsed_resume.experience_years
            )
            
            # Save to database
            resume_id = db.save_resume(resume)
            
            logger.info(f"Successfully uploaded resume: {file.filename}")
            
            return {
                "id": resume_id,
                "filename": file.filename,
                "candidate_name": resume.candidate_name,
                "skills_extracted": len(resume.skills),
                "message": "Resume uploaded and parsed successfully"
            }
            
        finally:
            # Clean up temporary file
            os.unlink(tmp_path)
            
    except Exception as e:
        logger.error(f"Failed to upload resume: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload resume: {str(e)}")
