"""
Semantic Chunking Module for Quran Verses

Groups semantically related verses together based on embedding similarity.
Preserves verse atomicity - verses are never split, only grouped.

Key Features:
- Embedding-based similarity computation
- Sliding window approach for boundary detection
- Configurable threshold strategies (fixed, percentile, std-based)
- Respects surah boundaries
"""

import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from tqdm import tqdm

from .data_loader import QuranChunk, QuranDataLoader
from .embeddings import DenseEncoder


@dataclass
class SemanticChunk:
    """Represents a group of semantically related verses."""

    chunk_id: str  # Unique identifier, e.g., "2:30-33_semantic"
    verse_ids: List[str]  # List of verse IDs, e.g., ["2:30", "2:31", "2:32", "2:33"]
    surah_id: int  # Surah number
    surah_name: str  # Turkish surah name
    surah_name_arabic: str  # Arabic surah name
    surah_transliteration: str  # Transliterated surah name
    surah_type: str  # meccan or medinan
    start_verse: int  # First verse number in chunk
    end_verse: int  # Last verse number in chunk
    combined_translation: str  # Combined Turkish translation
    combined_arabic: str  # Combined Arabic text
    combined_normalized: str = ""  # Normalized text for search
    combined_lemma: str = ""  # Lemmatized text for search
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
            "surah_id": self.surah_id,
            "surah_name": self.surah_name,
            "surah_name_arabic": self.surah_name_arabic,
            "surah_transliteration": self.surah_transliteration,
            "surah_type": self.surah_type,
            "start_verse": self.start_verse,
            "end_verse": self.end_verse,
            "combined_translation": self.combined_translation,
            "combined_arabic": self.combined_arabic,
            "combined_normalized": self.combined_normalized,
            "combined_lemma": self.combined_lemma,
            "verse_count": self.verse_count,
            "internal_similarities": self.internal_similarities,
            "avg_internal_similarity": self.avg_internal_similarity,
        }


