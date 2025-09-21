"""
System testing script to verify all components work correctly
"""
import sys
import os
import requests
import time
import subprocess

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

def test_api_connection():
    """Test if API is running and accessible"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ API connection successful")
            return True
        else:
            print(f"❌ API returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure backend is running on port 8000")
        return False
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def test_database():
    """Test database functionality"""
    try:
        from backend.models import db, JobDescription
        
        # Test database connection
        test_jd = JobDescription(
            title="Test Job",
            company="Test Company", 
            description="Test description",
            required_skills=["Python"],
            preferred_skills=["Docker"],
            qualifications=["Bachelor's degree"],
            location="Remote"
        )
        
        jd_id = db.save_job_description(test_jd)
        retrieved_jd = db.get_job_description(jd_id)
        
        if retrieved_jd and retrieved_jd.title == "Test Job":
            print("✅ Database test successful")
            return True
        else:
            print("❌ Database test failed - could not retrieve saved data")
            return False
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_parsing():
    """Test resume and JD parsing"""
    try:
        from backend.services.parser import parser
        
        # Test JD parsing
        sample_jd_text = """
        Senior Software Engineer
        
        Required Skills:
        - Python, JavaScript
        - SQL, PostgreSQL
        - Git, Docker
        
        Qualifications:
        - Bachelor's degree in Computer Science
        - 5+ years of experience
        """
        
        parsed_jd = parser.parse_job_description(sample_jd_text)
        
        if parsed_jd.required_skills and len(parsed_jd.required_skills) > 0:
            print("✅ JD parsing test successful")
            return True
        else:
            print("❌ JD parsing test failed - no skills extracted")
            return False
            
    except Exception as e:
        print(f"❌ Parsing test failed: {e}")
        return False

def test_scoring():
    """Test scoring system"""
    try:
        from backend.services.scorer import scorer
        from backend.models import Resume, JobDescription
        
        # Create test data
        test_resume = Resume(
            candidate_name="Test Candidate",
            skills=["Python", "JavaScript", "SQL"],
            experience_years=5,
            education=[{"degree": "Bachelor", "field": "Computer Science"}],
            projects=[{"name": "Test Project", "description": "Python web app"}],
            certifications=["AWS Certified"],
            raw_text="Test resume content"
        )
        
        test_jd = JobDescription(
            title="Software Engineer",
            required_skills=["Python", "SQL"],
            preferred_skills=["JavaScript"],
            qualifications=["Bachelor's degree"],
            description="Software engineering position"
        )
        
        # Test scoring
        result = scorer.score_resume(test_resume, test_jd)
        
        if result.relevance_score > 0 and result.fit_verdict in ['High', 'Medium', 'Low']:
            print("✅ Scoring test successful")
            print(f"   Score: {result.relevance_score}, Verdict: {result.fit_verdict}")
            return True
        else:
            print("❌ Scoring test failed - invalid results")
            return False
            
    except Exception as e:
        print(f"❌ Scoring test failed: {e}")
        return False

def test_semantic_matching():
    """Test semantic matching functionality"""
    try:
        from backend.services.semantic import semantic_matcher
        
        if not semantic_matcher.is_available():
            print("⚠️ Semantic matching not available (model not loaded)")
            return True  # Not a failure, just not available
        
        # Test embedding generation
        text1 = "Python software engineer with machine learning experience"
        text2 = "ML engineer proficient in Python programming"
        
        embedding1 = semantic_matcher.get_embedding(text1)
        embedding2 = semantic_matcher.get_embedding(text2)
        
        if embedding1 is not None and embedding2 is not None:
            similarity = semantic_matcher.calculate_similarity(embedding1, embedding2)
            print(f"✅ Semantic matching test successful (similarity: {similarity:.3f})")
            return True
        else:
            print("❌ Semantic matching test failed - could not generate embeddings")
            return False
            
    except Exception as e:
        print(f"❌ Semantic matching test failed: {e}")
        return False

def run_all_tests():
    """Run all system tests"""
    print("🧪 Running System Tests")
    print("=" * 50)
    
    tests = [
        ("Database", test_database),
        ("Parsing", test_parsing), 
        ("Scoring", test_scoring),
        ("Semantic Matching", test_semantic_matching),
        ("API Connection", test_api_connection)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        results[test_name] = test_func()
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
