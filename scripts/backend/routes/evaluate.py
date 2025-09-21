"""
Evaluation route handlers
"""
from fastapi import APIRouter, Form, HTTPException
import logging

from ..services.scorer import scorer
from ..services.suggestions import suggestion_generator
from ..models import db, Evaluation

router = APIRouter(prefix="/api/evaluate", tags=["evaluation"])
logger = logging.getLogger(__name__)

@router.post("/single")
async def evaluate_single_resume(resume_id: int = Form(...), jd_id: int = Form(...)):
    """Evaluate single resume against job description"""
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
        
        logger.info(f"Evaluated resume {resume_id} against JD {jd_id}")
        
        return {
            "evaluation_id": eval_id,
            "candidate_name": resume.candidate_name,
            "job_title": jd.title,
            "relevance_score": scoring_result.relevance_score,
            "fit_verdict": scoring_result.fit_verdict,
            "detailed_scores": {
                "hard_match": scoring_result.hard_match_score,
                "semantic_match": scoring_result.semantic_match_score
            },
            "missing_elements": {
                "skills": scoring_result.missing_skills,
                "projects": scoring_result.missing_projects,
                "certifications": scoring_result.missing_certifications
            },
            "suggestions": suggestions
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to evaluate resume: {e}")
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")
