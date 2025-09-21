"""
Streamlit Dashboard for Resume Relevance Check System
"""
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import os
import sys

# Add backend to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from backend.models import db

# Configure Streamlit page
st.set_page_config(
    page_title="Resume Relevance Check System",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .high-score {
        color: #28a745;
        font-weight: bold;
    }
    .medium-score {
        color: #ffc107;
        font-weight: bold;
    }
    .low-score {
        color: #dc3545;
        font-weight: bold;
    }
    .sidebar-section {
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = "http://localhost:8000"

def make_api_request(endpoint, method="GET", data=None, files=None):
    """Make API request with error handling"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            if files:
                response = requests.post(url, data=data, files=files)
            else:
                response = requests.post(url, data=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to backend API. Please ensure the backend server is running on port 8000.")
        return None
    except Exception as e:
        st.error(f"Request failed: {str(e)}")
        return None

def get_score_color(score):
    """Get color class based on score"""
    if score >= 75:
        return "high-score"
    elif score >= 50:
        return "medium-score"
    else:
        return "low-score"

def main():
    """Main dashboard application"""
    
    # Header
    st.markdown('<h1 class="main-header">📄 Resume Relevance Check System</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Dashboard", "Job Descriptions", "Resumes", "Evaluations", "Analytics"]
    )
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "Job Descriptions":
        show_job_descriptions()
    elif page == "Resumes":
        show_resumes()
    elif page == "Evaluations":
        show_evaluations()
    elif page == "Analytics":
        show_analytics()

def show_dashboard():
    """Show main dashboard with overview"""
    st.header("📊 System Overview")
    
    # Get statistics
    stats = make_api_request("/api/stats/")
    
    if stats:
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Resumes", stats.get("total_resumes", 0))
        
        with col2:
            st.metric("Job Descriptions", stats.get("total_job_descriptions", 0))
        
        with col3:
            st.metric("Recent Resumes", stats.get("recent_resumes", 0))
        
        with col4:
            st.metric("Recent JDs", stats.get("recent_jds", 0))
    
    st.markdown("---")
    
    # Quick actions
    st.header("🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 Create Job Description", use_container_width=True):
            st.session_state.page = "Job Descriptions"
            st.rerun()
    
    with col2:
        if st.button("📄 Upload Resume", use_container_width=True):
            st.session_state.page = "Resumes"
            st.rerun()
    
    with col3:
        if st.button("🔍 View Evaluations", use_container_width=True):
            st.session_state.page = "Evaluations"
            st.rerun()
    
    # Recent activity
    st.header("📈 Recent Activity")
    
    # Get recent job descriptions
    jds = make_api_request("/api/job-descriptions/")
    if jds and jds.get("job_descriptions"):
        st.subheader("Recent Job Descriptions")
        recent_jds = jds["job_descriptions"][:5]
        
        for jd in recent_jds:
            with st.expander(f"{jd['title']} - {jd['company']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Location:** {jd['location']}")
                    st.write(f"**Required Skills:** {len(jd['required_skills'])} skills")
                with col2:
                    st.write(f"**Preferred Skills:** {len(jd['preferred_skills'])} skills")
                    st.write(f"**Created:** {jd['created_at']}")

def show_job_descriptions():
    """Show job descriptions management page"""
    st.header("📋 Job Descriptions Management")
    
    # Tabs for different actions
    tab1, tab2 = st.tabs(["📝 Create New", "📋 View All"])
    
    with tab1:
        st.subheader("Create New Job Description")
        
        with st.form("create_jd_form"):
            title = st.text_input("Job Title*", placeholder="e.g., Senior Software Engineer")
            company = st.text_input("Company", placeholder="e.g., Tech Corp Inc.")
            location = st.text_input("Location", placeholder="e.g., San Francisco, CA")
            description = st.text_area(
                "Job Description*", 
                height=300,
                placeholder="Paste the complete job description here..."
            )
            
            submitted = st.form_submit_button("Create Job Description")
            
            if submitted:
                if title and description:
                    data = {
                        "title": title,
                        "company": company,
                        "location": location,
                        "description": description
                    }
                    
                    result = make_api_request("/api/job-descriptions/", "POST", data)
                    
                    if result:
                        st.success(f"✅ Job description created successfully! ID: {result['id']}")
                        st.json(result["parsed_data"])
                else:
                    st.error("Please fill in required fields (Title and Description)")
    
    with tab2:
        st.subheader("All Job Descriptions")
        
        jds = make_api_request("/api/job-descriptions/")
        
        if jds and jds.get("job_descriptions"):
            # Search and filter
            search_term = st.text_input("🔍 Search job descriptions", placeholder="Search by title, company, or skills...")
            
            jd_list = jds["job_descriptions"]
            
            # Filter based on search
            if search_term:
                jd_list = [
                    jd for jd in jd_list 
                    if search_term.lower() in jd["title"].lower() 
                    or search_term.lower() in jd["company"].lower()
                    or any(search_term.lower() in skill.lower() for skill in jd["required_skills"] + jd["preferred_skills"])
                ]
            
            # Display job descriptions
            for jd in jd_list:
                with st.expander(f"🏢 {jd['title']} - {jd['company']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**ID:** {jd['id']}")
                        st.write(f"**Location:** {jd['location']}")
                        st.write(f"**Created:** {jd['created_at']}")
                    
                    with col2:
                        st.write(f"**Required Skills:** {len(jd['required_skills'])}")
                        st.write(f"**Preferred Skills:** {len(jd['preferred_skills'])}")
                    
                    if jd['required_skills']:
                        st.write("**Required Skills:**")
                        st.write(", ".join(jd['required_skills']))
                    
                    if jd['preferred_skills']:
                        st.write("**Preferred Skills:**")
                        st.write(", ".join(jd['preferred_skills']))
                    
                    # Action buttons
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"📊 View Evaluations", key=f"eval_{jd['id']}"):
                            st.session_state.selected_jd = jd['id']
                            st.session_state.page = "Evaluations"
                            st.rerun()
                    
                    with col2:
                        if st.button(f"🔍 Evaluate Resumes", key=f"evaluate_{jd['id']}"):
                            st.session_state.selected_jd = jd['id']
                            show_batch_evaluation(jd['id'])
        else:
            st.info("No job descriptions found. Create your first job description!")

def show_resumes():
    """Show resumes management page"""
    st.header("📄 Resumes Management")
    
    # Tabs for different actions
    tab1, tab2 = st.tabs(["📤 Upload New", "📄 View All"])
    
    with tab1:
        st.subheader("Upload New Resume")
        
        uploaded_file = st.file_uploader(
            "Choose a resume file",
            type=['pdf', 'docx', 'doc'],
            help="Upload PDF or DOCX files only"
        )
        
        if uploaded_file is not None:
            if st.button("Upload and Parse Resume"):
                files = {"file": uploaded_file}
                result = make_api_request("/api/resumes/", "POST", files=files)
                
                if result:
                    st.success(f"✅ Resume uploaded successfully! ID: {result['id']}")
                    
                    # Display parsed information
                    st.subheader("Parsed Information")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Candidate:** {result['parsed_data']['candidate_name']}")
                        st.write(f"**Email:** {result['parsed_data']['email']}")
                        st.write(f"**Phone:** {result['parsed_data']['phone']}")
                    
                    with col2:
                        st.write(f"**Location:** {result['parsed_data']['location']}")
                        st.write(f"**Experience:** {result['parsed_data']['experience_years']} years")
                        st.write(f"**Skills Found:** {len(result['parsed_data']['skills'])}")
                    
                    if result['parsed_data']['skills']:
                        st.write("**Skills:**")
                        st.write(", ".join(result['parsed_data']['skills']))
    
    with tab2:
        st.subheader("All Resumes")
        
        resumes = make_api_request("/api/resumes/")
        
        if resumes and resumes.get("resumes"):
            # Search and filter
            search_term = st.text_input("🔍 Search resumes", placeholder="Search by name, email, or location...")
            
            resume_list = resumes["resumes"]
            
            # Filter based on search
            if search_term:
                resume_list = [
                    resume for resume in resume_list 
                    if search_term.lower() in resume["candidate_name"].lower() 
                    or search_term.lower() in resume["email"].lower()
                    or search_term.lower() in resume["location"].lower()
                ]
            
            # Display resumes in a table
            df = pd.DataFrame(resume_list)
            df = df[['id', 'candidate_name', 'email', 'location', 'skills_count', 'experience_years', 'created_at']]
            df.columns = ['ID', 'Name', 'Email', 'Location', 'Skills', 'Experience', 'Uploaded']
            
            st.dataframe(df, use_container_width=True)
            
            # Detailed view
            st.subheader("Detailed View")
            selected_resume_id = st.selectbox("Select a resume to view details", 
                                            options=[r['id'] for r in resume_list],
                                            format_func=lambda x: next(r['candidate_name'] for r in resume_list if r['id'] == x))
            
            if selected_resume_id:
                resume_detail = make_api_request(f"/api/resumes/{selected_resume_id}")
                
                if resume_detail:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Name:** {resume_detail['candidate_name']}")
                        st.write(f"**Email:** {resume_detail['email']}")
                        st.write(f"**Phone:** {resume_detail['phone']}")
                        st.write(f"**Location:** {resume_detail['location']}")
                        st.write(f"**Experience:** {resume_detail['experience_years']} years")
                    
                    with col2:
                        st.write(f"**Skills:** {len(resume_detail['skills'])}")
                        st.write(f"**Projects:** {len(resume_detail['projects'])}")
                        st.write(f"**Education:** {len(resume_detail['education'])}")
                        st.write(f"**Certifications:** {len(resume_detail['certifications'])}")
                    
                    # Skills
                    if resume_detail['skills']:
                        st.write("**Skills:**")
                        st.write(", ".join(resume_detail['skills']))
                    
                    # Projects
                    if resume_detail['projects']:
                        st.write("**Projects:**")
                        for project in resume_detail['projects']:
                            st.write(f"• {project.get('name', 'Unnamed Project')}: {project.get('description', 'No description')}")
        else:
            st.info("No resumes found. Upload your first resume!")

def show_evaluations():
    """Show evaluations page"""
    st.header("🔍 Resume Evaluations")
    
    # Get job descriptions for selection
    jds = make_api_request("/api/job-descriptions/")
    
    if not jds or not jds.get("job_descriptions"):
        st.warning("No job descriptions found. Please create a job description first.")
        return
    
    # Job description selection
    jd_options = {jd['id']: f"{jd['title']} - {jd['company']}" for jd in jds["job_descriptions"]}
    selected_jd_id = st.selectbox("Select Job Description", options=list(jd_options.keys()), 
                                 format_func=lambda x: jd_options[x])
    
    if selected_jd_id:
        # Tabs for different evaluation views
        tab1, tab2, tab3 = st.tabs(["📊 Results Overview", "🔍 Individual Evaluation", "📈 Batch Evaluation"])
        
        with tab1:
            show_evaluation_results(selected_jd_id)
        
        with tab2:
            show_individual_evaluation(selected_jd_id)
        
        with tab3:
            show_batch_evaluation(selected_jd_id)

def show_evaluation_results(jd_id):
    """Show evaluation results for a job description"""
    st.subheader("Evaluation Results")
    
    evaluations = make_api_request(f"/api/evaluations/jd/{jd_id}")
    
    if evaluations and evaluations.get("evaluations"):
        eval_list = evaluations["evaluations"]
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Evaluated", len(eval_list))
        
        with col2:
            high_fit = len([e for e in eval_list if e['fit_verdict'] == 'High'])
            st.metric("High Fit", high_fit)
        
        with col3:
            medium_fit = len([e for e in eval_list if e['fit_verdict'] == 'Medium'])
            st.metric("Medium Fit", medium_fit)
        
        with col4:
            avg_score = sum(e['relevance_score'] for e in eval_list) / len(eval_list)
            st.metric("Average Score", f"{avg_score:.1f}")
        
        # Score distribution chart
        scores = [e['relevance_score'] for e in eval_list]
        fig = px.histogram(x=scores, nbins=20, title="Score Distribution")
        fig.update_xaxis(title="Relevance Score")
        fig.update_yaxis(title="Number of Candidates")
        st.plotly_chart(fig, use_container_width=True)
        
        # Top candidates table
        st.subheader("Top Candidates")
        
        # Sort by score
        sorted_evals = sorted(eval_list, key=lambda x: x['relevance_score'], reverse=True)
        
        for i, eval_data in enumerate(sorted_evals[:10]):  # Top 10
            with st.expander(f"#{i+1} {eval_data['candidate_name']} - Score: {eval_data['relevance_score']:.1f}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Email:** {eval_data['candidate_email']}")
                    st.write(f"**Location:** {eval_data['candidate_location']}")
                    st.write(f"**Fit Verdict:** {eval_data['fit_verdict']}")
                
                with col2:
                    st.write(f"**Hard Match:** {eval_data['hard_match_score']:.1f}")
                    st.write(f"**Semantic Match:** {eval_data['semantic_match_score']:.1f}")
                
                if eval_data['missing_skills']:
                    st.write("**Missing Skills:**")
                    st.write(", ".join(eval_data['missing_skills']))
                
                if eval_data['improvement_suggestions']:
                    st.write("**Improvement Suggestions:**")
                    st.write(eval_data['improvement_suggestions'])
    else:
        st.info("No evaluations found for this job description. Run some evaluations first!")

def show_individual_evaluation(jd_id):
    """Show individual resume evaluation interface"""
    st.subheader("Individual Resume Evaluation")
    
    # Get resumes
    resumes = make_api_request("/api/resumes/")
    
    if not resumes or not resumes.get("resumes"):
        st.warning("No resumes found. Please upload some resumes first.")
        return
    
    # Resume selection
    resume_options = {r['id']: f"{r['candidate_name']} ({r['email']})" for r in resumes["resumes"]}
    selected_resume_id = st.selectbox("Select Resume to Evaluate", 
                                     options=list(resume_options.keys()),
                                     format_func=lambda x: resume_options[x])
    
    if st.button("🔍 Evaluate Resume"):
        data = {"resume_id": selected_resume_id, "jd_id": jd_id}
        result = make_api_request("/api/evaluate/", "POST", data)
        
        if result:
            st.success("✅ Evaluation completed!")
            
            # Display results
            col1, col2, col3 = st.columns(3)
            
            with col1:
                score_color = get_score_color(result['relevance_score'])
                st.markdown(f"**Relevance Score:** <span class='{score_color}'>{result['relevance_score']:.1f}/100</span>", 
                           unsafe_allow_html=True)
            
            with col2:
                st.write(f"**Fit Verdict:** {result['fit_verdict']}")
            
            with col3:
                st.write(f"**Candidate:** {result['candidate_name']}")
            
            # Detailed scores
            st.subheader("Detailed Scores")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Hard Match Score:** {result['hard_match_score']:.1f}")
            
            with col2:
                st.write(f"**Semantic Match Score:** {result['semantic_match_score']:.1f}")
            
            # Missing elements
            if result['missing_skills']:
                st.subheader("Missing Skills")
                st.write(", ".join(result['missing_skills']))
            
            if result['missing_projects']:
                st.subheader("Missing Project Types")
                st.write(", ".join(result['missing_projects']))
            
            if result['missing_certifications']:
                st.subheader("Missing Certifications")
                st.write(", ".join(result['missing_certifications']))
            
            # Improvement suggestions
            if result['improvement_suggestions']:
                st.subheader("Improvement Suggestions")
                st.write(result['improvement_suggestions'])

def show_batch_evaluation(jd_id):
    """Show batch evaluation interface"""
    st.subheader("Batch Resume Evaluation")
    
    # Get resumes
    resumes = make_api_request("/api/resumes/")
    
    if not resumes or not resumes.get("resumes"):
        st.warning("No resumes found. Please upload some resumes first.")
        return
    
    # Resume selection
    st.write("Select resumes to evaluate:")
    resume_list = resumes["resumes"]
    
    selected_resumes = []
    for resume in resume_list:
        if st.checkbox(f"{resume['candidate_name']} ({resume['email']})", key=f"batch_{resume['id']}"):
            selected_resumes.append(resume['id'])
    
    if st.button("🚀 Evaluate Selected Resumes") and selected_resumes:
        resume_ids_str = ",".join(map(str, selected_resumes))
        data = {"jd_id": jd_id, "resume_ids": resume_ids_str}
        
        with st.spinner("Evaluating resumes..."):
            result = make_api_request("/api/evaluate-batch/", "POST", data)
        
        if result:
            st.success(f"✅ Evaluated {result['total_evaluated']} resumes!")
            
            # Display results
            st.subheader("Batch Evaluation Results")
            
            results_df = pd.DataFrame(result['results'])
            results_df = results_df.sort_values('relevance_score', ascending=False)
            
            # Add rank
            results_df['rank'] = range(1, len(results_df) + 1)
            
            # Display table
            st.dataframe(results_df[['rank', 'candidate_name', 'relevance_score', 'fit_verdict']], 
                        use_container_width=True)
            
            # Score distribution
            fig = px.bar(results_df, x='candidate_name', y='relevance_score', 
                        title="Candidate Scores", color='fit_verdict')
            fig.update_xaxis(title="Candidates")
            fig.update_yaxis(title="Relevance Score")
            st.plotly_chart(fig, use_container_width=True)

def show_analytics():
    """Show analytics and insights page"""
    st.header("📈 Analytics & Insights")
    
    # Get data for analytics
    jds = make_api_request("/api/job-descriptions/")
    resumes = make_api_request("/api/resumes/")
    
    if not jds or not resumes:
        st.warning("Insufficient data for analytics. Please add job descriptions and resumes.")
        return
    
    # Skills analysis
    st.subheader("Skills Analysis")
    
    # Most common skills in job descriptions
    all_jd_skills = []
    for jd in jds.get("job_descriptions", []):
        all_jd_skills.extend(jd.get("required_skills", []))
        all_jd_skills.extend(jd.get("preferred_skills", []))
    
    if all_jd_skills:
        skill_counts = pd.Series(all_jd_skills).value_counts().head(10)
        fig = px.bar(x=skill_counts.values, y=skill_counts.index, orientation='h',
                    title="Most Requested Skills in Job Descriptions")
        fig.update_yaxis(title="Skills")
        fig.update_xaxis(title="Frequency")
        st.plotly_chart(fig, use_container_width=True)
    
    # Resume statistics
    st.subheader("Resume Statistics")
    
    if resumes.get("resumes"):
        resume_data = resumes["resumes"]
        
        # Experience distribution
        experience_data = [r.get("experience_years", 0) for r in resume_data]
        fig = px.histogram(x=experience_data, nbins=10, title="Experience Distribution")
        fig.update_xaxis(title="Years of Experience")
        fig.update_yaxis(title="Number of Candidates")
        st.plotly_chart(fig, use_container_width=True)
        
        # Skills count distribution
        skills_count_data = [r.get("skills_count", 0) for r in resume_data]
        fig = px.histogram(x=skills_count_data, nbins=15, title="Skills Count Distribution")
        fig.update_xaxis(title="Number of Skills")
        fig.update_yaxis(title="Number of Candidates")
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
