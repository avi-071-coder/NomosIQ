from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from pathlib import Path
from dotenv import load_dotenv
import uuid
import aiofiles

BASE_DIR = Path(__file__).resolve().parent

load_dotenv()

# Services
from services.analyzer import analyze_document
from services.chat import legal_chat
from services.explorer import search_legal_database

app = FastAPI(title="NomosIQ API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create static directories
os.makedirs(BASE_DIR / "static/uploads", exist_ok=True)

# Static files
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

@app.post("/api/analyze")
async def analyze_endpoint(
    content: str = Form(None),
    url: str = Form(None),
    file: UploadFile = File(None)
):
    """Analyze legal documents"""
    try:
        if file:
            # Save uploaded file
            file_id = str(uuid.uuid4())
            file_path = str(BASE_DIR / f"static/uploads/{file_id}_{file.filename}")
            async with aiofiles.open(file_path, 'wb') as out_file:
                content = await file.read()
                await out_file.write(content)
            
            result = await analyze_document(file_path)
            os.remove(file_path)  # Clean up
        elif content:
            result = await analyze_document(content)
        elif url:
            result = await analyze_document(url=url)
        else:
            raise HTTPException(status_code=400, detail="No input provided")
        
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def chat_endpoint(message: str = Form(...), context: str = Form("")):
    """LegalChat AI assistant"""
    try:
        response = await legal_chat(message, context)
        return {"success": True, "data": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/explore")
async def explore_endpoint(query: str = "", category: str = ""):
    """Legal knowledge explorer"""
    try:
        results = await search_legal_database(query, category)
        return {"success": True, "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount frontend static files at root
app.mount("/", StaticFiles(directory=str(BASE_DIR.parent / "frontend"), html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    os.makedirs(BASE_DIR / "static/uploads", exist_ok=True)
    uvicorn.run(app, host="0.0.0.0", port=8000)