class SemanticVerseChunker:
    """
    Groups Quran verses into semantic chunks based on embedding similarity.

    The chunking process:
    1. Load all verses and compute embeddings
    2. Calculate cosine similarity between consecutive verses
    3. Detect chunk boundaries where similarity drops below threshold
    4. Apply constraints (max size, surah boundaries)
    5. Create SemanticChunk objects

    Args:
        similarity_threshold: Minimum similarity to keep verses in same chunk
                              Can be float (0.0-1.0) or "percentile:X" or "std:X"
        max_chunk_size: Maximum number of verses per chunk
        min_chunk_size: Minimum verses per chunk (unless at surah boundary)
        respect_surah_boundary: If True, chunks don't cross surah boundaries
        encoder: Optional DenseEncoder instance (will create one if not provided)
    """

    def __init__(
        self,
        similarity_threshold: float = 0.75,
        max_chunk_size: int = 10,
        min_chunk_size: int = 1,
        respect_surah_boundary: bool = True,
        encoder: Optional[DenseEncoder] = None,
        cache_dir: Optional[Path] = None,
    ):
        self.similarity_threshold = similarity_threshold
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size
        self.respect_surah_boundary = respect_surah_boundary
        self.encoder = encoder or DenseEncoder()
        self.cache_dir = cache_dir or Path("cache")
        self.cache_dir.mkdir(exist_ok=True)

        # Store computed data
        self._verses: List[QuranChunk] = []
        self._embeddings: Optional[np.ndarray] = None
        self._similarities: Optional[np.ndarray] = None

    def load_verses(
        self, verses: Optional[List[QuranChunk]] = None, show_progress: bool = True
    ) -> List[QuranChunk]:
        """
        Load verses either from provided list or from data loader.

        Args:
            verses: Optional list of QuranChunk objects
            show_progress: Show progress bar

        Returns:
            List of QuranChunk objects
        """
        if verses is not None:
            self._verses = verses
        else:
            loader = QuranDataLoader()
            self._verses = loader.create_chunks(show_progress=show_progress)

        return self._verses

    def compute_embeddings(
        self,
        verses: Optional[List[QuranChunk]] = None,
        show_progress: bool = True,
        use_cache: bool = True,
    ) -> np.ndarray:
        """
        Compute embeddings for all verses.

        Args:
            verses: Optional list of verses (uses loaded verses if not provided)
            show_progress: Show progress bar
            use_cache: Use cached embeddings if available

        Returns:
            numpy array of shape (n_verses, embedding_dim)
        """
        if verses is not None:
            self._verses = verses

        if not self._verses:
            self.load_verses(show_progress=show_progress)

        cache_path = self.cache_dir / "verse_embeddings.npy"
        cache_meta_path = self.cache_dir / "verse_embeddings_meta.json"

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
        texts = [v.translation for v in self._verses]

        embeddings = self.encoder.encode_batch(
            texts, show_progress=show_progress, batch_size=32
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
                },
                f,
            )
        print(f"Cached embeddings to {cache_path}")

        return computed_embeddings

    def compute_similarities(
        self,
        embeddings: Optional[np.ndarray] = None,
    ) -> np.ndarray:
        """
        Compute cosine similarity between consecutive verses.

        Args:
            embeddings: Optional embedding array (uses computed embeddings if not provided)

        Returns:
            numpy array of shape (n_verses - 1,) with similarity scores
        """
        if embeddings is not None:
            self._embeddings = embeddings

        if self._embeddings is None:
            self.compute_embeddings()

        assert self._embeddings is not None
        embeddings_array = self._embeddings

        # Normalize embeddings for cosine similarity
        norms = np.linalg.norm(embeddings_array, axis=1, keepdims=True)
        normalized = embeddings_array / norms

        # Compute similarity between consecutive pairs
        # similarity[i] = cosine_sim(verse[i], verse[i+1])
        similarities = np.sum(normalized[:-1] * normalized[1:], axis=1)

        self._similarities = similarities
        return similarities

    def detect_boundaries(
        self,
        similarities: Optional[np.ndarray] = None,
        threshold: Optional[float] = None,
        threshold_type: str = "percentile",
    ) -> List[int]:
        """
        Detect chunk boundaries based on similarity threshold.

        Supports multiple threshold strategies (like LangChain SemanticChunker):
        - "percentile": Split at positions where similarity is below X percentile (default: 10)
        - "gradient": Split where similarity gradient (change rate) is highest
        - "interquartile": Split below Q1 - 1.5*IQR
        - "fixed": Use the exact threshold value provided

        A boundary is placed between verse[i] and verse[i+1] when:
        - similarity[i] < computed_threshold, OR
        - surah changes (if respect_surah_boundary is True)

        Args:
            similarities: Optional similarity array
            threshold: Threshold value (interpretation depends on threshold_type)
            threshold_type: "percentile", "gradient", "interquartile", or "fixed"

        Returns:
            List of boundary indices (positions where new chunks start)
        """
        if similarities is not None:
            self._similarities = similarities

        if self._similarities is None:
            self.compute_similarities()

        assert self._similarities is not None
        similarities_array = self._similarities

        threshold = threshold if threshold is not None else self.similarity_threshold
        gradients: Optional[np.ndarray] = None
        grad_threshold = 0.0

        # Compute threshold based on strategy
        if threshold_type == "percentile":
            # threshold is the percentile value (e.g., 10 means bottom 10%)
            # Lower percentile = more chunks, higher = fewer chunks
            percentile_value = threshold if threshold <= 100 else 10
            computed_threshold = np.percentile(similarities_array, percentile_value)
            print(
                f"Percentile-based threshold: {computed_threshold:.4f} (p={percentile_value})"
            )

        elif threshold_type == "gradient":
            # Find positions where similarity drops sharply
            # Use gradient (rate of change) to detect boundaries
            gradient_values = np.gradient(similarities_array)
            gradients = gradient_values
            # Threshold on negative gradients (drops in similarity)
            grad_threshold = float(
                np.percentile(gradient_values, threshold if threshold <= 100 else 10)
            )
            computed_threshold = None  # We'll use gradient-based detection
            print(f"Gradient-based detection: threshold={grad_threshold:.4f}")

        elif threshold_type == "interquartile":
            # IQR-based: split below Q1 - k*IQR
            q1 = np.percentile(similarities_array, 25)
            q3 = np.percentile(similarities_array, 75)
            iqr = q3 - q1
            k = threshold if threshold < 10 else 1.5  # default k=1.5
            computed_threshold = q1 - k * iqr
            print(
                f"IQR-based threshold: {computed_threshold:.4f} (Q1={q1:.4f}, IQR={iqr:.4f}, k={k})"
            )

        elif threshold_type == "std":
            # Standard deviation based: mean - k*std
            k = threshold if threshold < 10 else 1.0
            computed_threshold = np.mean(similarities_array) - k * np.std(
                similarities_array
            )
            print(f"Std-based threshold: {computed_threshold:.4f} (k={k})")

        else:  # "fixed" or unknown
            computed_threshold = threshold
            print(f"Fixed threshold: {computed_threshold:.4f}")

        boundaries = [0]  # First verse always starts a chunk

        for i, sim in enumerate(similarities_array):
            next_verse_idx = i + 1

            # Check surah boundary
            if self.respect_surah_boundary:
                if self._verses[i].surah_id != self._verses[next_verse_idx].surah_id:
                    boundaries.append(next_verse_idx)
                    continue

            # Gradient-based detection
            if threshold_type == "gradient":
                if gradients is not None and gradients[i] < grad_threshold:
                    boundaries.append(next_verse_idx)
            # Standard similarity threshold check
            elif sim < computed_threshold:
                boundaries.append(next_verse_idx)

        return boundaries

    def _apply_size_constraints(
        self,
        boundaries: List[int],
        n_verses: int,
    ) -> List[int]:
        """
        Apply max/min chunk size constraints to boundaries.

        Args:
            boundaries: List of boundary indices
            n_verses: Total number of verses

        Returns:
            Adjusted boundary list
        """
        assert self._similarities is not None
        similarities_array = self._similarities

        adjusted = [0]

        for i in range(1, len(boundaries)):
            prev_boundary = adjusted[-1]
            current_boundary = boundaries[i]
            chunk_size = current_boundary - prev_boundary

            # If chunk is too large, split it
            if chunk_size > self.max_chunk_size:
                # Find best split point within the chunk
                # Use similarity to find natural breaks
                start_idx = prev_boundary
                while start_idx + self.max_chunk_size < current_boundary:
                    # Find the lowest similarity point within max_chunk_size range
                    search_start = start_idx
                    search_end = min(start_idx + self.max_chunk_size, current_boundary)

                    if search_end - 1 > search_start:
                        local_sims = similarities_array[search_start : search_end - 1]
                        min_sim_idx = np.argmin(local_sims) + search_start + 1
                        adjusted.append(min_sim_idx)
                        start_idx = min_sim_idx
                    else:
                        break

            # Add the original boundary if not already added
            if current_boundary not in adjusted:
                adjusted.append(current_boundary)

        return adjusted

    def create_semantic_chunks(
        self,
        verses: Optional[List[QuranChunk]] = None,
        show_progress: bool = True,
        use_cache: bool = True,
        threshold_type: str = "percentile",
    ) -> List[SemanticChunk]:
        """
        Main method to create semantic chunks from verses.

        Args:
            verses: Optional list of QuranChunk objects
            show_progress: Show progress bar
            use_cache: Use cached embeddings
            threshold_type: "percentile" (default), "gradient", "interquartile", "std", or "fixed"

        Returns:
            List of SemanticChunk objects
        """
        # Load and process
        if verses is not None:
            self._verses = verses
        elif not self._verses:
            self.load_verses(show_progress=show_progress)

        # Compute embeddings and similarities
        self.compute_embeddings(show_progress=show_progress, use_cache=use_cache)
        self.compute_similarities()

        # Detect boundaries with specified threshold type
        boundaries = self.detect_boundaries(threshold_type=threshold_type)

        assert self._similarities is not None
        similarities_array = self._similarities

        # Apply size constraints
        boundaries = self._apply_size_constraints(boundaries, len(self._verses))

        # Create chunks
        chunks: List[SemanticChunk] = []

        # Add final boundary for iteration
        boundaries_with_end = boundaries + [len(self._verses)]

        iterator = range(len(boundaries))
        if show_progress:
            iterator = tqdm(iterator, desc="Creating semantic chunks")

        for i in iterator:
            start_idx = boundaries_with_end[i]
            end_idx = boundaries_with_end[i + 1]

            chunk_verses = self._verses[start_idx:end_idx]

            if not chunk_verses:
                continue

            # Get internal similarities
            internal_sims = []
            if end_idx - start_idx > 1:
                internal_sims = similarities_array[start_idx : end_idx - 1].tolist()

            # Create chunk
            first_verse = chunk_verses[0]
            last_verse = chunk_verses[-1]

            chunk = SemanticChunk(
                chunk_id=f"{first_verse.surah_id}:{first_verse.verse_id}-{last_verse.verse_id}_semantic",
                verse_ids=[v.id for v in chunk_verses],
                surah_id=first_verse.surah_id,
                surah_name=first_verse.surah_name,
                surah_name_arabic=first_verse.surah_name_arabic,
                surah_transliteration=first_verse.surah_transliteration,
                surah_type=first_verse.surah_type,
                start_verse=first_verse.verse_id,
                end_verse=last_verse.verse_id,
                combined_translation=" ".join(v.translation for v in chunk_verses),
                combined_arabic=" ".join(v.arabic_text for v in chunk_verses),
                combined_normalized=" ".join(
                    v.translation_normalized
                    for v in chunk_verses
                    if v.translation_normalized
                ),
                combined_lemma=" ".join(
                    v.translation_lemma for v in chunk_verses if v.translation_lemma
                ),
                internal_similarities=internal_sims,
            )

            chunks.append(chunk)

        print(
            f"\nCreated {len(chunks)} semantic chunks from {len(self._verses)} verses"
        )
        print(f"Average chunk size: {len(self._verses) / len(chunks):.2f} verses")

        return chunks

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the chunking process.

        Returns:
            Dictionary with statistics
        """
        if self._similarities is None:
            return {}

        return {
            "num_verses": len(self._verses),
            "similarity_mean": float(np.mean(self._similarities)),
            "similarity_std": float(np.std(self._similarities)),
            "similarity_min": float(np.min(self._similarities)),
            "similarity_max": float(np.max(self._similarities)),
            "similarity_p10": float(np.percentile(self._similarities, 10)),
            "similarity_p25": float(np.percentile(self._similarities, 25)),
            "similarity_p50": float(np.percentile(self._similarities, 50)),
            "threshold": self.similarity_threshold,
            "max_chunk_size": self.max_chunk_size,
        }

    def save_chunks(
        self,
        chunks: List[SemanticChunk],
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Save semantic chunks to JSON file.

        Args:
            chunks: List of SemanticChunk objects
            output_path: Optional output path

        Returns:
            Path to saved file
        """
        output_path = output_path or Path("data/semantic_chunks.json")
        output_path.parent.mkdir(exist_ok=True)

        data = [chunk.to_dict() for chunk in chunks]

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"Saved {len(chunks)} chunks to {output_path}")
        return output_path

    def load_chunks(
        self,
        input_path: Optional[Path] = None,
    ) -> List[SemanticChunk]:
        """
        Load semantic chunks from JSON file.

        Args:
            input_path: Optional input path

        Returns:
            List of SemanticChunk objects
        """
        input_path = input_path or Path("data/semantic_chunks.json")

        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        chunks = []
        for item in data:
            chunk = SemanticChunk(
                chunk_id=item["chunk_id"],
                verse_ids=item["verse_ids"],
                surah_id=item["surah_id"],
                surah_name=item["surah_name"],
                surah_name_arabic=item["surah_name_arabic"],
                surah_transliteration=item["surah_transliteration"],
                surah_type=item["surah_type"],
                start_verse=item["start_verse"],
                end_verse=item["end_verse"],
                combined_translation=item["combined_translation"],
                combined_arabic=item["combined_arabic"],
                combined_normalized=item.get("combined_normalized", ""),
                combined_lemma=item.get("combined_lemma", ""),
                internal_similarities=item.get("internal_similarities", []),
            )
            chunks.append(chunk)

        print(f"Loaded {len(chunks)} chunks from {input_path}")
        return chunks


