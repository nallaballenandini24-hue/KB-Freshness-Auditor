"""Helper functions"""
import uuid
from datetime import datetime


def generate_id() -> str:
    """Generate unique ID"""
    return str(uuid.uuid4())


def get_current_timestamp() -> datetime:
    """Get current UTC timestamp"""
    return datetime.utcnow()


def format_size(bytes_size: int) -> str:
    """Format bytes to human-readable size"""
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"


def extract_text_from_markdown(content: str) -> str:
    """Extract plain text from markdown content"""
    import re

    # Remove markdown formatting
    text = re.sub(r"[#*`~\[\]()]", "", content)
    return text.strip()
