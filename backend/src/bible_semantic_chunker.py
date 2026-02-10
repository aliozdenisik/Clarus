"""
Semantic Chunking Module for Bible Verses

Groups semantically related verses together based on embedding similarity.
Preserves verse atomicity - verses are never split, only grouped.

Key Features:
- Embedding-based similarity computation
- Sliding window approach for boundary detection
- Configurable threshold strategies
- Respects book and chapter boundaries
"""

import json
import asyncio
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from tqdm import tqdm

from .bible_loader import BibleChunk, BibleDataLoader
from .embeddings import DenseEncoder, AsyncDenseEncoder


@dataclass
class BibleSemanticChunk:
    """Represents a group of semantically related Bible verses."""

    chunk_id: str  # Unique identifier, e.g., "kjva:1:1:1-5_semantic"
    verse_ids: List[str]  # List of verse IDs
    translation: str  # Translation code (e.g., "kjva")
    book_id: int  # Book number
    book_name: str  # Book name
    chapter: int  # Chapter number
    start_verse: int  # First verse number in chunk
    end_verse: int  # Last verse number in chunk
    text: str  # Combined text
    testament: str  # OT, NT, or Apocrypha
    verse_count: int = 0  # Number of verses in chunk
    internal_similarities: List[float] = field(
        default_factory=list
    )  # Similarities within chunk
    avg_internal_similarity: float = 0.0  # Average internal similarity

    def __post_init__(self):
        self.verse_count = len(self.verse_ids)
        if self.internal_similarities:
            self.avg_internal_similarity = sum(self.internal_similarities) / len(
                self.internal_similarities
            )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "chunk_id": self.chunk_id,
            "verse_ids": self.verse_ids,
            "translation": self.translation,
            "book_id": self.book_id,
            "book_name": self.book_name,
            "chapter": self.chapter,
            "start_verse": self.start_verse,
            "end_verse": self.end_verse,
            "text": self.text,
            "testament": self.testament,
            "verse_count": self.verse_count,
            "internal_similarities": self.internal_similarities,
            "avg_internal_similarity": self.avg_internal_similarity,
        }


