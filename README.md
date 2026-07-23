# NomosIQ 
**AI-Powered Legal Intelligence for India**

NomosIQ is a professional legal platform designed to simplify complex Indian laws for citizens and professionals alike. It uses state-of-the-art AI to analyze legal documents, explain rights, and provide instant legal information.

## Core Features
- **LegalChat AI**: A 24/7 assistant that explains laws, sections, and procedures in simple English.
- **Document Analyzer**: Upload or paste legal documents to get summaries, risk indicators, and actionable steps.
- **Law Explorer**: Search and deep-link into specific BNS (Bharatiya Nyaya Sanhita) sections and Constitutional Articles.

## Requirements
- **Python 3.8+**
- **Google Gemini API Key** 
- **Dependencies**: Listed in `backend/requirements.txt`

## Getting Started

### 1. Setup Environment
Create a `.env` file in the `backend/` directory:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

### 2. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 3. Run the Platform
Start the backend server:
```bash
python backend/app.py
```
Then, open `frontend/index.html` in your browser.

## How It Works
1. **Frontend**: A modern Single Page Application (SPA) built with Vanilla HTML/JS/CSS for maximum speed and smooth navigation.
2. **Backend**: A FastAPI server that handles requests, document processin


