# agents/reducer.py
# ============================================================
# AI Blog Writer — Reducer Node
# Merges all parallel section outputs DETERMINISTICALLY.
# Sorts by section_id, assembles markdown, validates output.
# This is where the blog becomes a real document.
# ============================================================

import os
from utils.logger import log_stage, log_info, log_success, log_warning, log_final_blog
from schemas.models import WrittenSection, FinalBlog, AIBlogWriterState


def reducer_node(state: AIBlogWriterState) -> dict:
    """
    Reducer Node — final step in the DAG.
    Collects all written sections, sorts them, merges into one blog.
    Validates the output against FinalBlog schema.
    """
    log_stage("REDUCER", "Merging parallel section outputs")

    written_sections: list[WrittenSection] = state.get("written_sections", [])

    if not written_sections:
        log_warning("No sections to reduce — something went wrong upstream")
        empty = FinalBlog(
            title=state.get("topic", "Untitled"),
            full_content="[No content generated]",
            total_words=0,
            sections_count=0,
            is_production_ready=False
        )
        return {"final_blog": empty}

    # ── Step 1: Sort sections by section_id (deterministic order) ──
    valid_sections = [s for s in written_sections if s.is_valid]
    invalid_sections = [s for s in written_sections if not s.is_valid]

    sorted_sections = sorted(valid_sections, key=lambda s: s.section_id)

    if invalid_sections:
        log_warning(f"{len(invalid_sections)} section(s) failed and were excluded")

    log_info(f"Merging {len(sorted_sections)} valid sections")

    # ── Step 2: Build the blog title ──
    topic = state.get("topic", "Untitled")
    blog_plan = state.get("blog_plan")
    tone = blog_plan.tone if blog_plan else "informative"

    blog_title = _build_title(topic, tone)

    # ── Step 3: Assemble markdown content ──
    markdown_parts = [f"# {blog_title}\n"]

    # Add sources section if retrieval was used
    retrieval = state.get("retrieval_results")
    if retrieval and retrieval.sources:
        markdown_parts.append(f"> *This article is grounded with verified sources.*\n")

    for section in sorted_sections:
        markdown_parts.append(f"\n## {section.title}\n")
        markdown_parts.append(section.content)
        markdown_parts.append("\n")

    # Add sources at the bottom
    if retrieval and retrieval.sources:
        markdown_parts.append("\n---\n## Sources\n")
        for i, source in enumerate(retrieval.sources[:5], 1):
            markdown_parts.append(f"{i}. {source}\n")

    full_content = "\n".join(markdown_parts)
    total_words = sum(s.word_count for s in sorted_sections)

    # ── Step 4: Validate with Pydantic ──
    is_production_ready = (
        len(sorted_sections) >= 3
        and total_words >= 400
        and all(s.word_count > 50 for s in sorted_sections)
    )

    final_blog = FinalBlog(
        title=blog_title,
        full_content=full_content,
        total_words=total_words,
        sections_count=len(sorted_sections),
        is_production_ready=is_production_ready
    )

    # ── Step 5: Save to output file ──
    _save_blog(final_blog, topic)

    log_final_blog(blog_title, total_words, len(sorted_sections))

    if not is_production_ready:
        log_warning("Blog did not meet production threshold (need 3+ sections, 400+ words)")

    return {"final_blog": final_blog}


def _build_title(topic: str, tone: str) -> str:
    """Builds a clean title from the topic."""
    # Capitalize properly
    title = topic.strip()
    if not title[0].isupper():
        title = title.title()
    return title


def _save_blog(blog: FinalBlog, topic: str):
    """Saves the final blog to the output/ directory as a markdown file."""
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)

    # Clean filename
    filename = topic.lower().replace(" ", "_").replace("/", "_")[:50] + ".md"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(blog.full_content)

    log_success(f"Blog saved → output/{filename}")
