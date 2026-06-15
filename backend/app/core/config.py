import os
from dotenv import load_dotenv

load_dotenv()

# ── Groq API Keys (3 keys split across 7 agents for rate-limit safety) ──
GROQ_API_KEY_1 = os.getenv("GROQ_API_KEY_1", "")   # Review Intake + Purchase Verification
GROQ_API_KEY_2 = os.getenv("GROQ_API_KEY_2", "")   # Experience Consistency + Text Authenticity
GROQ_API_KEY_3 = os.getenv("GROQ_API_KEY_3", "")   # Media Authenticity + Trust Score

# ── LLM Model Configuration ──
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_FALLBACK_MODEL = os.getenv("GROQ_FALLBACK_MODEL", "llama-3.1-8b-instant")
GROQ_VISION_MODEL = os.getenv("GROQ_VISION_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")
GROQ_TEMPERATURE = float(os.getenv("GROQ_TEMPERATURE", "0.1"))

# ── LangSmith Tracing ──
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY", "")
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "true")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "ai-review-verification-system")

# Apply LangSmith env vars so LangChain picks them up automatically
if LANGSMITH_API_KEY:
    os.environ["LANGCHAIN_TRACING_V2"] = LANGCHAIN_TRACING_V2
    os.environ["LANGCHAIN_PROJECT"] = LANGCHAIN_PROJECT
    os.environ["LANGSMITH_API_KEY"] = LANGSMITH_API_KEY

# ── Database ──
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.getenv("DB_PATH", os.path.join(BASE_DIR, "review_system.db"))

# ── Uploads ──
UPLOADS_DIR = os.getenv("UPLOADS_DIR", os.path.join(BASE_DIR, "uploads"))
os.makedirs(UPLOADS_DIR, exist_ok=True)
