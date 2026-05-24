## Research Paper Manager (with AI Summarization)

A backend system built with **FastAPI** for managing research papers, including PDF upload, text extraction, database storage, and AI-powered summarization using Claude API.

---

## Project Motivation
In academic research workflows, researchers and students frequently face the following challenges:
- Managing large volumes of distributed PDF papers.
- Extracting key information and cross-referencing efficiently
- Quickly understanding core contributions without spending hours reading full texts.

This project was developed to explore how **robust backend architectures and LLMs can be seamlessly combined** to drastically improve academic reading and literature review efficiency.

---

## Features
### Paper management
- Upload research papers (PDF format)
- Store and manage metadata in a database
- Retrieve and delete stored papers

### AI Powered Summarization
- Automatically extract text from uploaded PDFs
- Generate structured summaries using **Claude API**
- Provide concise key insights for each paper

### Database Integration
- SQLite database using SQLAlchemy
- Clean ORM-based data models
- Persistent storage for uploaded papers and summaries

### RESTful API
- Built with fastAPI
- Auto-generated API documentation (`/docs`)
- Clean modular routing structure

### File Handing
- PDF upload and storage system
- Static file serving for upload documents

---

## Tech Stack
- **Backend**: FastAPI
- **Database**: SQLite + SQLAlchemy
- **AI Integration**: Anthropic Claude API
- **PDF Processing**: PyPDF2 / pdfplumber
- **Validation**: Pydantic
- **Server**: Uvicorn

---

## Project Structure

```text
app/
├── api/
│   └── __init__.py          
│   └── papers.py          
├── services/
│   ├── pdf_service.py    
│   └── ai_service.py  
│   └── __init__.py     
├── config.py              
├── database.py          
├── main.py              
├── models.py             
├── schemas.py            
└── __init__.py            
```
---

---
## Research Value

This project explores the intersection of:

- Backend system design
- Document processing pipelines
- Large Language model applications in academic workflows

It serves as a prototype for **AI-assisted research reading tools**.

---

---
## Future Work
- Add user login system (so each user can manage their own papers)
- Improve AI summary quality (make it more structured)
- Add a simple frontend page (instead of only API)
- Support more file types
- Deploy the project online so it can be accessed from anywhere
---

## Author

Developed as a personal project for exploring backend engineering and AI-assisted academic tools.
