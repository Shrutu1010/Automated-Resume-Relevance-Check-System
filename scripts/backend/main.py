"""
FastAPI main application for Resume Relevance Check System
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import tempfile
import shutil
from typing import List, Optional
import logging

from .models import db, JobDescription, Resume, Evaluation
from .services.parser import parser
from .services.scorer import scorer
from .services.suggestions import suggestion_generator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Resume Relevance Check System",
    description="Automated resume evaluation system for job postings",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), '..', 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Resume Relevance Check System API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "database": "connected"}

# Job Description endpoints
@app.post("/api/job-descriptions/")
async def create_job_description(
    title: str = Form(...),
    company: str = Form(""),
    description: str = Form(...),
    location: str = Form("")
):
    """Create a new job description"""
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
        
        logger.info(f"Created job description with ID: {jd_id}")
        
        return {
            "id": jd_id,
            "message": "Job description created successfully",
            "parsed_data": {
                "title": jd.title,
                "company": jd.company,
                "required_skills": jd.required_skills,
                "preferred_skills": jd.preferred_skills,
                "qualifications": jd.qualifications,
                "location": jd.location
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to create job description: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create job description: {str(e)}")

@app.get("/api/job-descriptions/")
async def get_job_descriptions():
    """Get all job descriptions"""
    try:
        jds = db.get_all_job_descriptions()
        return {
            "job_descriptions": [
                {
                    "id": jd.id,
                    "title": jd.title,
                    "company": jd.company,
                    "location": jd.location,
                    "required_skills": jd.required_skills,
                    "preferred_skills": jd.preferred_skills,
                    "created_at": jd.created_at
                }
                for jd in jds
            ]
        }
    except Exception as e:
        logger.error(f"Failed to get job descriptions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get job descriptions: {str(e)}")

@app.get("/api/job-descriptions/{jd_id}")
async def get_job_description(jd_id: int):
    """Get specific job description"""
    try:
        jd = db.get_job_description(jd_id)
        if not jd:
            raise HTTPException(status_code=404, detail="Job description not found")
        
        return {
            "id": jd.id,
            "title": jd.title,
            "company": jd.company,
            "description": jd.description,
            "required_skills": jd.required_skills,
            "preferred_skills": jd.preferred_skills,
            "qualifications": jd.qualifications,
            "location": jd.location,
            "created_at": jd.created_at
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job description {jd_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get job description: {str(e)}")

# Resume endpoints
@app.post("/api/resumes/")
async def upload_resume(file: UploadFile = File(...)):
    """Upload and parse a resume"""
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
            
            logger.info(f"Uploaded and parsed resume with ID: {resume_id}")
            
            return {
                "id": resume_id,
                "message": "Resume uploaded and parsed successfully",
                "parsed_data": {
                    "candidate_name": resume.candidate_name,
                    "email": resume.email,
                    "phone": resume.phone,
                    "location": resume.location,
                    "skills": resume.skills,
                    "projects": len(resume.projects),
                    "education": len(resume.education),
                    "certifications": len(resume.certifications),
                    "experience_years": resume.experience_years
                }
            }
            
        finally:
            # Clean up temporary file
            os.unlink(tmp_path)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload resume: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload resume: {str(e)}")

@app.get("/api/resumes/")
async def get_resumes():
    """Get all resumes"""
    try:
        resumes = db.get_all_resumes()
        return {
            "resumes": [
                {
                    "id": resume.id,
                    "filename": resume.filename,
                    "candidate_name": resume.candidate_name,
                    "email": resume.email,
                    "location": resume.location,
                    "skills_count": len(resume.skills),
                    "experience_years": resume.experience_years,
                    "created_at": resume.created_at
                }
                for resume in resumes
            ]
        }
    except Exception as e:
        logger.error(f"Failed to get resumes: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get resumes: {str(e)}")

@app.get("/api/resumes/{resume_id}")
async def get_resume(resume_id: int):
    """Get specific resume"""
    try:
        resume = db.get_resume(resume_id)
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        return {
            "id": resume.id,
            "filename": resume.filename,
            "candidate_name": resume.candidate_name,
            "email": resume.email,
            "phone": resume.phone,
            "location": resume.location,
            "skills": resume.skills,
            "projects": resume.projects,
            "education": resume.education,
            "certifications": resume.certifications,
            "experience_years": resume.experience_years,
            "created_at": resume.created_at
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get resume {resume_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get resume: {str(e)}")

# Evaluation endpoints
@app.post("/api/evaluate/")
async def evaluate_resume(resume_id: int = Form(...), jd_id: int = Form(...)):
    """Evaluate a resume against a job description"""
    try:
        # Get resume and job description
        resume = db.get_resume(resume_id)
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        jd = db.get_job_description(jd_id)
        if not jd:
            raise HTTPException(status_code=404, detail="Job description not found")
        
        # Perform scoring
        scoring_result = scorer.score_resume(resume, jd)
        
        # Generate improvement suggestions
        suggestions = suggestion_generator.generate_suggestions(resume, jd, scoring_result)
        
        # Create evaluation record
        evaluation = Evaluation(
            resume_id=resume_id,
            jd_id=jd_id,
            relevance_score=scoring_result.relevance_score,
            fit_verdict=scoring_result.fit_verdict,
            hard_match_score=scoring_result.hard_match_score,
            semantic_match_score=scoring_result.semantic_match_score,
            missing_skills=scoring_result.missing_skills,
            missing_projects=scoring_result.missing_projects,
            missing_certifications=scoring_result.missing_certifications,
            improvement_suggestions=suggestions
        )
        
        # Save evaluation
        eval_id = db.save_evaluation(evaluation)
        
        logger.info(f"Evaluated resume {resume_id} against JD {jd_id}, score: {scoring_result.relevance_score}")
        
        return {
            "evaluation_id": eval_id,
            "resume_id": resume_id,
            "jd_id": jd_id,
            "relevance_score": scoring_result.relevance_score,
            "fit_verdict": scoring_result.fit_verdict,
            "hard_match_score": scoring_result.hard_match_score,
            "semantic_match_score": scoring_result.semantic_match_score,
            "missing_skills": scoring_result.missing_skills,
            "missing_projects": scoring_result.missing_projects,
            "missing_certifications": scoring_result.missing_certifications,
            "improvement_suggestions": suggestions,
            "skill_matches": scoring_result.skill_matches,
            "candidate_name": resume.candidate_name,
            "job_title": jd.title
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to evaluate resume: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to evaluate resume: {str(e)}")

@app.post("/api/evaluate-batch/")
async def evaluate_batch(jd_id: int = Form(...), resume_ids: str = Form(...)):
    """Evaluate multiple resumes against a job description"""
    try:
        # Parse resume IDs
        resume_id_list = [int(id.strip()) for id in resume_ids.split(',') if id.strip()]
        
        if not resume_id_list:
            raise HTTPException(status_code=400, detail="No resume IDs provided")
        
        # Get job description
        jd = db.get_job_description(jd_id)
        if not jd:
            raise HTTPException(status_code=404, detail="Job description not found")
        
        results = []
        
        for resume_id in resume_id_list:
            try:
                # Get resume
                resume = db.get_resume(resume_id)
                if not resume:
                    logger.warning(f"Resume {resume_id} not found, skipping")
                    continue
                
                # Perform scoring
                scoring_result = scorer.score_resume(resume, jd)
                
                # Generate suggestions
                suggestions = suggestion_generator.generate_suggestions(resume, jd, scoring_result)
                
                # Create evaluation record
                evaluation = Evaluation(
                    resume_id=resume_id,
                    jd_id=jd_id,
                    relevance_score=scoring_result.relevance_score,
                    fit_verdict=scoring_result.fit_verdict,
                    hard_match_score=scoring_result.hard_match_score,
                    semantic_match_score=scoring_result.semantic_match_score,
                    missing_skills=scoring_result.missing_skills,
                    missing_projects=scoring_result.missing_projects,
                    missing_certifications=scoring_result.missing_certifications,
                    improvement_suggestions=suggestions
                )
                
                # Save evaluation
                eval_id = db.save_evaluation(evaluation)
                
                results.append({
                    "evaluation_id": eval_id,
                    "resume_id": resume_id,
                    "candidate_name": resume.candidate_name,
                    "relevance_score": scoring_result.relevance_score,
                    "fit_verdict": scoring_result.fit_verdict,
                    "missing_skills": scoring_result.missing_skills
                })
                
            except Exception as e:
                logger.error(f"Failed to evaluate resume {resume_id}: {e}")
                continue
        
        logger.info(f"Batch evaluated {len(results)} resumes against JD {jd_id}")
        
        return {
            "jd_id": jd_id,
            "job_title": jd.title,
            "total_evaluated": len(results),
            "results": sorted(results, key=lambda x: x['relevance_score'], reverse=True)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to perform batch evaluation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to perform batch evaluation: {str(e)}")

@app.get("/api/evaluations/jd/{jd_id}")
async def get_evaluations_by_jd(jd_id: int):
    """Get all evaluations for a job description"""
    try:
        evaluations = db.get_evaluations_by_jd(jd_id)
        
        # Get additional data for each evaluation
        results = []
        for eval in evaluations:
            resume = db.get_resume(eval.resume_id)
            results.append({
                "evaluation_id": eval.id,
                "resume_id": eval.resume_id,
                "candidate_name": resume.candidate_name if resume else "Unknown",
                "candidate_email": resume.email if resume else "",
                "candidate_location": resume.location if resume else "",
                "relevance_score": eval.relevance_score,
                "fit_verdict": eval.fit_verdict,
                "hard_match_score": eval.hard_match_score,
                "semantic_match_score": eval.semantic_match_score,
                "missing_skills": eval.missing_skills,
                "missing_projects": eval.missing_projects,
                "missing_certifications": eval.missing_certifications,
                "improvement_suggestions": eval.improvement_suggestions,
                "created_at": eval.created_at
            })
        
        return {
            "jd_id": jd_id,
            "total_evaluations": len(results),
            "evaluations": results
        }
        
    except Exception as e:
        logger.error(f"Failed to get evaluations for JD {jd_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get evaluations: {str(e)}")

# Statistics endpoints
@app.get("/api/stats/")
async def get_statistics():
    """Get system statistics"""
    try:
        resumes = db.get_all_resumes()
        jds = db.get_all_job_descriptions()
        
        return {
            "total_resumes": len(resumes),
            "total_job_descriptions": len(jds),
            "recent_resumes": len([r for r in resumes if r.created_at]),  # Could add date filtering
            "recent_jds": len([j for j in jds if j.created_at])
        }
        
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
