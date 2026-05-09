import google.generativeai as genai
import os
import json

api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-flash-latest')

async def search_legal_database(query, category=""):
    """Search legal database dynamically using AI for comprehensive coverage"""
    if not query:
        default_laws = [
            {
                "title": "Article 21, Constitution of India",
                "explanation": "Guarantees the protection of life and personal liberty to all persons.",
                "applies": "When a person's life or freedom is unlawfully restricted by the state.",
                "category": "constitution"
            },
            {
                "title": "Section 103, Bharatiya Nyaya Sanhita (BNS)",
                "explanation": "Defines the punishment for murder (formerly IPC Section 302).",
                "applies": "In cases involving culpable homicide amounting to murder.",
                "category": "bns"
            },
            {
                "title": "Right to Information Act (RTI), 2005",
                "explanation": "Empowers citizens to request information from public authorities, promoting transparency.",
                "applies": "When you need official records, government data, or status of your applications.",
                "category": "rights"
            },
            {
                "title": "Article 14, Constitution of India",
                "explanation": "Ensures equality before the law and equal protection of the laws within India.",
                "applies": "When there is discrimination by the state on grounds of religion, race, caste, sex, or place of birth.",
                "category": "constitution"
            },
            {
                "title": "Consumer Protection Act, 2019",
                "explanation": "Protects consumers from unfair trade practices, defective goods, and deficient services.",
                "applies": "When you receive a faulty product or are misled by false advertisements.",
                "category": "rights"
            }
        ]
        
        if category:
            return [law for law in default_laws if law["category"] == category]
        return default_laws
        
    prompt = f"""
    You are an Indian Legal Expert. The user searched for: "{query}"
    Category filter: "{category}" (can be 'constitution', 'bns', 'rights', or empty for all).
    
    Find the most relevant Indian laws, BNS sections, or Constitutional articles matching this search.
    - If the user searches for a specific article or section (e.g., "Article 21" or "BNS 103"), return ONLY that specific result.
    - If the search is broad, vague, or contains typos (e.g., "ny article", "theft", "rights"), return up to 5 of the closest matching results.
    - ALWAYS return at least 1 relevant result. Do not return an empty array.
    
    Respond strictly with a JSON array ONLY:
    [
        {{
            "title": "Exact Law/Section/Article Name",
            "explanation": "Simple 1-2 sentence explanation of what it means",
            "applies": "Real life scenario when this applies",
            "category": "bns" // (or constitution, rights)
        }}
    ]
    """
    try:
        response = model.generate_content(prompt)
        text_response = response.text
        if '```json' in text_response:
            text_response = text_response.split('```json')[1].split('```')[0]
        elif '```' in text_response:
            text_response = text_response.split('```')[1].split('```')[0]
            
        results = json.loads(text_response.strip())
        return results
    except Exception as e:
        print(f"Explorer Error: {e}")
        return [{
            "title": "System Notice",
            "explanation": "Our AI explorer is currently experiencing high load or your API key is invalid.",
            "applies": "Please try searching again in a moment.",
            "category": "system"
        }]