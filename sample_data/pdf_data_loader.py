import os
import shutil
from pathlib import Path

class PDFDataManager:
    """Manages PDF sample data for the resume relevance system"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.jds_dir = self.base_dir / "jds_pdf"
        self.resumes_dir = self.base_dir / "resumes_pdf"
        
        # Create directories if they don't exist
        self.jds_dir.mkdir(exist_ok=True)
        self.resumes_dir.mkdir(exist_ok=True)
    
    def list_jd_files(self):
        """List all PDF job description files"""
        return list(self.jds_dir.glob("*.pdf"))
    
    def list_resume_files(self):
        """List all PDF resume files"""
        return list(self.resumes_dir.glob("*.pdf"))
    
    def get_sample_data_info(self):
        """Get information about available sample data"""
        jd_files = self.list_jd_files()
        resume_files = self.list_resume_files()
        
        return {
            "job_descriptions": {
                "count": len(jd_files),
                "files": [f.name for f in jd_files]
            },
            "resumes": {
                "count": len(resume_files),
                "files": [f.name for f in resume_files]
            }
        }
    
    def validate_pdf_files(self):
        """Validate that PDF files exist and are readable"""
        issues = []
        
        jd_files = self.list_jd_files()
        resume_files = self.list_resume_files()
        
        if len(jd_files) == 0:
            issues.append("No job description PDF files found in sample_data/jds_pdf/")
        
        if len(resume_files) == 0:
            issues.append("No resume PDF files found in sample_data/resumes_pdf/")
        
        # Check file sizes
        for file_path in jd_files + resume_files:
            if file_path.stat().st_size == 0:
                issues.append(f"Empty file: {file_path.name}")
        
        return issues

if __name__ == "__main__":
    manager = PDFDataManager()
    info = manager.get_sample_data_info()
    issues = manager.validate_pdf_files()
    
    print("=== PDF Sample Data Status ===")
    print(f"Job Descriptions: {info['job_descriptions']['count']} files")
    for file in info['job_descriptions']['files']:
        print(f"  - {file}")
    
    print(f"\nResumes: {info['resumes']['count']} files")
    for file in info['resumes']['files']:
        print(f"  - {file}")
    
    if issues:
        print(f"\n⚠️  Issues found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print(f"\n✅ All PDF files are ready!")