class BibleSemanticVerseChunker:
    """
    Groups Bible verses into semantic chunks based on embedding similarity.

    The chunking process:
    1. Load all verses and compute embeddings
    2. Calculate cosine similarity between consecutive verses
    3. Detect chunk boundaries where similarity drops below threshold
    4. Apply constraints (max size, book/chapter boundaries)
    5. Create BibleSemanticChunk objects

    Args:
        translation: Bible translation to use (default: "kjva")
        similarity_threshold: Minimum similarity to keep verses in same chunk
        max_chunk_size: Maximum number of verses per chunk
        respect_chapter_boundary: If True, chunks don't cross chapter boundaries (Default: True)
        encoder: Optional DenseEncoder instance
    """

    def __init__(
        self,
        translation: str = "kjva",
        similarity_threshold: float = 0.75,
        max_chunk_size: int = 10,
        respect_chapter_boundary: bool = True,
        encoder: Optional[DenseEncoder] = None,
        async_encoder: Optional[AsyncDenseEncoder] = None,
        use_async: bool = True,  # Use async encoder by default for speed
        cache_dir: Optional[Path] = None,
    ):
        self.translation = translation
        self.similarity_threshold = similarity_threshold
        self.max_chunk_size = max_chunk_size
        self.respect_chapter_boundary = respect_chapter_boundary
        self.encoder = encoder or DenseEncoder()
        self.async_encoder = async_encoder
        self.use_async = use_async
        self.cache_dir = cache_dir or Path("cache")
        self.cache_dir.mkdir(exist_ok=True)

        # Store computed data
        self._verses: List[BibleChunk] = []
        self._embeddings: Optional[np.ndarray] = None
        self._similarities: Optional[np.ndarray] = None

    def load_verses(
        self, verses: Optional[List[BibleChunk]] = None, show_progress: bool = True
    ) -> List[BibleChunk]:
        """Load verses either from provided list or from data loader."""
        if verses is not None:
            self._verses = verses
        else:
            loader = BibleDataLoader(translation=self.translation)
            self._verses = loader.create_chunks(show_progress=show_progress)

        return self._verses

    def compute_embeddings(
        self,
        verses: Optional[List[BibleChunk]] = None,
        show_progress: bool = True,
        use_cache: bool = True,
    ) -> np.ndarray:
        """Compute embeddings for all verses. Uses async encoder if available for 2-3x speedup."""
        if verses is not None:
            self._verses = verses

        if not self._verses:
            self.load_verses(show_progress=show_progress)

        filename = f"bible_{self.translation}_embeddings.npy"
        meta_filename = f"bible_{self.translation}_embeddings_meta.json"

        cache_path = self.cache_dir / filename
        cache_meta_path = self.cache_dir / meta_filename

        # Try to load from cache
        if use_cache and cache_path.exists() and cache_meta_path.exists():
            with open(cache_meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            if meta.get("num_verses") == len(self._verses):
                print(f"Loading cached embeddings from {cache_path}")
                loaded_embeddings = np.load(cache_path)
                self._embeddings = loaded_embeddings
                return loaded_embeddings

        # Compute embeddings
        print(f"Computing embeddings for {len(self._verses)} verses...")
        texts = [v.text for v in self._verses]

        # Use async encoder for faster processing (2-3x speedup)
        if self.use_async:
            embeddings = asyncio.run(
                self._compute_embeddings_async(texts, show_progress)
            )
        else:
            # Fallback to sync with larger batch
            embeddings = self.encoder.encode_batch(
                texts,
                show_progress=show_progress,
                batch_size=100,  # Increased from 32
            )

        computed_embeddings = np.array(embeddings)
        self._embeddings = computed_embeddings

        # Cache embeddings
        np.save(cache_path, computed_embeddings)
        with open(cache_meta_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "num_verses": len(self._verses),
                    "embedding_dim": computed_embeddings.shape[1],
                    "translation": self.translation,
                },
                f,
            )
        print(f"Cached embeddings to {cache_path}")

        return computed_embeddings

    async def _compute_embeddings_async(
        self,
        texts: List[str],
        show_progress: bool = True,
    ) -> List[List[float]]:
        """
        Async embedding computation with optimized batching.

        Uses:
        - batch_size=256: Larger batches reduce API overhead
        - max_concurrent=10: Parallel requests for maximum throughput
        """
        # Lazy init async encoder
        if self.async_encoder is None:
            self.async_encoder = AsyncDenseEncoder()

        return await self.async_encoder.encode_batch_async(
            texts,
            batch_size=256,  # 8x larger than sync default
            max_concurrent=10,  # Parallel API calls
            show_progress=show_progress,
        )

    def compute_similarities(
        self,
        embeddings: Optional[np.ndarray] = None,
    ) -> np.ndarray:
        """Compute cosine similarity between consecutive verses."""
        if embeddings is not None:
            self._embeddings = embeddings

        if self._embeddings is None:
            self.compute_embeddings()

        assert self._embeddings is not None
        embeddings_array = self._embeddings

        # Normalize embeddings for cosine similarity
        norms = np.linalg.norm(embeddings_array, axis=1, keepdims=True)
        # Avoid division by zero
        norms[norms == 0] = 1e-10
        normalized = embeddings_array / norms

        # Compute similarity between consecutive pairs
        similarities = np.sum(normalized[:-1] * normalized[1:], axis=1)

        self._similarities = similarities
        return similarities

    def detect_boundaries(
        self,
        similarities: Optional[np.ndarray] = None,
        threshold: Optional[float] = None,
        threshold_type: str = "percentile",
    ) -> List[int]:
        """Detect chunk boundaries based on similarity threshold."""
        if similarities is not None:
            self._similarities = similarities

        if self._similarities is None:
            self.compute_similarities()

        assert self._similarities is not None
        similarities_array = self._similarities

        threshold = threshold if threshold is not None else self.similarity_threshold
        gradients: Optional[np.ndarray] = None
        grad_threshold = 0.0

        # Compute threshold based on strategy (same as Quran chunker)
        if threshold_type == "percentile":
            percentile_value = threshold if threshold <= 100 else 10
            computed_threshold = np.percentile(similarities_array, percentile_value)
            print(
                f"Percentile-based threshold: {computed_threshold:.4f} (p={percentile_value})"
            )

        elif threshold_type == "gradient":
            gradient_values = np.gradient(similarities_array)
            gradients = gradient_values
            grad_threshold = float(
                np.percentile(gradient_values, threshold if threshold <= 100 else 10)
            )
            computed_threshold = None
            print(f"Gradient-based detection: threshold={grad_threshold:.4f}")

        elif threshold_type == "interquartile":
            q1 = np.percentile(similarities_array, 25)
            q3 = np.percentile(similarities_array, 75)
            iqr = q3 - q1
            k = threshold if threshold < 10 else 1.5
            computed_threshold = q1 - k * iqr
            print(
                f"IQR-based threshold: {computed_threshold:.4f} (Q1={q1:.4f}, IQR={iqr:.4f}, k={k})"
            )

        elif threshold_type == "std":
            k = threshold if threshold < 10 else 1.0
            computed_threshold = np.mean(similarities_array) - k * np.std(
                similarities_array
            )
            print(f"Std-based threshold: {computed_threshold:.4f} (k={k})")

        else:  # "fixed"
            computed_threshold = threshold
            print(f"Fixed threshold: {computed_threshold:.4f}")

        boundaries = [0]

        for i, sim in enumerate(similarities_array):
            next_verse_idx = i + 1

            # Check for hard boundaries (Book or Chapter change)
            curr_verse = self._verses[i]
            next_verse = self._verses[next_verse_idx]

            # Always break on book change
            if curr_verse.book_id != next_verse.book_id:
                boundaries.append(next_verse_idx)
                continue

            # Optionally break on chapter change
            if (
                self.respect_chapter_boundary
                and curr_verse.chapter != next_verse.chapter
            ):
                boundaries.append(next_verse_idx)
                continue

            # Semantic check
            if threshold_type == "gradient":
                if gradients is not None and gradients[i] < grad_threshold:
                    boundaries.append(next_verse_idx)
            elif sim < computed_threshold:
                boundaries.append(next_verse_idx)

        return boundaries

    def _apply_size_constraints(
        self,
        boundaries: List[int],
        n_verses: int,
    ) -> List[int]:
        """Apply max/min chunk size constraints to boundaries."""
        assert self._similarities is not None
        similarities_array = self._similarities

        adjusted = [0]

        for i in range(1, len(boundaries)):
            prev_boundary = adjusted[-1]
            current_boundary = boundaries[i]
            chunk_size = current_boundary - prev_boundary

            # Split large chunks
            if chunk_size > self.max_chunk_size:
                start_idx = prev_boundary
                while start_idx + self.max_chunk_size < current_boundary:
                    search_start = start_idx
                    search_end = min(start_idx + self.max_chunk_size, current_boundary)

                    if search_end - 1 > search_start:
                        local_sims = similarities_array[search_start : search_end - 1]
                        # Find minimum similarity point to break at
                        min_sim_idx = np.argmin(local_sims) + search_start + 1
                        adjusted.append(min_sim_idx)
                        start_idx = min_sim_idx
                    else:
                        break

            if current_boundary not in adjusted:
                adjusted.append(current_boundary)

        return adjusted

    def create_semantic_chunks(
        self,
        verses: Optional[List[BibleChunk]] = None,
        show_progress: bool = True,
        use_cache: bool = True,
        threshold_type: str = "percentile",
    ) -> List[BibleSemanticChunk]:
        """Main method to create semantic chunks."""
        # Load
        if verses is not None:
            self._verses = verses
        elif not self._verses:
            self.load_verses(show_progress=show_progress)

        # Compute
        self.compute_embeddings(show_progress=show_progress, use_cache=use_cache)
        self.compute_similarities()

        # Detect
        boundaries = self.detect_boundaries(threshold_type=threshold_type)

        assert self._similarities is not None
        similarities_array = self._similarities

        # Constraint
        boundaries = self._apply_size_constraints(boundaries, len(self._verses))

        # Create Chunks
        chunks: List[BibleSemanticChunk] = []
        boundaries_with_end = boundaries + [len(self._verses)]

        iterator = range(len(boundaries))
        if show_progress:
            iterator = tqdm(iterator, desc="Creating Bible semantic chunks")

        for i in iterator:
            start_idx = boundaries_with_end[i]
            end_idx = boundaries_with_end[i + 1]

            chunk_verses = self._verses[start_idx:end_idx]

            if not chunk_verses:
                continue

            internal_sims = []
            if end_idx - start_idx > 1:
                internal_sims = similarities_array[start_idx : end_idx - 1].tolist()

            first = chunk_verses[0]
            last = chunk_verses[-1]

            # Format: translation:book:chapter:start-end_semantic
            chunk_id = f"{first.translation}:{first.book_id}:{first.chapter}:{first.verse}-{last.verse}_semantic"

            chunk = BibleSemanticChunk(
                chunk_id=chunk_id,
                verse_ids=[v.id for v in chunk_verses],
                translation=first.translation,
                book_id=first.book_id,
                book_name=first.book_name,
                chapter=first.chapter,
                start_verse=first.verse,
                end_verse=last.verse,
                text=" ".join(v.text for v in chunk_verses),
                testament=first.testament,
                internal_similarities=internal_sims,
            )

            chunks.append(chunk)

        print(
            f"\nCreated {len(chunks)} semantic chunks from {len(self._verses)} verses"
        )
        print(f"Average chunk size: {len(self._verses) / len(chunks):.2f} verses")

        return chunks

    def save_chunks(
        self,
        chunks: List[BibleSemanticChunk],
        output_path: Optional[Path] = None,
    ) -> Path:
        """Save semantic chunks to JSON file."""
        output_path = output_path or Path(
            f"data/bible_{self.translation}_semantic_chunks.json"
        )
        output_path.parent.mkdir(exist_ok=True)

        data = [chunk.to_dict() for chunk in chunks]

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"Saved {len(chunks)} chunks to {output_path}")
        return output_path

    def load_chunks(
        self,
        input_path: Optional[Path] = None,
    ) -> List[BibleSemanticChunk]:
        """Load semantic chunks from JSON file."""
        input_path = input_path or Path(
            f"data/bible_{self.translation}_semantic_chunks.json"
        )

        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        chunks = []
        for item in data:
            chunk = BibleSemanticChunk(
                chunk_id=item["chunk_id"],
                verse_ids=item["verse_ids"],
                translation=item["translation"],
                book_id=item["book_id"],
                book_name=item["book_name"],
                chapter=item["chapter"],
                start_verse=item["start_verse"],
                end_verse=item["end_verse"],
                text=item["text"],
                testament=item["testament"],
                internal_similarities=item.get("internal_similarities", []),
            )
            chunks.append(chunk)

        print(f"Loaded {len(chunks)} chunks from {input_path}")
        return chunks


if __name__ == "__main__":
    # Test the chunker
    print("Testing Bible Semantic Chunker...")

    chunker = BibleSemanticVerseChunker(
        translation="kjva",
        similarity_threshold=0.75,
        max_chunk_size=10,
    )

    chunks = chunker.create_semantic_chunks(show_progress=True)

    # Analyze a few chunks (e.g., Genesis 1)
    genesis_chunks = [c for c in chunks if c.book_name == "Genesis" and c.chapter == 1]
    print(f"\nGenesis 1 chunks ({len(genesis_chunks)}):")
    for c in genesis_chunks:
        print(f"  [{c.start_verse}-{c.end_verse}] {c.text[:50]}...")

    chunker.save_chunks(chunks)
