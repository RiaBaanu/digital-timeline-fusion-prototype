# pipeline/provenance.py
import hashlib
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ProvenanceRecord:
    file_path: str
    row_index: int
    sha256_hash: str


def compute_sha256(file_path: str) -> str:
    hash_obj = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()
