# Sample Data for Resume Relevance System

This directory contains sample data for testing and demonstrating the Resume Relevance System.

## Directory Structure

\`\`\`
sample_data/
├── jds_pdf/          # Job Description PDF files (place your 2 JD PDFs here)
├── resumes_pdf/      # Resume PDF files (place your 10 resume PDFs here)
├── pdf_data_loader.py # PDF data management utilities
└── README.md         # This file
\`\`\`

## Setting Up Your PDF Files

### Job Descriptions (2 files expected)
Place your job description PDF files in `jds_pdf/` directory:
- Example: `axion_ray_data_analyst.pdf`
- Example: `software_engineer_position.pdf`

### Resumes (10 files expected)  
Place your resume PDF files in `resumes_pdf/` directory:
- Example: `pavan_kalyan_resume.pdf`
- Example: `candidate_2_resume.pdf`
- ... (8 more resume files)

## File Naming Conventions

### For Job Descriptions:
- Use descriptive names: `company_position.pdf`
- Examples: `axion_ray_data_analyst.pdf`, `tech_corp_frontend_dev.pdf`

### For Resumes:
- Use candidate names: `firstname_lastname_resume.pdf`
- Examples: `pavan_kalyan_resume.pdf`, `john_doe_resume.pdf`

## Loading Data into System

After placing your PDF files:

1. **Validate files are in place:**
   \`\`\`bash
   python sample_data/pdf_data_loader.py
   \`\`\`

2. **Load into database:**
   \`\`\`bash
   python scripts/load_pdf_sample_data.py
   \`\`\`

3. **Start the system:**
   \`\`\`bash
   ./run.sh
   \`\`\`

## Sample Content Reference

Based on your provided samples:

### Job Description Example (Axion Ray):
- **Position:** Data Analyst  
- **Company:** Axion Ray
- **Requirements:** Manufacturing engineering background, Python/R, data analysis
- **Experience:** 1+ years in manufacturing

### Resume Example (Pavan Kalyan):
- **Name:** Pavan Kalyan
- **Skills:** Python, SQL, Data Visualization, Pandas, NumPy
- **Background:** Physics degree, Data Analysis projects
- **Experience:** Data analysis, web scraping, dashboard building

## Troubleshooting

### Common Issues:
1. **No PDF files found:** Ensure files are in correct directories
2. **Empty files:** Check that PDF files are not corrupted
3. **Parsing errors:** Verify PDFs contain readable text (not just images)

### Getting Help:
- Check the main README.md for system setup
- Run `python scripts/test_system.py` for comprehensive testing
- Review logs in the console for detailed error messages
\`\`\`

```bash file="" isHidden
