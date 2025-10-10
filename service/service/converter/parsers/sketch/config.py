# --- LLM Configuration ---
ENABLE_LLM_FALLBACK = True


# --- API Key Configuration ---
# Best practice: Load API Key from an environment variable.
# You can set it in your terminal: export SILICONFLOW_API_KEY="your_key_here"
LLM_API_KEY = "sk-ddwxtevjbtcuqswmcarbtykkrmlwdydiqqejgqakjayzbyga"  # Default to the last used key from original script
# LLM_API_KEY = "AIzaSyC0kAwn91TtXRfnJnTC-qEE9dZNG0vPgS8"  # Google
# LLM_API_KEY = "lm-studio"  # LM Studio

# --- Base URL Configuration ---
# The endpoint for the API call.
LLM_BASE_URL = "https://api.siliconflow.cn/v1"  # SiliconFlow (last used)
# LLM_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
# LLM_BASE_URL = "http://127.0.0.1:1234/v1"

# --- Model Name Configuration ---
# The specific model to be used.
LLM_MODEL_NAME = "Qwen/Qwen2.5-Coder-7B-Instruct"  # SiliconFlow (last used model from original script)
# LLM_MODEL_NAME = "gemini-2.5-flash"
# LLM_MODEL_NAME = "openai/gpt-oss-20b"

# --- Layout Analysis ---
# Threshold for considering layers in the same row for rule-based analysis
LAYOUT_Y_THRESHOLD = 10  # 增加垂直对齐容差，避免过度严格
# Threshold for horizontal alignment in column detection
LAYOUT_X_THRESHOLD = 10  # 增加水平对齐容差，提高分组准确性

# --- File Size Limits ---
# Maximum file size allowed for processing (50MB)
MAX_FILE_SIZE = 100 * 1024 * 1024
