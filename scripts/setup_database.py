"""
Database setup and initialization script
"""
import sys
import os

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Now import from backend
from backend.models import db, JobDescription, Resume
import json

def setup_database():
    """Initialize database with schema"""
    print("🗄️ Setting up database...")
    
    try:
        # Initialize database (this will create tables)
        db.init_database()
        print("✅ Database schema created successfully!")
        
        # Test database connection
        test_jd = JobDescription(
            title="Test Position",
            company="Test Company",
            description="Test description",
            required_skills=["Python", "SQL"],
            preferred_skills=["Docker"],
            qualifications=["Bachelor's degree"],
            location="Remote"
        )
        
        jd_id = db.save_job_description(test_jd)
        retrieved_jd = db.get_job_description(jd_id)
        
        if retrieved_jd:
            print("✅ Database connection test successful!")
            print(f"   Created test job description with ID: {jd_id}")
            db.delete_job_description(jd_id)
            print("   Test data cleaned up")
        else:
            print("❌ Database connection test failed!")
            
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False
    
    return True


if __name__ == "__main__":
    print("🚀 Database Setup Script")
    print("=" * 50)
    
    success = setup_database()
    if success:
        print("\n✅ Database setup complete!")
        print("📁 Ready for PDF sample data loading")
        print("\nNext steps:")
        print("1. Place your PDF files in sample_data/jds_pdf/ and sample_data/resumes_pdf/")
        print("2. Run: python scripts/load_pdf_sample_data.py")
        print("3. Start the application with: ./run.sh")
    else:
        print("\n❌ Database setup failed!")
        sys.exit(1)
