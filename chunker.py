"""
Stage 2 of the pipeline: splitting documents into chunks.

⚠️ THIS IS THE FILE YOU CHANGE IN MILESTONE 3.

`split_documents` below is deliberately plain. It cuts every document into
fixed-size pieces with a fixed overlap and pays no attention to where sentences
or paragraphs end. It works, and it is not good.

On a corpus of short posts it may not cut anything at all: `campus_life` comes
out as 88 documents and 88 chunks, because almost nothing in it reaches 800
characters. That is the baseline, not a bug — Milestone 3 is where you decide
whether one post should stay one chunk.

Your job in Milestone 3 is to replace the *body* of `split_documents` with a
strategy that fits the documents you actually read in Milestone 1. Keep the
name and the shape of what it returns — the rest of the pipeline calls it, and
your README has to name the function that produced your chunks.

If you get stuck for 30 minutes, `fallback_split` is the original. Switch back
to it, write down what you saw, and move on. That's a real observation about
your pipeline, not giving up.
"""

from dataclasses import dataclass
import re

import config
from ingest import Document

MAX_CHUNK_SIZE = 800

@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str        # which file it came from
    index: int         # which chunk within that file, starting at 0
    produced_by: str   # the function that made it — cite this in your README

    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    The starter's original chunker. Fixed-size character windows with overlap.

    Keep this function. Milestone 3's stop rule points back at it, and having
    something to compare your own strategy against is useful in unit 2.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    if overlap >= chunk_size:
        raise ValueError("overlap has to be smaller than chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        start = 0
        index = 0
        while start < len(doc.text):
            piece = doc.text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::fallback_split",
                    )
                )
                index += 1
            start += chunk_size - overlap

    return chunks

def split_paragraph(
    prefix: str,
    paragraph: str,
    source: str,
    start_index: int,
) -> list[Chunk]:

    # Split after sentence-ending punctuation followed by whitespace.
    sentences = [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", paragraph.strip())
        if sentence.strip()
    ]

    chunks: list[Chunk] = []
    current_sentences: list[str] = []
    next_index = start_index

    for sentence in sentences:
        joined_sentences = " ".join(current_sentences + [sentence])
        candidate_text = f"{prefix}\n\n{joined_sentences}".strip()

        if len(candidate_text) <= MAX_CHUNK_SIZE:
            current_sentences.append(sentence)

        else:
            if current_sentences:
                current_text = (
                    f"{prefix}\n\n{' '.join(current_sentences)}"
                ).strip()

                chunks.append(
                    Chunk(
                        text=current_text,
                        source=source,
                        index=next_index,
                        produced_by="chunker.py::split_documents",
                    )
                )
                next_index += 1
                current_sentences = []

            fresh_text = f"{prefix}\n\n{sentence}".strip()

            if len(fresh_text) <= MAX_CHUNK_SIZE:
                current_sentences = [sentence]

            else:
                # Emergency fallback: one sentence alone is too long.
                available = MAX_CHUNK_SIZE - len(prefix) - 2

                if available <= 0:
                    raise ValueError("Prefix is too long to fit within the maximum chunk size.")

                start = 0
                while start < len(sentence):
                    piece = sentence[start : start + available].strip()

                    if piece:
                        chunks.append(
                            Chunk(
                                text=f"{prefix}\n\n{piece}".strip(),
                                source=source,
                                index=next_index,
                                produced_by="chunker.py::split_documents",
                            )
                        )
                        next_index += 1

                    start += available

    if current_sentences:
        current_text = (
            f"{prefix}\n\n{' '.join(current_sentences)}"
        ).strip()

        chunks.append(
            Chunk(
                text=current_text,
                source=source,
                index=next_index,
                produced_by="chunker.py::split_documents",
            )
        )

    return chunks

