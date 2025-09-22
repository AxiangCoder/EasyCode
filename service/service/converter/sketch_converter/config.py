
import os

# --- General Paths ---
# Base directory for the converter logic
BASE_DIR = os.path.dirname(__file__)
# Default root for media files, assuming a structure like service/media/
MEDIA_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "media"))

# --- Default File Paths ---
# These can be overridden by command-line arguments
DEFAULT_SKETCH_INPUT = os.path.join(MEDIA_ROOT, "sketches", "6B6771BA-E1C8-40F1-938C-19EDD4C50371.json")
DEFAULT_TOKENS_INPUT = os.path.join(BASE_DIR, "..", "design_tokens.json")
DEFAULT_DSL_OUTPUT = os.path.join(MEDIA_ROOT, "sketches", "dsl_output_refactored.json")
DEFAULT_REPORT_OUTPUT = os.path.join(MEDIA_ROOT, "sketches", "token_report_refactored.json")

# --- LLM Configuration ---
ENABLE_LLM_FALLBACK = True

# --- API Key Configuration ---
# Best practice: Load API Key from an environment variable.
# You can set it in your terminal: export SILICONFLOW_API_KEY="your_key_here"
LLM_API_KEY = os.environ.get("SILICONFLOW_API_KEY", "sk-ddwxtevjbtcuqswmcarbtykkrmlwdydiqqejgqakjayzbyga")  # Default to the last used key from original script

# Original commented-out keys for reference:
# LLM_API_KEY = "AIzaSyC0kAwn91TtXRfnJnTC-qEE9dZNG0vPgS8"  # Google
# LLM_API_KEY = "lm-studio"  # LM Studio

# --- Base URL Configuration ---
# The endpoint for the API call.
LLM_BASE_URL = "https://api.siliconflow.cn/v1"  # SiliconFlow (last used)

# Original commented-out URLs for reference (from original script's OpenAI client):
# LLM_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
# LLM_BASE_URL = "http://127.0.0.1:1234/v1"

# --- Model Name Configuration ---
# The specific model to be used.
LLM_MODEL_NAME = "Qwen/QwQ-32B"  # SiliconFlow (last used model from original script)

# Original commented-out models for reference:
# LLM_MODEL_NAME = "gemini-2.5-flash"
# LLM_MODEL_NAME = "openai/gpt-oss-20b"

# --- Layout Analysis ---
# Threshold for considering layers in the same row for rule-based analysis
LAYOUT_Y_THRESHOLD = 10
# Threshold for horizontal alignment in column detection
LAYOUT_X_THRESHOLD = 5

# --- File Size Limits ---
# Maximum file size allowed for processing (50MB)
MAX_FILE_SIZE = 100 * 1024 * 1024
