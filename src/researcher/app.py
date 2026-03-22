from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from researcher.crew import Researcher, extract_clean_context
from researcher.pdf_generator import convert_md_to_pdf
from crewai import Crew, Process

# Vercel Compatibility: Only /tmp is writable in serverless functions
IS_VERCEL = os.environ.get("VERCEL") == "1"
BASE_DIR = "/tmp" if IS_VERCEL else os.getcwd()
REPORT_MD = os.path.join(BASE_DIR, "report.md")
REPORT_PDF = os.path.join(BASE_DIR, "report.pdf")

app = FastAPI(title="AI Researcher API")

# Enable CORS for frontend interaction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class ResearchRequest(BaseModel):
    topic: str

class ResearchStatus(BaseModel):
    status: str
    message: str

# In-memory status (for simplicity in this local app)
current_status = {"status": "idle", "message": "Ready to start research."}

def run_research_task(topic: str):
    global current_status
    try:
        current_status["status"] = "processing"
        current_status["message"] = f"Researching: {topic}..."
        
        inputs = {"topic": topic}
        r = Researcher(output_path=REPORT_MD)

        # ── Crew 1: Research ──────────────────────────────────
        research_crew = Crew(
            agents=[r.research_agent()],
            tasks=[r.research_task()],
            process=Process.sequential,
            verbose=True,
        )
        raw_output = research_crew.kickoff(inputs=inputs)
        clean_text = extract_clean_context(raw_output.raw) # LiteAgentOutput has .raw

        # ── Crew 2: Report generation ─────────────────────────
        current_status["message"] = "Generating report..."
        report_crew = Crew(
            agents=[r.generate_report()],
            tasks=[r.generate()],
            process=Process.sequential,
            verbose=True,
        )
        # Fix the hardcoded topic from main.py
        report_crew.kickoff(inputs={"topic": topic, "clean_text": clean_text})

        # ── PDF Generation ─────────────────────────
        current_status["message"] = "Converting to PDF..."
        convert_md_to_pdf(REPORT_MD, REPORT_PDF)
        
        current_status["status"] = "completed"
        current_status["message"] = "Research completed successfully!"
    except Exception as e:
        current_status["status"] = "error"
        current_status["message"] = f"Error: {str(e)}"

@app.post("/research", response_model=ResearchStatus)
async def start_research(request: ResearchRequest, background_tasks: BackgroundTasks):
    if current_status["status"] == "processing":
        raise HTTPException(status_code=400, detail="Research already in progress.")
    
    background_tasks.add_task(run_research_task, request.topic)
    return {"status": "processing", "message": "Research started in background."}

@app.get("/status", response_model=ResearchStatus)
async def get_status():
    return current_status

@app.get("/download")
async def download_pdf():
    pdf_path = REPORT_PDF
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF not found. Please run research first.")
    return FileResponse(pdf_path, media_type="application/pdf", filename="research_report.pdf")

# Serve static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