def process_section(
    title: str,
    heading: str,
    paragraphs: list[str],
    source: str,
    start_index: int,
    intro: str = "",
) -> list[Chunk]:
    if not paragraphs:
        return []
    
    prefix_parts = [title]

    if intro:
        prefix_parts.append(intro)

    if heading:
        prefix_parts.append(heading)

    prefix = "\n\n".join(prefix_parts).strip()

    section_text = "\n\n".join(paragraphs).strip()
    full_text = f"{prefix}\n\n{section_text}".strip()

    # If the whole sections fits, keep it together as one chunk
    if len(full_text) <= MAX_CHUNK_SIZE:
        return [
            Chunk(
                text=full_text,
                source=source,
                index=start_index,
                produced_by="chunker.py::split_documents",
            )
        ]

    chunks: list[Chunk] = []
    current_paragraphs: list[str] = []
    next_index = start_index

    for paragraph in paragraphs:
        candidate_paragraphs = current_paragraphs + [paragraph]
        joined_candidate = "\n\n".join(candidate_paragraphs)
        candidate_text = f"{prefix}\n\n{joined_candidate}".strip()

        if len(candidate_text) <= MAX_CHUNK_SIZE:
            current_paragraphs.append(paragraph)

        else:
            # Save the current chunk before starting a new one.
            if current_paragraphs:
                joined_current = "\n\n".join(current_paragraphs)
                current_text = f"{prefix}\n\n{joined_current}".strip()

                chunks.append(
                    Chunk(
                        text=current_text,
                        source=source,
                        index=next_index,
                        produced_by="chunker.py::split_documents",
                    )
                )

                next_index += 1
                current_paragraphs = []

            # Check whether this paragraph fits by itself
            fresh_text = f"{prefix}\n\n{paragraph}".strip()

            if len(fresh_text) <= MAX_CHUNK_SIZE:
                current_paragraphs = [paragraph]

            else:
                # If one paragraph is still too large, split it at sentence boundaries.
                sentence_chunks = split_paragraph(
                    prefix=prefix,
                    paragraph=paragraph,
                    source=source,
                    start_index=next_index,
                )

                chunks.extend(sentence_chunks)
                next_index += len(sentence_chunks)

    # Save any remaining paragraphs after the loop
    if current_paragraphs:
        joined_current = "\n\n".join(current_paragraphs)
        current_text = f"{prefix}\n\n{joined_current}".strip()

        chunks.append(
            Chunk(
                text=current_text,
                source=source,
                index=next_index,
                produced_by="chunker.py::split_documents",
            )
        )

    return chunks

def split_documents(documents: list[Document]) -> list[Chunk]:
    """
    Split documents into chunks. ⚠️ REPLACE THE BODY OF THIS IN MILESTONE 3.

    Right now it just calls the fallback. That is the plain, generic behaviour
    the brief is talking about.

    When you write your own strategy, set `produced_by` to
    "chunker.py::split_documents" so your README's Sample Chunks section names
    the right function. `app.py chunks` prints that string for you.

    Things worth thinking about before you write any code:
      - Are your documents short posts or long guides?
      - Is the useful information in one sentence, or spread over a paragraph?
      - Would splitting on paragraph breaks keep more thoughts intact than
        splitting on a character count?
    """
    
    chunks: list[Chunk] = []

    for doc in documents:
        lines = doc.text.splitlines()

        title = ""
        intro_lines: list[str] = []

        current_heading = ""
        current_section_lines: list[str] = []

        sections: list[tuple[str, list[str]]] = []

        found_first_section = False

        for line in lines:
            stripped = line.strip()

            # Document title
            if stripped.startswith("# "):
                title = stripped
                continue

            # New section
            if stripped.startswith("## "):
                if current_heading:
                    sections.append(
                        (current_heading, current_section_lines)
                    )

                current_heading = stripped
                current_section_lines = []
                found_first_section = True
                continue

            # Content before the first ## heading is introductory material.
            if not found_first_section:
                intro_lines.append(line)
            else:
                current_section_lines.append(line)

        # Don't forget the final section.
        if current_heading:
            sections.append(
                (current_heading, current_section_lines)
            )

        intro = "\n".join(intro_lines).strip()
        next_index = 0

        for section_number, (heading, section_lines) in enumerate(sections):
            section_text = "\n".join(section_lines).strip()

            # Blank lines separate paragraphs.
            paragraphs = [
                paragraph.strip()
                for paragraph in section_text.split("\n\n")
                if paragraph.strip()
            ]

            section_intro = intro if section_number == 0 else ""

            section_chunks = process_section(
                title=title,
                heading=heading,
                paragraphs=paragraphs,
                source=doc.source,
                start_index=next_index,
                intro=section_intro,
            )

            chunks.extend(section_chunks)
            next_index += len(section_chunks)

    return chunks


def describe(chunks: list[Chunk]) -> str:
    """A one-line summary, printed after indexing."""
    if not chunks:
        return "0 chunks"
    lengths = [len(c.text) for c in chunks]
    return (
        f"{len(chunks)} chunks, "
        f"{sum(lengths) // len(lengths)} characters on average "
        f"(shortest {min(lengths)}, longest {max(lengths)}), "
        f"produced by {chunks[0].produced_by}"
    )


if __name__ == "__main__":
    from ingest import load_documents

    chunks = split_documents(load_documents())
    print(describe(chunks))
