"""
Resume and Job Description parsing service
Extracts structured information from documents
"""
import re
import json
import spacy
from typing import List, Dict, Optional, Tuple
import PyMuPDF  # fitz
import pdfplumber
from docx import Document
import docx2txt
from dataclasses import dataclass
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
import logging

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# Load spaCy model (install with: python -m spacy download en_core_web_sm)
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Please install spaCy English model: python -m spacy download en_core_web_sm")
    nlp = None

@dataclass
class ParsedResume:
    """Structured resume data"""
    raw_text: str
    candidate_name: str
    email: str
    phone: str
    location: str
    skills: List[str]
    projects: List[Dict[str, str]]
    education: List[Dict[str, str]]
    certifications: List[str]
    experience_years: int
    work_experience: List[Dict[str, str]]

@dataclass
class ParsedJobDescription:
    """Structured job description data"""
    raw_text: str
    title: str
    company: str
    description: str
    required_skills: List[str]
    preferred_skills: List[str]
    qualifications: List[str]
    location: str
    experience_required: str

class DocumentParser:
    """Main document parsing class"""
    
    def __init__(self):
        self.skills_keywords = self._load_skills_keywords()
        self.education_keywords = self._load_education_keywords()
        self.certification_keywords = self._load_certification_keywords()
    
    def _load_skills_keywords(self) -> List[str]:
        """Load common technical skills for extraction"""
        return [
            # Programming Languages
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust',
            'swift', 'kotlin', 'scala', 'r', 'matlab', 'sql', 'html', 'css', 'bash', 'powershell',
            
            # Frameworks & Libraries
            'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 'spring', 'laravel',
            'rails', 'asp.net', 'jquery', 'bootstrap', 'tailwind', 'tensorflow', 'pytorch', 'keras',
            'pandas', 'numpy', 'scikit-learn', 'opencv', 'matplotlib', 'seaborn',
            
            # Databases
            'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'cassandra', 'oracle',
            'sqlite', 'dynamodb', 'firebase', 'supabase',
            
            # Cloud & DevOps
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'gitlab', 'github actions',
            'terraform', 'ansible', 'chef', 'puppet', 'vagrant', 'nginx', 'apache',
            
            # Tools & Technologies
            'git', 'jira', 'confluence', 'slack', 'figma', 'sketch', 'photoshop', 'illustrator',
            'tableau', 'power bi', 'excel', 'google analytics', 'salesforce', 'hubspot',
            
            # Methodologies
            'agile', 'scrum', 'kanban', 'devops', 'ci/cd', 'tdd', 'bdd', 'microservices',
            'rest api', 'graphql', 'soap', 'oauth', 'jwt', 'ssl', 'https',
            
            # Soft Skills
            'leadership', 'communication', 'teamwork', 'problem solving', 'analytical thinking',
            'project management', 'time management', 'adaptability', 'creativity', 'innovation'
        ]
    
    def _load_education_keywords(self) -> List[str]:
        """Load education-related keywords"""
        return [
            'bachelor', 'master', 'phd', 'doctorate', 'diploma', 'certificate', 'degree',
            'computer science', 'software engineering', 'information technology', 'data science',
            'machine learning', 'artificial intelligence', 'cybersecurity', 'business administration',
            'engineering', 'mathematics', 'statistics', 'physics', 'chemistry', 'biology'
        ]
    
    def _load_certification_keywords(self) -> List[str]:
        """Load certification keywords"""
        return [
            'aws certified', 'azure certified', 'google cloud certified', 'cisco certified',
            'microsoft certified', 'oracle certified', 'salesforce certified', 'pmp',
            'scrum master', 'product owner', 'itil', 'six sigma', 'comptia', 'cissp',
            'ceh', 'cisa', 'cism', 'prince2', 'togaf', 'cobit'
        ]
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF using multiple methods"""
        text = ""
        
        # Try PyMuPDF first
        try:
            doc = PyMuPDF.open(file_path)
            for page in doc:
                text += page.get_text()
            doc.close()
        except Exception as e:
            logging.warning(f"PyMuPDF failed: {e}")
        
        # Fallback to pdfplumber if PyMuPDF fails or returns empty
        if not text.strip():
            try:
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
            except Exception as e:
                logging.warning(f"pdfplumber failed: {e}")
        
        return text.strip()
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            # Try python-docx first
            doc = Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            
            # Fallback to docx2txt if needed
            if not text.strip():
                text = docx2txt.process(file_path)
            
            return text.strip()
        except Exception as e:
            logging.error(f"Failed to extract text from DOCX: {e}")
            return ""
    
    def extract_contact_info(self, text: str) -> Tuple[str, str, str, str]:
        """Extract name, email, phone, and location from text"""
        # Email extraction
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        email = emails[0] if emails else ""
        
        # Phone extraction
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?$$?\d{3}$$?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, text)
        phone = phones[0] if phones else ""
        if isinstance(phone, tuple):
            phone = ''.join(phone)
        
        # Name extraction (usually first line or near contact info)
        lines = text.split('\n')
        name = ""
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if line and not re.search(r'[@\d]', line) and len(line.split()) <= 4:
                # Likely a name if no email/numbers and reasonable length
                if not any(keyword in line.lower() for keyword in ['resume', 'cv', 'curriculum']):
                    name = line
                    break
        
        # Location extraction
        location_patterns = [
            r'([A-Za-z\s]+,\s*[A-Z]{2})',  # City, State
            r'([A-Za-z\s]+,\s*[A-Za-z\s]+,\s*[A-Z]{2})',  # City, County, State
            r'([A-Za-z\s]+,\s*\d{5})',  # City, ZIP
        ]
        location = ""
        for pattern in location_patterns:
            matches = re.findall(pattern, text)
            if matches:
                location = matches[0]
                break
        
        return name, email, phone, location
    
    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from text using keyword matching and NLP"""
        text_lower = text.lower()
        found_skills = []
        
        # Keyword-based extraction
        for skill in self.skills_keywords:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        # NLP-based extraction for additional skills
        if nlp:
            doc = nlp(text)
            for ent in doc.ents:
                if ent.label_ in ['ORG', 'PRODUCT'] and len(ent.text) > 2:
                    # Check if it might be a technology/skill
                    if any(keyword in ent.text.lower() for keyword in ['tech', 'soft', 'program', 'develop']):
                        found_skills.append(ent.text)
        
        # Remove duplicates and return
        return list(set(found_skills))
    
    def extract_projects(self, text: str) -> List[Dict[str, str]]:
        """Extract project information from text"""
        projects = []
        
        # Look for project sections
        project_patterns = [
            r'(?i)projects?\s*:?\s*\n(.*?)(?=\n\s*(?:education|experience|skills|certifications|$))',
            r'(?i)personal\s+projects?\s*:?\s*\n(.*?)(?=\n\s*(?:education|experience|skills|certifications|$))',
            r'(?i)academic\s+projects?\s*:?\s*\n(.*?)(?=\n\s*(?:education|experience|skills|certifications|$))'
        ]
        
        for pattern in project_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                # Split projects by bullet points or line breaks
                project_lines = [line.strip() for line in match.split('\n') if line.strip()]
                
                for line in project_lines:
                    if len(line) > 20:  # Reasonable project description length
                        # Try to extract project name and description
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            projects.append({
                                'name': parts[0].strip(),
                                'description': parts[1].strip()
                            })
                        else:
                            projects.append({
                                'name': line[:50] + '...' if len(line) > 50 else line,
                                'description': line
                            })
        
        return projects[:5]  # Limit to 5 projects
    
    def extract_education(self, text: str) -> List[Dict[str, str]]:
        """Extract education information from text"""
        education = []
        
        # Look for education section
        education_pattern = r'(?i)education\s*:?\s*\n(.*?)(?=\n\s*(?:experience|projects|skills|certifications|$))'
        matches = re.findall(education_pattern, text, re.DOTALL)
        
        for match in matches:
            lines = [line.strip() for line in match.split('\n') if line.strip()]
            
            for line in lines:
                # Look for degree patterns
                degree_patterns = [
                    r'(bachelor|master|phd|doctorate|diploma|certificate).*?(?:in|of)\s+([^,\n]+)',
                    r'(b\.?s\.?|m\.?s\.?|ph\.?d\.?|b\.?a\.?|m\.?a\.?).*?(?:in|of)?\s+([^,\n]+)',
                ]
                
                for pattern in degree_patterns:
                    degree_match = re.search(pattern, line, re.IGNORECASE)
                    if degree_match:
                        education.append({
                            'degree': degree_match.group(1),
                            'field': degree_match.group(2).strip(),
                            'institution': line  # Full line as institution info
                        })
                        break
        
        return education[:3]  # Limit to 3 education entries
    
    def extract_certifications(self, text: str) -> List[str]:
        """Extract certifications from text"""
        text_lower = text.lower()
        certifications = []
        
        # Keyword-based extraction
        for cert in self.certification_keywords:
            if cert.lower() in text_lower:
                certifications.append(cert)
        
        # Look for certification section
        cert_pattern = r'(?i)certifications?\s*:?\s*\n(.*?)(?=\n\s*(?:education|experience|projects|skills|$))'
        matches = re.findall(cert_pattern, text, re.DOTALL)
        
        for match in matches:
            lines = [line.strip() for line in match.split('\n') if line.strip()]
            for line in lines:
                if len(line) > 5 and len(line) < 100:  # Reasonable cert name length
                    certifications.append(line)
        
        return list(set(certifications))[:10]  # Remove duplicates, limit to 10
    
    def extract_experience_years(self, text: str) -> int:
        """Extract years of experience from text"""
        # Look for experience patterns
        experience_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'experience\s*:?\s*(\d+)\+?\s*years?',
            r'(\d+)\+?\s*years?\s*in\s*(?:software|development|programming|engineering)',
        ]
        
        years = 0
        for pattern in experience_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    years = max(years, int(matches[0]))
                except ValueError:
                    continue
        
        return years
    
    def parse_resume(self, file_path: str, filename: str) -> ParsedResume:
        """Parse resume file and extract structured information"""
        # Extract text based on file type
        if filename.lower().endswith('.pdf'):
            text = self.extract_text_from_pdf(file_path)
        elif filename.lower().endswith(('.docx', '.doc')):
            text = self.extract_text_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {filename}")
        
        if not text:
            raise ValueError("Could not extract text from file")
        
        # Extract structured information
        name, email, phone, location = self.extract_contact_info(text)
        skills = self.extract_skills(text)
        projects = self.extract_projects(text)
        education = self.extract_education(text)
        certifications = self.extract_certifications(text)
        experience_years = self.extract_experience_years(text)
        
        return ParsedResume(
            raw_text=text,
            candidate_name=name,
            email=email,
            phone=phone,
            location=location,
            skills=skills,
            projects=projects,
            education=education,
            certifications=certifications,
            experience_years=experience_years,
            work_experience=[]  # Could be enhanced further
        )
    
    def parse_job_description(self, text: str) -> ParsedJobDescription:
        """Parse job description text and extract structured information"""
        # Extract job title (usually first line or prominent)
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        title = lines[0] if lines else "Unknown Position"
        
        # Extract company name (look for common patterns)
        company = ""
        company_patterns = [
            r'(?i)company\s*:?\s*([^\n]+)',
            r'(?i)employer\s*:?\s*([^\n]+)',
            r'(?i)organization\s*:?\s*([^\n]+)',
        ]
        
        for pattern in company_patterns:
            match = re.search(pattern, text)
            if match:
                company = match.group(1).strip()
                break
        
        # Extract location
        location_patterns = [
            r'(?i)location\s*:?\s*([^\n]+)',
            r'(?i)based\s+in\s+([^\n,]+)',
            r'([A-Za-z\s]+,\s*[A-Z]{2})',  # City, State format
        ]
        
        location = ""
        for pattern in location_patterns:
            matches = re.findall(pattern, text)
            if matches:
                location = matches[0]
                break
        
        # Extract skills and requirements
        required_skills = []
        preferred_skills = []
        qualifications = []
        
        # Look for requirements sections
        req_patterns = [
            r'(?i)(?:required|must\s+have|essential).*?(?:skills|requirements|qualifications)\s*:?\s*\n(.*?)(?=\n\s*(?:preferred|nice|optional|responsibilities|duties|$))',
            r'(?i)requirements\s*:?\s*\n(.*?)(?=\n\s*(?:preferred|nice|optional|responsibilities|duties|$))',
        ]
        
        for pattern in req_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                # Extract skills from requirements
                skills_in_req = self.extract_skills(match)
                required_skills.extend(skills_in_req)
        
        # Look for preferred/nice-to-have sections
        pref_patterns = [
            r'(?i)(?:preferred|nice\s+to\s+have|optional|plus).*?(?:skills|requirements|qualifications)\s*:?\s*\n(.*?)(?=\n\s*(?:responsibilities|duties|$))',
        ]
        
        for pattern in pref_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                skills_in_pref = self.extract_skills(match)
                preferred_skills.extend(skills_in_pref)
        
        # Extract qualifications
        qual_patterns = [
            r'(?i)qualifications\s*:?\s*\n(.*?)(?=\n\s*(?:responsibilities|duties|skills|$))',
            r'(?i)education\s*:?\s*\n(.*?)(?=\n\s*(?:responsibilities|duties|skills|$))',
        ]
        
        for pattern in qual_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                qual_lines = [line.strip() for line in match.split('\n') if line.strip()]
                qualifications.extend(qual_lines[:5])  # Limit qualifications
        
        # Extract experience requirements
        exp_pattern = r'(\d+)\+?\s*years?\s*(?:of\s*)?(?:experience|exp)'
        exp_matches = re.findall(exp_pattern, text, re.IGNORECASE)
        experience_required = f"{exp_matches[0]}+ years" if exp_matches else "Not specified"
        
        return ParsedJobDescription(
            raw_text=text,
            title=title,
            company=company,
            description=text,
            required_skills=list(set(required_skills)),
            preferred_skills=list(set(preferred_skills)),
            qualifications=qualifications,
            location=location,
            experience_required=experience_required
        )

# Global parser instance
parser = DocumentParser()
