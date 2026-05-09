import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-flash-latest')

BNS_SECTIONS = {
    "302": "Murder - punishment death/life imprisonment",
    "304": "Culpable homicide not amounting to murder",
    "420": "Cheating and dishonestly inducing delivery of property"
}

async def legal_chat(message, context=""):
    """LegalChat AI Assistant"""
    
    system_prompt = """
    You are LegalChat, an AI legal assistant for India. Always:
    1. Use simple, clear language (avoid legal jargon)
    2. Reference BNS sections, Constitution Articles when relevant
    3. Assess risk level: SAFE/ATTENTION/RISK
    4. Provide actionable next steps
    5. Include relevant helplines/authorities
    6. Add disclaimer: "Not legal advice"
    
    Structure response as JSON:
    {
        "answer": "Clear explanation",
        "risk_level": "SAFE|ATTENTION|RISK",
        "sections": ["BNS 302", "Art 21"],
        "next_steps": ["Step 1", "Step 2"],
        "related_questions": ["Q1?", "Q2?"],
        "links": ["helpline urls"]
    }
    """
    
    full_prompt = f"{system_prompt}\n\nContext: {context}\nUser: {message}"
    
    try:
        response = model.generate_content(full_prompt)
        text_response = response.text
        # Clean up JSON formatting if present
        if '```json' in text_response:
            text_response = text_response.split('```json')[1].split('```')[0]
        elif '```' in text_response:
            text_response = text_response.split('```')[1].split('```')[0]
            
        chat_response = json.loads(text_response.strip())
        return chat_response
    except Exception as e:
        print(f"Chat Error: {e}")
        return {
            "answer": "I'm sorry, I encountered an issue processing your legal request. Please try again or rephrase your question. If the system is not configured with a valid API key, AI features will be disabled.",
            "risk_level": "ATTENTION",
            "sections": [],
            "next_steps": ["Ensure your internet connection is stable.", "Check if the API key is configured properly in .env"],
            "related_questions": [],
            "links": []
        }