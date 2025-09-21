"""
Resume scoring service combining hard matching and semantic similarity
"""
import numpy as np
from typing import List, Dict, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import fuzz, process
import re
import logging
from dataclasses import dataclass

from .semantic import SemanticMatcher
from ..models import Resume, JobDescription, Evaluation

@dataclass
class ScoringResult:
    """Result of resume scoring"""
    relevance_score: float  # 0-100
    fit_verdict: str  # High/Medium/Low
    hard_match_score: float
    semantic_match_score: float
    missing_skills: List[str]
    missing_projects: List[str]
    missing_certifications: List[str]
    skill_matches: Dict[str, float]
    education_match: float
    experience_match: float

class ResumeScorer:
    """Main scoring engine for resume relevance"""
    
    def __init__(self):
        self.semantic_matcher = SemanticMatcher()
        self.tfidf_vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_features=5000
        )
        
        # Scoring weights
        self.weights = {
            'hard_match': 0.5,
            'semantic_match': 0.5,
            'skills': 0.4,
            'education': 0.2,
            'experience': 0.2,
            'projects': 0.1,
            'certifications': 0.1
        }
        
        # Fit verdict thresholds
        self.thresholds = {
            'high': 75.0,
            'medium': 50.0,
            'low': 0.0
        }
    
    def calculate_hard_match_score(self, resume: Resume, jd: JobDescription) -> Dict[str, float]:
        """Calculate hard matching scores using keyword matching and fuzzy matching"""
        scores = {
            'skills': 0.0,
            'education': 0.0,
            'experience': 0.0,
            'certifications': 0.0,
            'projects': 0.0
        }
        
        # Skills matching
        skills_score, skill_matches = self._match_skills(resume.skills, jd.required_skills, jd.preferred_skills)
        scores['skills'] = skills_score
        
        # Education matching
        scores['education'] = self._match_education(resume.education, jd.qualifications)
        
        # Experience matching
        scores['experience'] = self._match_experience(resume.experience_years, jd.experience_required)
        
        # Certifications matching
        scores['certifications'] = self._match_certifications(resume.certifications, jd.required_skills + jd.preferred_skills)
        
        # Projects matching (based on skills mentioned in projects)
        scores['projects'] = self._match_projects(resume.projects, jd.required_skills + jd.preferred_skills)
        
        return scores, skill_matches
    
    def _match_skills(self, resume_skills: List[str], required_skills: List[str], 
                     preferred_skills: List[str]) -> Tuple[float, Dict[str, float]]:
        """Match skills using fuzzy matching"""
        if not resume_skills:
            return 0.0, {}
        
        all_jd_skills = required_skills + preferred_skills
        if not all_jd_skills:
            return 50.0, {}  # Neutral score if no skills specified
        
        skill_matches = {}
        total_score = 0.0
        
        # Check each JD skill against resume skills
        for jd_skill in all_jd_skills:
            best_match_score = 0.0
            best_match_skill = ""
            
            for resume_skill in resume_skills:
                # Exact match
                if jd_skill.lower() == resume_skill.lower():
                    match_score = 100.0
                else:
                    # Fuzzy match
                    match_score = fuzz.ratio(jd_skill.lower(), resume_skill.lower())
                
                if match_score > best_match_score:
                    best_match_score = match_score
                    best_match_skill = resume_skill
            
            # Consider match if score > 80
            if best_match_score > 80:
                skill_matches[jd_skill] = best_match_score / 100.0
                # Weight required skills higher
                weight = 1.5 if jd_skill in required_skills else 1.0
                total_score += (best_match_score / 100.0) * weight
        
        # Calculate percentage of matched skills
        total_possible = len(required_skills) * 1.5 + len(preferred_skills)
        if total_possible > 0:
            skills_score = min(100.0, (total_score / total_possible) * 100)
        else:
            skills_score = 0.0
        
        return skills_score, skill_matches
    
    def _match_education(self, resume_education: List[Dict[str, str]], 
                        jd_qualifications: List[str]) -> float:
        """Match education requirements"""
        if not resume_education:
            return 0.0
        
        if not jd_qualifications:
            return 50.0  # Neutral if no requirements
        
        education_text = " ".join([
            f"{edu.get('degree', '')} {edu.get('field', '')}" 
            for edu in resume_education
        ]).lower()
        
        matches = 0
        for qual in jd_qualifications:
            qual_lower = qual.lower()
            # Check for degree level matches
            if any(degree in qual_lower for degree in ['bachelor', 'master', 'phd', 'doctorate']):
                if any(degree in education_text for degree in ['bachelor', 'master', 'phd', 'doctorate']):
                    matches += 1
            # Check for field matches
            elif any(field in education_text for field in qual_lower.split()):
                matches += 1
        
        return min(100.0, (matches / len(jd_qualifications)) * 100)
    
    def _match_experience(self, resume_years: int, jd_experience: str) -> float:
        """Match experience requirements"""
        if not jd_experience or jd_experience == "Not specified":
            return 50.0  # Neutral if not specified
        
        # Extract years from JD requirement
        years_match = re.search(r'(\d+)', jd_experience)
        if not years_match:
            return 50.0
        
        required_years = int(years_match.group(1))
        
        if resume_years >= required_years:
            return 100.0
        elif resume_years >= required_years * 0.8:  # 80% of required
            return 80.0
        elif resume_years >= required_years * 0.6:  # 60% of required
            return 60.0
        else:
            return max(0.0, (resume_years / required_years) * 50)
    
    def _match_certifications(self, resume_certs: List[str], jd_skills: List[str]) -> float:
        """Match certifications with job requirements"""
        if not resume_certs:
            return 0.0
        
        if not jd_skills:
            return 50.0
        
        cert_text = " ".join(resume_certs).lower()
        matches = 0
        
        for skill in jd_skills:
            if any(cert_keyword in skill.lower() for cert_keyword in ['certified', 'certification']):
                if fuzz.partial_ratio(skill.lower(), cert_text) > 70:
                    matches += 1
        
        relevant_skills = [s for s in jd_skills if 'certified' in s.lower() or 'certification' in s.lower()]
        if relevant_skills:
            return min(100.0, (matches / len(relevant_skills)) * 100)
        else:
            return 50.0  # Bonus for having certs even if not required
    
    def _match_projects(self, resume_projects: List[Dict[str, str]], jd_skills: List[str]) -> float:
        """Match projects with job requirements based on skills mentioned"""
        if not resume_projects:
            return 0.0
        
        if not jd_skills:
            return 50.0
        
        project_text = " ".join([
            f"{proj.get('name', '')} {proj.get('description', '')}" 
            for proj in resume_projects
        ]).lower()
        
        matches = 0
        for skill in jd_skills:
            if fuzz.partial_ratio(skill.lower(), project_text) > 70:
                matches += 1
        
        return min(100.0, (matches / len(jd_skills)) * 100)
    
    def calculate_semantic_score(self, resume: Resume, jd: JobDescription) -> float:
        """Calculate semantic similarity using embeddings"""
        try:
            # Get embeddings for resume and JD
            resume_embedding = self.semantic_matcher.get_embedding(resume.raw_text)
            jd_embedding = self.semantic_matcher.get_embedding(jd.description)
            
            if resume_embedding is None or jd_embedding is None:
                logging.warning("Failed to get embeddings, falling back to TF-IDF")
                return self._calculate_tfidf_similarity(resume.raw_text, jd.description)
            
            # Calculate cosine similarity
            similarity = self.semantic_matcher.calculate_similarity(resume_embedding, jd_embedding)
            return similarity * 100  # Convert to 0-100 scale
            
        except Exception as e:
            logging.error(f"Semantic scoring failed: {e}")
            return self._calculate_tfidf_similarity(resume.raw_text, jd.description)
    
    def _calculate_tfidf_similarity(self, resume_text: str, jd_text: str) -> float:
        """Fallback TF-IDF similarity calculation"""
        try:
            documents = [resume_text, jd_text]
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(documents)
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return similarity * 100
        except Exception as e:
            logging.error(f"TF-IDF similarity failed: {e}")
            return 50.0  # Neutral score
    
    def identify_missing_elements(self, resume: Resume, jd: JobDescription, 
                                skill_matches: Dict[str, float]) -> Tuple[List[str], List[str], List[str]]:
        """Identify missing skills, projects, and certifications"""
        # Missing skills (required skills not matched well)
        missing_skills = []
        for skill in jd.required_skills:
            if skill not in skill_matches or skill_matches[skill] < 0.8:
                missing_skills.append(skill)
        
        # Missing project types (inferred from unmatched skills)
        missing_projects = []
        project_related_skills = [s for s in missing_skills if any(
            keyword in s.lower() for keyword in ['framework', 'library', 'tool', 'platform', 'system']
        )]
        if project_related_skills:
            missing_projects = [f"Projects using {skill}" for skill in project_related_skills[:3]]
        
        # Missing certifications (certification-related skills not matched)
        missing_certifications = []
        for skill in jd.required_skills + jd.preferred_skills:
            if any(cert_keyword in skill.lower() for cert_keyword in ['certified', 'certification']):
                if skill not in skill_matches or skill_matches[skill] < 0.8:
                    missing_certifications.append(skill)
        
        return missing_skills, missing_projects, missing_certifications
    
    def determine_fit_verdict(self, score: float) -> str:
        """Determine fit verdict based on score"""
        if score >= self.thresholds['high']:
            return 'High'
        elif score >= self.thresholds['medium']:
            return 'Medium'
        else:
            return 'Low'
    
    def score_resume(self, resume: Resume, jd: JobDescription) -> ScoringResult:
        """Main scoring function that combines all scoring methods"""
        try:
            # Calculate hard match scores
            hard_scores, skill_matches = self.calculate_hard_match_score(resume, jd)
            
            # Calculate weighted hard match score
            hard_match_score = (
                hard_scores['skills'] * self.weights['skills'] +
                hard_scores['education'] * self.weights['education'] +
                hard_scores['experience'] * self.weights['experience'] +
                hard_scores['projects'] * self.weights['projects'] +
                hard_scores['certifications'] * self.weights['certifications']
            ) / (self.weights['skills'] + self.weights['education'] + 
                self.weights['experience'] + self.weights['projects'] + 
                self.weights['certifications'])
            
            # Calculate semantic match score
            semantic_match_score = self.calculate_semantic_score(resume, jd)
            
            # Calculate final relevance score
            relevance_score = (
                hard_match_score * self.weights['hard_match'] +
                semantic_match_score * self.weights['semantic_match']
            )
            
            # Determine fit verdict
            fit_verdict = self.determine_fit_verdict(relevance_score)
            
            # Identify missing elements
            missing_skills, missing_projects, missing_certifications = self.identify_missing_elements(
                resume, jd, skill_matches
            )
            
            return ScoringResult(
                relevance_score=round(relevance_score, 2),
                fit_verdict=fit_verdict,
                hard_match_score=round(hard_match_score, 2),
                semantic_match_score=round(semantic_match_score, 2),
                missing_skills=missing_skills,
                missing_projects=missing_projects,
                missing_certifications=missing_certifications,
                skill_matches=skill_matches,
                education_match=hard_scores['education'],
                experience_match=hard_scores['experience']
            )
            
        except Exception as e:
            logging.error(f"Scoring failed: {e}")
            # Return default low score
            return ScoringResult(
                relevance_score=0.0,
                fit_verdict='Low',
                hard_match_score=0.0,
                semantic_match_score=0.0,
                missing_skills=jd.required_skills,
                missing_projects=[],
                missing_certifications=[],
                skill_matches={},
                education_match=0.0,
                experience_match=0.0
            )

# Global scorer instance
scorer = ResumeScorer()
