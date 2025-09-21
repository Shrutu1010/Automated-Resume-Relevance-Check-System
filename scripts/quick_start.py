#!/usr/bin/env python3
"""
Quick start script for the Resume Relevance System
Handles the complete setup process including PDF data loading
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed!")
        print(f"Error: {e.stderr}")
        return False

def check_pdf_files():
    """Check if PDF files are present"""
    jds_dir = Path("sample_data/jds_pdf")
    resumes_dir = Path("sample_data/resumes_pdf")
    
    jd_files = list(jds_dir.glob("*.pdf")) if jds_dir.exists() else []
    resume_files = list(resumes_dir.glob("*.pdf")) if resumes_dir.exists() else []
    
    return len(jd_files), len(resume_files), jd_files, resume_files

def main():
    print("🚀 Resume Relevance System - Quick Start")
    print("=" * 50)
    
    # Check current directory
    if not os.path.exists("requirements.txt"):
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Step 1: Setup database
    if not run_command("python scripts/setup_database.py", "Setting up database"):
        sys.exit(1)
    
    # Step 2: Check for PDF files
    print("\n📁 Checking for PDF sample data...")
    jd_count, resume_count, jd_files, resume_files = check_pdf_files()
    
    print(f"   Job Descriptions found: {jd_count}")
    for jd in jd_files:
        print(f"     - {jd.name}")
    
    print(f"   Resumes found: {resume_count}")
    for resume in resume_files:
        print(f"     - {resume.name}")
    
    # Step 3: Load PDF data if available
    if jd_count > 0 or resume_count > 0:
        print(f"\n📊 Loading {jd_count + resume_count} PDF files into database...")
        if not run_command("python scripts/load_pdf_sample_data.py", "Loading PDF sample data"):
            print("⚠️  PDF loading failed, but system can still run")
    else:
        print("\n⚠️  No PDF files found!")
        print("Please add your PDF files:")
        print("   • Job Descriptions (2 files) → sample_data/jds_pdf/")
        print("   • Resumes (10 files) → sample_data/resumes_pdf/")
        print("   Then run: python scripts/load_pdf_sample_data.py")
    
    # Step 4: Final instructions
    print("\n" + "=" * 50)
    print("🎉 SETUP COMPLETE!")
    print("=" * 50)
    
    if jd_count == 0 and resume_count == 0:
        print("📁 TO ADD YOUR PDF FILES:")
        print("   1. Place 2 job description PDFs in: sample_data/jds_pdf/")
        print("   2. Place 10 resume PDFs in: sample_data/resumes_pdf/")
        print("   3. Run: python scripts/load_pdf_sample_data.py")
        print("")
    
    print("🚀 TO START THE SYSTEM:")
    print("   1. Backend API:")
    print("      cd backend && python main.py")
    print("")
    print("   2. Frontend Dashboard (in new terminal):")
    print("      streamlit run frontend/app.py")
    print("")
    print("   3. Open in browser:")
    print("      • API Documentation: http://localhost:8000/docs")
    print("      • Dashboard: http://localhost:8501")
    print("")
    print("📊 SAMPLE DATA STATUS:")
    print(f"   • Job Descriptions: {jd_count} loaded")
    print(f"   • Resumes: {resume_count} loaded")
    
    if jd_count >= 2 and resume_count >= 10:
        print("   ✅ Full sample dataset ready!")
    elif jd_count > 0 or resume_count > 0:
        print("   ⚠️  Partial sample dataset loaded")
    else:
        print("   ❌ No sample data loaded - add PDF files")

if __name__ == "__main__":
    main()
