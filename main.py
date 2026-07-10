#FastAPI app — autonomous document-generation agent.

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from agent.models import AgentRequest, AgentResponse
from agent.orchestrator import run_agent_pipeline

load_dotenv()

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# Ensure output directory exists
OUTPUTS_DIR = Path(__file__).parent / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)


# Application lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown hooks."""
    logger.info("Agent DocX Builder starting up …")
    try:
        from agent.providers import detect_provider

        config = detect_provider()
        logger.info("LLM provider: %s (model: %s)", config.name, config.default_model)
    except RuntimeError as exc:
        logger.warning("No LLM provider detected — %s", exc)
    yield
    logger.info("Agent DocX Builder shutting down.")


# FastAPI instance
app = FastAPI(
    title="Agent DocX Builder",
    description="Autonomous agent that generates professional Word documents.",
    version="1.0.0",
    lifespan=lifespan,
)

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routes
@app.get("/health", tags=["ops"])
async def health_check():
    """Liveness probe — confirms the service is running."""
    return {"status": "ok"}


@app.post("/agent", response_model=AgentResponse, tags=["agent"])
async def create_document(body: AgentRequest):
    """Accept a natural-language request and return a structured document."""
    logger.info("Received request: %s", body.request[:80])
    result = await run_agent_pipeline(body.request, outputs_dir=OUTPUTS_DIR)
    return result


# Static file serving for generated documents
@app.get("/documents/{filename}", tags=["documents"])
async def download_document(filename: str):
    """Download a previously generated .docx file."""
    file_path = OUTPUTS_DIR / filename
    if not file_path.exists() or not file_path.suffix == ".docx":
        return JSONResponse(status_code=404, content={"detail": "Document not found."})

    from fastapi.responses import FileResponse

    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
