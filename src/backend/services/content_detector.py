"""
Content detection service for identifying textbook content boundaries.

P1 Scope:
- Detect content start (skip cover/preface/TOC)
- Select complete chapters
- Handle various chapter marker patterns
"""

import re
from typing import List, Dict, Any


class ContentDetector:
    """Detect content boundaries in parsed textbook chunks."""

    def __init__(self, min_content_page: int = 10, char_jump_threshold: float = 3.0):
        """
        Initialize content detector.

        Args:
            min_content_page: Minimum page number for content start (skip cover/preface)
            char_jump_threshold: Multiplier for detecting char count jump (TOC -> content)
        """
        self.min_content_page = min_content_page
        self.char_jump_threshold = char_jump_threshold

    def detect_content_start(self, chunks: List[Dict[str, Any]]) -> int:
        """
        Detect the starting index of main content.

        Strategy:
        1. Skip pages < min_content_page (cover/copyright/preface)
        2. Look for chapter markers ("第一章", "第1章", "Chapter 1")
        3. Detect character count jump (TOC -> content transition)

        Args:
            chunks: List of parsed chunks with metadata

        Returns:
            Index of first content chunk
        """
        if not chunks:
            return 0

        # Strategy 1: Skip early pages
        for i, chunk in enumerate(chunks):
            page = chunk.get("page", 0)
            if page >= self.min_content_page:
                # Check if this chunk has a chapter marker
                if self._is_chapter_marker(chunk["content"]):
                    return i
                # Otherwise, continue to strategy 3
                break

        # Strategy 2: Look for chapter markers anywhere
        for i, chunk in enumerate(chunks):
            if self._is_chapter_marker(chunk["content"]):
                return i

        # Strategy 3: Detect character count jump
        if len(chunks) >= 3:
            for i in range(1, len(chunks)):
                prev_chars = chunks[i - 1]["char_count"]
                curr_chars = chunks[i]["char_count"]

                # Detect significant jump in character count
                if prev_chars > 0 and curr_chars > prev_chars * self.char_jump_threshold:
                    return i

        # Fallback: return first chunk after min_content_page
        for i, chunk in enumerate(chunks):
            if chunk.get("page", 0) >= self.min_content_page:
                return i

        return 0

    def select_chapter(self, chunks: List[Dict[str, Any]], chapter_num: int = 1) -> List[Dict[str, Any]]:
        """
        Select a complete chapter from chunks.

        Args:
            chunks: List of parsed chunks
            chapter_num: Chapter number to select (1-indexed)

        Returns:
            List of chunks belonging to the chapter, with chapter_title metadata added
        """
        if not chunks:
            return []

        # Find chapter boundaries
        chapter_starts = []
        for i, chunk in enumerate(chunks):
            if self._is_chapter_marker(chunk["content"]):
                chapter_starts.append(i)

        # If no chapter markers found, return all chunks with default title
        if not chapter_starts:
            default_title = f"第{chapter_num}章"
            return [
                {**chunk, "chapter_title": default_title}
                for chunk in chunks
            ]

        # Select the requested chapter
        if chapter_num > len(chapter_starts):
            # Requested chapter doesn't exist, return empty
            return []

        start_idx = chapter_starts[chapter_num - 1]
        end_idx = chapter_starts[chapter_num] if chapter_num < len(chapter_starts) else len(chunks)

        # Extract chapter title
        chapter_title = self._extract_chapter_title(chunks[start_idx]["content"])

        # Return chapter chunks with metadata
        chapter_chunks = []
        for chunk in chunks[start_idx:end_idx]:
            chapter_chunks.append({
                **chunk,
                "chapter_title": chapter_title
            })

        return chapter_chunks

    def _is_chapter_marker(self, content: str) -> bool:
        """
        Check if content contains a chapter marker.

        Patterns:
        - 第一章, 第二章, ... (Chinese)
        - 第1章, 第2章, ... (Chinese with digits)
        - Chapter 1, Chapter 2, ... (English)

        Args:
            content: Text content to check

        Returns:
            True if content starts with a chapter marker
        """
        # Get first line only
        first_line = content.split('\n')[0].strip()

        patterns = [
            r'^第[一二三四五六七八九十百]+章',  # 第一章, 第二章
            r'^第\d+章',  # 第1章, 第2章
            r'^Chapter\s+\d+',  # Chapter 1, Chapter 2
        ]

        for pattern in patterns:
            if re.match(pattern, first_line, re.IGNORECASE):
                return True

        return False

    def _extract_chapter_title(self, content: str) -> str:
        """
        Extract chapter title from content.

        Args:
            content: Text content containing chapter marker

        Returns:
            Chapter title string
        """
        # Get first line
        first_line = content.split('\n')[0].strip()

        # If first line is a chapter marker, return it
        if self._is_chapter_marker(first_line):
            return first_line

        # Otherwise, try to extract from full content
        patterns = [
            r'(第[一二三四五六七八九十百]+章[^\n]*)',
            r'(第\d+章[^\n]*)',
            r'(Chapter\s+\d+[^\n]*)',
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return "未知章节"

    def get_chapter_metadata(self, chapter_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract metadata from chapter chunks.

        Args:
            chapter_chunks: List of chunks belonging to a chapter

        Returns:
            Metadata dict with:
            - chapter_title: Chapter title
            - start_page: First page number
            - end_page: Last page number
            - chunk_count: Number of chunks
            - char_count: Total character count
        """
        if not chapter_chunks:
            return {
                "chapter_title": "未知章节",
                "start_page": 0,
                "end_page": 0,
                "chunk_count": 0,
                "char_count": 0
            }

        return {
            "chapter_title": chapter_chunks[0].get("chapter_title", "未知章节"),
            "start_page": chapter_chunks[0].get("page", 0),
            "end_page": chapter_chunks[-1].get("page", 0),
            "chunk_count": len(chapter_chunks),
            "char_count": sum(chunk["char_count"] for chunk in chapter_chunks)
        }
