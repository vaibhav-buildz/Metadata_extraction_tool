from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
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


# Serve frontend static files
_FRONTEND = Path(__file__).parent.parent / "frontend"
if _FRONTEND.exists():
    app.mount("/static", StaticFiles(directory=str(_FRONTEND)), name="static")


@app.get("/", response_class=HTMLResponse)
async def root():
    index = _FRONTEND / "index.html"
    if index.exists():
        return HTMLResponse(content=index.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>Metadata Forensics API</h1><p>Frontend not found.</p>")


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
    print("✓ Frontend UI:  http://localhost:8000")
    print("✓ API docs:     http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
