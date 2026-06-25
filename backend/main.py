from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import tempfile
from pathlib import Path
from extractors.registry import get_extractor
from reporters.html_reporter import HTMLReporter
from reporters.json_reporter import JSONReporter


app = FastAPI(
    title="Metadata Forensics API",
    description="Extract and analyze metadata from documents, images, audio, and PDFs",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "Metadata Forensics API",
        "version": "1.0.0",
        "endpoint": "POST /api/analyze"
    }


@app.post("/api/analyze")
async def analyze_file(file: UploadFile = File(...)):
    """Upload and analyze a file for metadata"""
    try:
        # Save temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            # Get appropriate extractor
            extractor = get_extractor(tmp_path)
            metadata = extractor._safe_extract()
            
            # Generate reports
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
            # Clean up temp file
            Path(tmp_path).unlink(missing_ok=True)
    
    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": f"Unsupported file type: {str(e)}"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Analysis failed: {str(e)}"}
        )


if __name__ == "__main__":
    import uvicorn
    print("✓ Starting Metadata Forensics API...")
    print("✓ Server: http://localhost:8000")
    print("✓ API docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
