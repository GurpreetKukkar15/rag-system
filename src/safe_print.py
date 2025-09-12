"""
Emoji-safe logging and print utilities for Windows compatibility.
Prevents UnicodeEncodeError when using emoji characters in console output.
"""

import builtins
import re
import logging
import sys
import os

# -------------------------------
# Emoji/Unicode filter regex
# -------------------------------
emoji_pattern = re.compile(
    "[" 
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F1E0-\U0001F1FF"  # flags
    "\u2705\u274c\u26a0\ufe0f\u26a1\ufe0f"  # common symbols: ✅❌⚠️⚡
    "]+",
    flags=re.UNICODE
)

# -------------------------------
# Safe print override
# -------------------------------
original_print = builtins.print

def safe_print(*args, **kwargs):
    """Print function that strips emoji/unicode characters for Windows compatibility."""
    new_args = []
    for arg in args:
        if isinstance(arg, str):
            # Strip emoji and replace with ASCII equivalents
            clean_arg = emoji_pattern.sub("", str(arg))
            # Replace common emoji with ASCII equivalents
            clean_arg = clean_arg.replace("✅", "[OK]")
            clean_arg = clean_arg.replace("❌", "[ERROR]")
            clean_arg = clean_arg.replace("⚠️", "[WARNING]")
            clean_arg = clean_arg.replace("⚡", "[INFO]")
            clean_arg = clean_arg.replace("🚀", "[STARTUP]")
            new_args.append(clean_arg)
        else:
            new_args.append(arg)
    
    original_print(*new_args, **kwargs)

# Override the built-in print function
builtins.print = safe_print

# -------------------------------
# Safe logging setup
# -------------------------------
class EmojiFilter(logging.Filter):
    """Logging filter that strips emoji characters from log messages."""
    
    def filter(self, record):
        if hasattr(record, 'msg') and isinstance(record.msg, str):
            # Strip emoji and replace with ASCII equivalents
            clean_msg = emoji_pattern.sub("", str(record.msg))
            clean_msg = clean_msg.replace("✅", "[OK]")
            clean_msg = clean_msg.replace("❌", "[ERROR]")
            clean_msg = clean_msg.replace("⚠️", "[WARNING]")
            clean_msg = clean_msg.replace("⚡", "[INFO]")
            clean_msg = clean_msg.replace("🚀", "[STARTUP]")
            record.msg = clean_msg
        return True

def setup_safe_logging(log_file="logs/api.log", level=logging.INFO):
    """Set up emoji-safe logging configuration."""
    
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        filename=log_file,
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filemode='a'
    )
    
    # Add emoji filter to all loggers
    emoji_filter = EmojiFilter()
    for handler in logging.root.handlers:
        handler.addFilter(emoji_filter)
    
    # Also configure console logging
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(console_formatter)
    console_handler.addFilter(emoji_filter)
    
    logging.root.addHandler(console_handler)

# -------------------------------
# Utility functions
# -------------------------------
def safe_log_info(message):
    """Log an info message with emoji safety."""
    logging.info(message)

def safe_log_error(message):
    """Log an error message with emoji safety."""
    logging.error(message)

def safe_log_warning(message):
    """Log a warning message with emoji safety."""
    logging.warning(message)

def safe_log_debug(message):
    """Log a debug message with emoji safety."""
    logging.debug(message)

# -------------------------------
# Example usage and test
# -------------------------------
if __name__ == "__main__":
    # Test the emoji-safe printing
    print("✅ Testing emoji-safe print!")
    print("❌ This should work without Unicode errors")
    print("⚠️ Warning messages are safe too")
    print("⚡ Info messages work perfectly")
    print("🚀 Startup messages are clean")
    
    # Test logging
    setup_safe_logging()
    safe_log_info("✅ API started successfully!")
    safe_log_error("❌ Database connection failed!")
    safe_log_warning("⚠️ Ollama server not responding!")
    safe_log_debug("⚡ Debug information here!")
