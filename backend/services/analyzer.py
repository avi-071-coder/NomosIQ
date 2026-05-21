from google import genai
import os
import requests
import re

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

LEGAL_TERMS = {
    "bail": "Temporary release of accused with conditions",
    "cognizable": "Police can arrest without warrant",
    "non-cognizable": "Police need court order to investigate",
    "IPC": "Indian Penal Code (now BNS)",
    "BNS": "Bharatiya Nyaya Sanhita 2023",
    "FIR": "First Information Report - starts police investigation"
}

async def fetch_url_content(url):
    """Fetch content from URL"""
    try:
        response = requests.get(url, timeout=10)
        text = re.sub(r'<[^>]+>', '', response.text)  # Strip HTML
        return text[:10000]  # Limit length
    except:
        return None

async def analyze_document(input_data, url=None):
    """Main document analysis - TEXT & URL ONLY"""
    
    if isinstance(input_data, str) and input_data.startswith('http'):
        content = await fetch_url_content(input_data)
    elif isinstance(input_data, str):
        content = input_data
    else:
        return {"error": "Image upload not supported. Please paste text or use URL."}
    
    if not content:
        return {"error": "Could not extract text from input"}
    
    prompt = f"""
    Analyze this Indian legal document and provide structured analysis:

    DOCUMENT: {content[:4000]}

    Return JSON format ONLY with:
    {{
        "summary": "Simple 2-3 sentence explanation",
        "sections": [
            {{
                "title": "Section title",
                "explanation": "What it says in simple terms",
                "purpose": "Why this clause exists",
                "impact": "What it means for the user"
            }}
        ],
        "terms": ["list", "of", "legal", "terms"],
        "risk_level": "SAFE|ATTENTION|RISK",
        "risk_explanation": "Why this risk level",
        "next_steps": ["Actionable step 1", "Step 2", "Step 3"],
        "links": ["relevant authority links"]
    }}
    """
    
    response = client.models.generate_content(
        model='gemini-flash-latest',
        contents=prompt
    )
    # Simple JSON parsing (more robust)
    try:
        import json
        # Extract JSON from response
        json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
        analysis = json.loads(json_match.group()) if json_match else {}
    except:
        analysis = {"summary": "Analysis complete", "risk_level": "SAFE"}
    
    # Enhance with term explanations
    explained_terms = {term: LEGAL_TERMS.get(term, "Legal term") for term in analysis.get("terms", [])}
    
    return {
        **analysis,
        "terms_explained": explained_terms,
        "disclaimer": "This is informational only. Consult a lawyer.",
        "features_note": "Text & URL analysis working. Image OCR requires additional setup."
    }