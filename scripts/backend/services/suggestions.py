"""
LLM-powered improvement suggestions service
"""
import openai
import os
from typing import List, Dict, Optional
import logging
from dataclasses import dataclass

from ..models import Resume, JobDescription
from .scorer import ScoringResult

@dataclass
class ImprovementSuggestion:
    """Structure for improvement suggestions"""
    category: str  # skills, experience, education, projects, certifications
    priority: str  # high, medium, low
    suggestion: str
    specific_actions: List[str]

class SuggestionGenerator:
    """Generates improvement suggestions using LLM"""
    
    def __init__(self):
        # Initialize OpenAI client
        self.client = None
        self._setup_openai()
        
        # Fallback suggestions for when LLM is not available
        self.fallback_suggestions = {
            'skills': [
                "Consider learning the missing technical skills mentioned in the job requirements",
                "Add relevant programming languages or frameworks to your skillset",
                "Obtain certifications in key technologies mentioned in the job description"
            ],
            'projects': [
                "Create projects that demonstrate the required skills",
                "Contribute to open-source projects related to the job requirements",
                "Build a portfolio showcasing relevant technical abilities"
            ],
            'experience': [
                "Gain more experience in the required domain",
                "Take on projects that align with the job responsibilities",
                "Consider internships or freelance work in the relevant field"
            ],
            'education': [
                "Consider additional courses or certifications in relevant areas",
                "Pursue advanced degrees if required by the position",
                "Take online courses to fill knowledge gaps"
            ]
        }
    
    def _setup_openai(self):
        """Setup OpenAI client"""
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            try:
                self.client = openai.OpenAI(api_key=api_key)
                logging.info("OpenAI client initialized successfully")
            except Exception as e:
                logging.error(f"Failed to initialize OpenAI client: {e}")
                self.client = None
        else:
            logging.warning("OPENAI_API_KEY not found, using fallback suggestions")
    
    def generate_suggestions(self, resume: Resume, jd: JobDescription, 
                           scoring_result: ScoringResult) -> str:
        """
        Generate comprehensive improvement suggestions
        
        Args:
            resume: Parsed resume data
            jd: Job description data
            scoring_result: Scoring results with missing elements
            
        Returns:
            Formatted improvement suggestions
        """
        if self.client:
            return self._generate_llm_suggestions(resume, jd, scoring_result)
        else:
            return self._generate_fallback_suggestions(scoring_result)
    
    def _generate_llm_suggestions(self, resume: Resume, jd: JobDescription, 
                                scoring_result: ScoringResult) -> str:
        """Generate suggestions using LLM"""
        try:
            # Prepare context for LLM
            context = self._prepare_context(resume, jd, scoring_result)
            
            # Create prompt
            prompt = f"""
            As a career advisor, analyze this resume against the job description and provide specific, actionable improvement suggestions.

            CONTEXT:
            {context}

            SCORING RESULTS:
            - Overall Score: {scoring_result.relevance_score}/100
            - Fit Level: {scoring_result.fit_verdict}
            - Missing Skills: {', '.join(scoring_result.missing_skills) if scoring_result.missing_skills else 'None'}
            - Missing Certifications: {', '.join(scoring_result.missing_certifications) if scoring_result.missing_certifications else 'None'}

            Please provide:
            1. Top 3 priority improvements
            2. Specific skills to develop
            3. Project suggestions
            4. Certification recommendations
            5. Experience enhancement tips

            Format as clear, actionable bullet points. Be specific and practical.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert career advisor specializing in resume optimization and job matching."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logging.error(f"LLM suggestion generation failed: {e}")
            return self._generate_fallback_suggestions(scoring_result)
    
    def _prepare_context(self, resume: Resume, jd: JobDescription, 
                        scoring_result: ScoringResult) -> str:
        """Prepare context for LLM"""
        context = f"""
        JOB DESCRIPTION:
        Title: {jd.title}
        Company: {jd.company}
        Required Skills: {', '.join(jd.required_skills)}
        Preferred Skills: {', '.join(jd.preferred_skills)}
        Experience Required: {jd.experience_required}
        
        CANDIDATE PROFILE:
        Name: {resume.candidate_name}
        Current Skills: {', '.join(resume.skills)}
        Experience: {resume.experience_years} years
        Education: {len(resume.education)} degree(s)
        Projects: {len(resume.projects)} project(s)
        Certifications: {len(resume.certifications)} certification(s)
        """
        
        return context
    
    def _generate_fallback_suggestions(self, scoring_result: ScoringResult) -> str:
        """Generate fallback suggestions when LLM is not available"""
        suggestions = []
        
        # Priority improvements based on score
        if scoring_result.relevance_score < 50:
            suggestions.append("🔴 HIGH PRIORITY IMPROVEMENTS:")
        elif scoring_result.relevance_score < 75:
            suggestions.append("🟡 MEDIUM PRIORITY IMPROVEMENTS:")
        else:
            suggestions.append("🟢 MINOR IMPROVEMENTS:")
        
        # Skills suggestions
        if scoring_result.missing_skills:
            suggestions.append("\n📚 SKILLS TO DEVELOP:")
            for skill in scoring_result.missing_skills[:5]:
                suggestions.append(f"  • Learn {skill} through online courses or tutorials")
        
        # Project suggestions
        if scoring_result.missing_projects:
            suggestions.append("\n🛠️ PROJECT RECOMMENDATIONS:")
            for project in scoring_result.missing_projects[:3]:
                suggestions.append(f"  • Build {project.lower()}")
        
        # Certification suggestions
        if scoring_result.missing_certifications:
            suggestions.append("\n🏆 CERTIFICATION RECOMMENDATIONS:")
            for cert in scoring_result.missing_certifications[:3]:
                suggestions.append(f"  • Obtain {cert}")
        
        # General suggestions based on score
        if scoring_result.relevance_score < 30:
            suggestions.extend([
                "\n💡 GENERAL RECOMMENDATIONS:",
                "  • Consider gaining more relevant experience in this field",
                "  • Focus on building a strong portfolio of relevant projects",
                "  • Network with professionals in this industry"
            ])
        elif scoring_result.relevance_score < 60:
            suggestions.extend([
                "\n💡 GENERAL RECOMMENDATIONS:",
                "  • Highlight transferable skills more effectively",
                "  • Add more specific examples of relevant work",
                "  • Consider additional training in key areas"
            ])
        else:
            suggestions.extend([
                "\n💡 GENERAL RECOMMENDATIONS:",
                "  • Fine-tune your resume to better match job keywords",
                "  • Add quantifiable achievements to strengthen your profile",
                "  • Consider obtaining additional certifications for competitive edge"
            ])
        
        return "\n".join(suggestions)
    
    def generate_structured_suggestions(self, resume: Resume, jd: JobDescription, 
                                      scoring_result: ScoringResult) -> List[ImprovementSuggestion]:
        """Generate structured suggestions for programmatic use"""
        suggestions = []
        
        # Skills suggestions
        if scoring_result.missing_skills:
            priority = "high" if scoring_result.relevance_score < 50 else "medium"
            suggestions.append(ImprovementSuggestion(
                category="skills",
                priority=priority,
                suggestion=f"Develop missing technical skills: {', '.join(scoring_result.missing_skills[:3])}",
                specific_actions=[
                    f"Take online courses in {skill}" for skill in scoring_result.missing_skills[:3]
                ]
            ))
        
        # Project suggestions
        if scoring_result.missing_projects:
            suggestions.append(ImprovementSuggestion(
                category="projects",
                priority="medium",
                suggestion="Build projects demonstrating required skills",
                specific_actions=[
                    f"Create {project.lower()}" for project in scoring_result.missing_projects[:2]
                ]
            ))
        
        # Certification suggestions
        if scoring_result.missing_certifications:
            suggestions.append(ImprovementSuggestion(
                category="certifications",
                priority="low",
                suggestion="Obtain relevant certifications",
                specific_actions=[
                    f"Get certified in {cert}" for cert in scoring_result.missing_certifications[:2]
                ]
            ))
        
        return suggestions

# Global suggestion generator instance
suggestion_generator = SuggestionGenerator()
