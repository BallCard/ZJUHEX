"""
Test semantic similarity for cross-textbook deduplication.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src" / "backend"))

from sentence_transformers import SentenceTransformer
import numpy as np

# Load model
print("Loading model...")
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# Test texts
text1 = "细胞膜 细胞膜是细胞的外层结构，由脂质双层组成"
text2 = "细胞膜 细胞膜由磷脂双分子层构成，具有选择通透性"

# Compute embeddings
embeddings = model.encode([text1, text2])

# Compute cosine similarity
similarity = np.dot(embeddings[0], embeddings[1]) / (
    np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
)

print(f"\nText 1: {text1}")
print(f"Text 2: {text2}")
print(f"\nCosine similarity: {similarity:.4f}")
print(f"Threshold: 0.90")
print(f"Will merge: {'YES' if similarity >= 0.90 else 'NO'}")

# Test with more similar texts
text3 = "细胞膜 细胞膜是细胞的外层结构"
text4 = "细胞膜 细胞膜是细胞外层结构"

embeddings2 = model.encode([text3, text4])
similarity2 = np.dot(embeddings2[0], embeddings2[1]) / (
    np.linalg.norm(embeddings2[0]) * np.linalg.norm(embeddings2[1])
)

print(f"\n\nText 3: {text3}")
print(f"Text 4: {text4}")
print(f"\nCosine similarity: {similarity2:.4f}")
print(f"Will merge: {'YES' if similarity2 >= 0.90 else 'NO'}")
