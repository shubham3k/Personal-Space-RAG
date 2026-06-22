"""Application-wide constants."""

SUPPORTED_EXTENSIONS = {".md", ".markdown", ".txt", ".pdf", ".json", ".csv"}

DOC_TYPE_MAP = {
    "journals": "journal",
    "notes": "note",
    "bookmarks": "bookmark",
    "pdfs": "pdf",
    "exports": "export",
}

MAX_FILE_SIZE_MB = 50
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
MAX_DOCUMENT_CHARS = 100_000

SYSTEM_PROMPT_BUDGET = 500
CONTEXT_BUDGET = 4000
CHAT_HISTORY_BUDGET = 1000
RESPONSE_BUDGET = 2048

WATCH_IGNORE_PATTERNS = {
    ".swp", ".tmp", ".bak", "~", ".DS_Store", "Thumbs.db", ".gitkeep", ".crdownload"
}
WATCH_IGNORE_PREFIXES = {".", "~", "#"}

MIN_QUERY_LENGTH = 2
MAX_QUERY_LENGTH = 2000
LOW_CONFIDENCE_THRESHOLD = 0.4

GROQ_RPM_LIMIT = 30
GROQ_RPD_LIMIT = 14400
CEREBRAS_TPD_LIMIT = 1_000_000
GEMINI_RPD_LIMIT = 1500

PROVIDER_CONTEXT_WINDOWS = {
    "groq": 131_072,
    "cerebras": 131_072,
    "gemini": 1_048_576,
    "ollama": 8_192,
}
