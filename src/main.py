import uvicorn
import sys
import os
import builtins
import re

# Emoji-safe print override (prevents UnicodeEncodeError on Windows)
emoji_pattern = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F1E0-\U0001F1FF"  # flags
    "\U00002700-\U000027BF"  # dingbats
    "\U0001F900-\U0001F9FF"  # supplemental symbols & pictographs
    "\U00002600-\U000026FF"  # miscellaneous symbols
    "\U00002B00-\U00002BFF"  # miscellaneous symbols & arrows
    "]+",
    flags=re.UNICODE,
)

original_print = builtins.print

def safe_print(*args, **kwargs):
    new_args = []
    for arg in args:
        if isinstance(arg, str):
            arg = emoji_pattern.sub("", arg)
        new_args.append(arg)
    original_print(*new_args, **kwargs)

builtins.print = safe_print

# Import emoji-safe logging
from safe_print import setup_safe_logging, safe_log_info, safe_log_error, safe_log_warning

# Set up emoji-safe logging
setup_safe_logging()

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Check database migration before starting
try:
    from init_db import check_and_migrate
    check_and_migrate()
except Exception as e:
    safe_log_warning(f"Database migration check failed: {e}")
    safe_log_info("Continuing with startup...")

from api import app

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
