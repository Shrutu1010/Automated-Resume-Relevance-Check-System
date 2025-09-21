#!/usr/bin/env python3
"""
Script to load PDF sample data into the database
This script processes your actual PDF files (2 JDs + 10 resumes)
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.services.parser import DocumentParser
from backend.models import JobDescription, Resume, SessionLocal
from sample_data.pdf_data_loader import PDFDataManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_pdf_sample_data():
    """Load PDF sample data into database"""
    
    # Initialize components
    pdf_manager = PDFDataManager()
    parser = DocumentParser()
    db = SessionLocal()
    
    try:
        # Validate PDF files exist
        issues = pdf_manager.validate_pdf_files()
        if issues:
            logger.error("PDF validation failed:")
            for issue in issues:
                logger.error(f"  - {issue}")
            logger.error("\nPlease ensure your PDF files are placed in:")
            logger.error("  - sample_data/jds_pdf/ (for job descriptions)")
            logger.error("  - sample_data/resumes_pdf/ (for resumes)")
            return False
        
        # Load Job Descriptions
        logger.info("Loading Job Description PDFs...")
        jd_files = pdf_manager.list_jd_files()
        
        for jd_file in jd_files:
            logger.info(f"Processing JD: {jd_file.name}")
            
            # Parse PDF content
            parsed_content = parser.parse_job_description(str(jd_file))
            
            # Create database entry
            jd = JobDescription(
                title=parsed_content.get('title', jd_file.stem.replace('_', ' ').title()),
                company=parsed_content.get('company', 'Sample Company'),
                description=parsed_content.get('description', ''),
                requirements=parsed_content.get('requirements', []),
                preferred_skills=parsed_content.get('preferred_skills', []),
                location=parsed_content.get('location', 'Remote'),
                experience_level=parsed_content.get('experience_level', 'Mid-level'),
                raw_text=parsed_content.get('raw_text', ''),
                file_path=str(jd_file)
            )
            
            db.add(jd)
            logger.info(f"✅ Added JD: {jd.title}")
        
        # Load Resumes
        logger.info("\nLoading Resume PDFs...")
        resume_files = pdf_manager.list_resume_files()
        
        for resume_file in resume_files:
            logger.info(f"Processing Resume: {resume_file.name}")
            
            # Parse PDF content
            parsed_content = parser.parse_resume(str(resume_file))
            
            # Create database entry
            resume = Resume(
                candidate_name=parsed_content.get('name', resume_file.stem.replace('_', ' ').title()),
                email=parsed_content.get('email', f"{resume_file.stem}@example.com"),
                phone=parsed_content.get('phone', ''),
                skills=parsed_content.get('skills', []),
                experience=parsed_content.get('experience', []),
                education=parsed_content.get('education', []),
                projects=parsed_content.get('projects', []),
                certifications=parsed_content.get('certifications', []),
                raw_text=parsed_content.get('raw_text', ''),
                file_path=str(resume_file)
            )
            
            db.add(resume)
            logger.info(f"✅ Added Resume: {resume.candidate_name}")
        
        # Commit all changes
        db.commit()
        
        # Summary
        total_jds = len(jd_files)
        total_resumes = len(resume_files)
        
        logger.info(f"\n🎉 Successfully loaded PDF sample data:")
        logger.info(f"   📋 Job Descriptions: {total_jds}")
        logger.info(f"   📄 Resumes: {total_resumes}")
        logger.info(f"   📊 Total Documents: {total_jds + total_resumes}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error loading PDF sample data: {str(e)}")
        db.rollback()
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    success = load_pdf_sample_data()
    if not success:
        sys.exit(1)
    
    print("\n" + "="*50)
    print("📁 NEXT STEPS:")
    print("="*50)
    print("1. Place your PDF files in the correct directories:")
    print("   • Job Descriptions (2 files) → sample_data/jds_pdf/")
    print("   • Resumes (10 files) → sample_data/resumes_pdf/")
    print("")
    print("2. Run this script again to load the data:")
    print("   python scripts/load_pdf_sample_data.py")
    print("")
    print("3. Start the system:")
    print("   ./run.sh")
