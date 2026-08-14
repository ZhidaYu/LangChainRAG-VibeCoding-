"""Chinese text cleaning utilities."""
import re


def clean_text(text: str) -> str:
    """Clean and normalize Chinese text."""
    if not text:
        return ""
    # Remove excessive whitespace
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Normalize Unicode
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Remove control chars except newlines
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    return text.strip()
