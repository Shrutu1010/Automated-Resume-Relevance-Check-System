"""
Generate sample resume text for testing
"""

sample_resumes = [
    {
        "filename": "john_doe_senior_engineer.txt",
        "content": """
JOHN DOE
Senior Software Engineer
Email: john.doe@email.com
Phone: (555) 123-4567
Location: San Francisco, CA

PROFESSIONAL SUMMARY
Experienced Senior Software Engineer with 6+ years of expertise in full-stack development, 
specializing in Python, JavaScript, and cloud technologies. Proven track record of leading 
development teams and delivering scalable web applications.

TECHNICAL SKILLS
Programming Languages: Python, JavaScript, TypeScript, Java, SQL
Frontend: React.js, Vue.js, HTML5, CSS3, Bootstrap
Backend: Django, Flask, Node.js, Express.js
Databases: PostgreSQL, MySQL, MongoDB, Redis
Cloud & DevOps: AWS (EC2, S3, RDS), Docker, Kubernetes, Jenkins
Tools: Git, JIRA, Confluence, Postman

PROFESSIONAL EXPERIENCE

Senior Software Engineer | TechStart Inc. | 2020 - Present
• Led development of microservices architecture serving 100K+ daily users
• Implemented CI/CD pipelines reducing deployment time by 60%
• Mentored 3 junior developers and conducted code reviews
• Designed and built RESTful APIs using Python Django and PostgreSQL
• Collaborated with product team to deliver features using Agile methodologies

Software Engineer | WebSolutions Co. | 2018 - 2020
• Developed responsive web applications using React.js and Node.js
• Optimized database queries improving application performance by 40%
• Integrated third-party APIs and payment gateways
• Participated in daily standups and sprint planning sessions

PROJECTS
E-commerce Platform
• Built full-stack e-commerce application using React, Node.js, and PostgreSQL
• Implemented user authentication, payment processing, and inventory management
• Deployed on AWS with Docker containerization

Data Analytics Dashboard
• Created real-time analytics dashboard using Python, Flask, and Chart.js
• Integrated with multiple data sources and APIs
• Implemented caching layer with Redis for improved performance

EDUCATION
Bachelor of Science in Computer Science
University of California, Berkeley | 2018

CERTIFICATIONS
• AWS Certified Solutions Architect - Associate
• Certified Scrum Master (CSM)
"""
    },
    {
        "filename": "sarah_chen_data_scientist.txt",
        "content": """
SARAH CHEN
Data Scientist
Email: sarah.chen@email.com
Phone: (555) 987-6543
Location: New York, NY

PROFESSIONAL SUMMARY
Data Scientist with 4+ years of experience in machine learning, statistical analysis, 
and data visualization. Expertise in Python, R, and cloud platforms with a strong 
background in predictive modeling and business intelligence.

TECHNICAL SKILLS
Programming: Python, R, SQL, Scala
Machine Learning: Scikit-learn, TensorFlow, PyTorch, Keras
Data Analysis: Pandas, NumPy, SciPy, Matplotlib, Seaborn, Plotly
Databases: PostgreSQL, MySQL, MongoDB, Snowflake
Cloud Platforms: AWS (SageMaker, S3, EC2), Google Cloud Platform
Big Data: Apache Spark, Hadoop, Kafka
Tools: Jupyter, Git, Docker, Airflow

PROFESSIONAL EXPERIENCE

Senior Data Scientist | FinTech Analytics | 2021 - Present
• Developed machine learning models for fraud detection with 95% accuracy
• Built recommendation systems increasing user engagement by 25%
• Created automated data pipelines processing 1M+ transactions daily
• Collaborated with engineering teams to deploy models in production
• Presented insights to C-level executives and stakeholders

Data Scientist | Marketing Insights Corp | 2019 - 2021
• Designed A/B testing frameworks for marketing campaigns
• Built customer segmentation models using clustering algorithms
• Created interactive dashboards using Tableau and Python
• Performed statistical analysis on customer behavior data
• Reduced customer churn by 15% through predictive modeling

PROJECTS
Stock Price Prediction Model
• Developed LSTM neural network for stock price forecasting
• Achieved 85% accuracy using TensorFlow and historical market data
• Deployed model on AWS SageMaker with real-time predictions

Customer Lifetime Value Analysis
• Built CLV prediction model using regression and ensemble methods
• Analyzed customer data to identify high-value segments
• Presented findings that influenced marketing strategy decisions

Natural Language Processing for Reviews
• Created sentiment analysis model for product reviews
• Used BERT and transformer models for text classification
• Processed 100K+ reviews with 92% accuracy

EDUCATION
Master of Science in Data Science
Columbia University | 2019

Bachelor of Science in Statistics
University of California, Los Angeles | 2017

CERTIFICATIONS
• AWS Certified Machine Learning - Specialty
• Google Cloud Professional Data Engineer
• Certified Analytics Professional (CAP)
"""
    },
    {
        "filename": "mike_johnson_frontend_dev.txt",
        "content": """
MIKE JOHNSON
Frontend Developer
Email: mike.johnson@email.com
Phone: (555) 456-7890
Location: Austin, TX

PROFESSIONAL SUMMARY
Creative Frontend Developer with 3+ years of experience building responsive, 
user-friendly web applications. Passionate about modern JavaScript frameworks, 
UI/UX design, and creating exceptional user experiences.

TECHNICAL SKILLS
Frontend: HTML5, CSS3, JavaScript (ES6+), TypeScript
Frameworks: React.js, Vue.js, Angular, Next.js
Styling: Sass, Less, Styled Components, Tailwind CSS, Bootstrap
Tools: Git, Webpack, Vite, npm, yarn
Design: Figma, Adobe XD, Photoshop, Sketch
Testing: Jest, Cypress, React Testing Library
Other: Node.js, Express.js, MongoDB

PROFESSIONAL EXPERIENCE

Frontend Developer | Creative Web Agency | 2021 - Present
• Developed 15+ responsive websites and web applications
• Collaborated with designers to implement pixel-perfect UI designs
• Optimized website performance achieving 95+ Google PageSpeed scores
• Implemented accessibility standards (WCAG 2.1) across all projects
• Led frontend development for e-commerce platform serving 50K+ users

Junior Frontend Developer | StartupTech | 2020 - 2021
• Built interactive components using React.js and TypeScript
• Integrated RESTful APIs and managed application state with Redux
• Participated in agile development process and daily standups
• Contributed to component library used across multiple projects

PROJECTS
Portfolio Website
• Designed and developed personal portfolio using React and Gatsby
• Implemented smooth animations and transitions using Framer Motion
• Achieved perfect Lighthouse scores for performance and accessibility

E-learning Platform
• Built interactive learning platform with React and Node.js
• Created responsive design supporting mobile and tablet devices
• Implemented user authentication and progress tracking features

Restaurant Booking System
• Developed booking interface using Vue.js and Vuetify
• Integrated with backend API for real-time availability
• Added calendar component and email notification system

EDUCATION
Bachelor of Arts in Web Design and Development
University of Texas at Austin | 2020

CERTIFICATIONS
• Google UX Design Certificate
• Meta Frontend Developer Certificate
• Responsive Web Design Certification (freeCodeCamp)

ADDITIONAL SKILLS
• Strong eye for design and attention to detail
• Experience with Agile/Scrum methodologies
• Excellent communication and teamwork skills
• Continuous learner staying updated with latest web technologies
"""
    }
]

def generate_sample_resumes():
    """Generate sample resume files"""
    import os
    
    resume_dir = os.path.join(os.path.dirname(__file__), 'resumes')
    os.makedirs(resume_dir, exist_ok=True)
    
    for resume in sample_resumes:
        file_path = os.path.join(resume_dir, resume['filename'])
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(resume['content'])
        print(f"Generated: {resume['filename']}")

if __name__ == "__main__":
    generate_sample_resumes()
    print("✅ Sample resumes generated successfully!")
