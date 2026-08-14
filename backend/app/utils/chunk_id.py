"""Deterministic chunk ID generation."""
import hashlib


def generate_chunk_id(source_file: str, chunk_index: int, content: str) -> str:
    """Generate a deterministic chunk ID: same content always maps to same ID."""
    content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
    key = f"{source_file}|chunk_{chunk_index}|{content_hash}"
    return hashlib.sha256(key.encode()).hexdigest()
