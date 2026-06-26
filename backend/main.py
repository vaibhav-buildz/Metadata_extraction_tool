from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sys
import tempfile
import os
from pathlib import Path
from dotenv import load_dotenv

# Load env variables from root or backend directories
load_dotenv(Path(__file__).parent.parent / ".env")
load_dotenv(Path(__file__).parent / ".env")


# Ensure backend subpackages are importable regardless of launch method
sys.path.insert(0, str(Path(__file__).parent))

from extractors.registry import get_extractor
from reporters.html_reporter import HTMLReporter
from reporters.json_reporter import JSONReporter

app = FastAPI(
    title="Metadata Forensics API",
    description="Extract and analyze metadata from documents, images, audio, and PDFs",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Metadata Forensics API"}

@app.post("/api/analyze")
async def analyze_file(file: UploadFile = File(...)):
    try:
        suffix = Path(file.filename).suffix if file.filename else ""
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            extractor = get_extractor(tmp_path)
            metadata = extractor._safe_extract()
            if file.filename:
                metadata["filename"] = file.filename
                
            html_report = HTMLReporter.generate(metadata)
            json_report = JSONReporter.generate(metadata)
            
            return {
                "success": True,
                "filename": file.filename,
                "metadata": metadata,
                "html_report": html_report,
                "json_report": json_report
            }
        finally:
            Path(tmp_path).unlink(missing_ok=True)
    
    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": f"Unsupported: {str(e)}"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Failed: {str(e)}"}
        )

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("FASTAPI_HOST", "0.0.0.0")
    port = int(os.getenv("FASTAPI_PORT", "8000"))
    reload = os.getenv("FASTAPI_RELOAD", "false").lower() == "true"
    
    print("✓ Starting Metadata Forensics API...")
    print(f"✓ Server: http://{host}:{port}")
    print(f"✓ Docs: http://{host}:{port}/docs")
    uvicorn.run("main:app", host=host, port=port, reload=reload)