def analyze_surah_chunks(
    chunks: List[SemanticChunk],
    surah_id: int,
) -> None:
    """
    Print analysis of chunks for a specific surah.

    Args:
        chunks: List of SemanticChunk objects
        surah_id: Surah number to analyze
    """
    surah_chunks = [c for c in chunks if c.surah_id == surah_id]

    if not surah_chunks:
        print(f"No chunks found for surah {surah_id}")
        return

    print(f"\n{'=' * 60}")
    print(
        f"Surah {surah_id} - {surah_chunks[0].surah_name} ({surah_chunks[0].surah_transliteration})"
    )
    print(f"{'=' * 60}")
    print(f"Total chunks: {len(surah_chunks)}")
    print(f"Total verses: {sum(c.verse_count for c in surah_chunks)}")
    print()

    for chunk in surah_chunks:
        verse_range = (
            f"{chunk.start_verse}-{chunk.end_verse}"
            if chunk.start_verse != chunk.end_verse
            else str(chunk.start_verse)
        )
        print(f"Chunk: [{chunk.surah_id}:{verse_range}] ({chunk.verse_count} verses)")
        print(
            f"  Avg similarity: {chunk.avg_internal_similarity:.4f}"
            if chunk.internal_similarities
            else "  Single verse"
        )

        # Show first 100 chars of combined translation
        preview = (
            chunk.combined_translation[:150] + "..."
            if len(chunk.combined_translation) > 150
            else chunk.combined_translation
        )
        print(f"  Text: {preview}")
        print()


if __name__ == "__main__":
    # Test the chunker
    print("Testing Semantic Verse Chunker...")

    chunker = SemanticVerseChunker(
        similarity_threshold=0.75,
        max_chunk_size=10,
        respect_surah_boundary=True,
    )

    # Create chunks
    chunks = chunker.create_semantic_chunks(show_progress=True)

    # Print statistics
    stats = chunker.get_statistics()
    print("\nStatistics:")
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.4f}")
        else:
            print(f"  {key}: {value}")

    # Analyze first two surahs
    analyze_surah_chunks(chunks, 1)  # Fatiha
    analyze_surah_chunks(chunks, 2)  # Bakara (first chunks)

    # Save chunks
    chunker.save_chunks(chunks)
