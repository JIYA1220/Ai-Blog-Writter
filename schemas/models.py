# schemas/models.py
# ============================================================
# AI Blog Writer — Pydantic Schemas
# Every node's input/output is validated against these models.
# Nothing malformed leaks through the pipeline.
# ============================================================

from __future__ import annotations
from typing import Annotated, List, Literal, Optional
import operator
from pydantic import BaseModel, Field


# ─────────────────────────────────────────────
# 1. SECTION PLAN — Output of the Planner node
# ─────────────────────────────────────────────
class SectionPlan(BaseModel):
    """Defines what one blog section should contain."""
    section_id: int = Field(..., description="Unique index for ordering")
    title: str = Field(..., description="Section heading")
    goal: str = Field(..., description="What this section must achieve")
    constraints: List[str] = Field(default_factory=list, description="Rules the writer must follow")
    word_budget: int = Field(default=300, description="Max words for this section")
    requires_retrieval: bool = Field(default=False, description="Does this section need grounded facts?")


# ─────────────────────────────────────────────
# 2. BLOG PLAN — Full outline from the Planner
# ─────────────────────────────────────────────
class BlogPlan(BaseModel):
    """The structured plan for the entire blog post."""
    topic: str
    target_audience: str
    tone: str = Field(default="informative and engaging")
    sections: List[SectionPlan] = Field(default_factory=list)
    total_word_budget: int = Field(default=1500)


# ─────────────────────────────────────────────
# 3. RETRIEVAL RESULT — Output of the Retriever
# ─────────────────────────────────────────────
class RetrievalResult(BaseModel):
    """Deduplicated evidence gathered from web search."""
    query: str
    snippets: List[str] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)
    is_grounded: bool = Field(default=True)


# ─────────────────────────────────────────────
# 4. WRITTEN SECTION — Output of each worker
# ─────────────────────────────────────────────
class WrittenSection(BaseModel):
    """A single completed blog section from a parallel worker."""
    section_id: int
    title: str
    content: str
    word_count: int
    is_valid: bool = Field(default=True)


# ─────────────────────────────────────────────
# 5. FINAL BLOG — Output of the Reducer node
# ─────────────────────────────────────────────
class FinalBlog(BaseModel):
    """The assembled, validated final blog post."""
    title: str
    full_content: str
    total_words: int
    sections_count: int
    is_production_ready: bool = Field(default=False)


# ─────────────────────────────────────────────
# 6. EVALUATION — Output of the Evaluator node
# ─────────────────────────────────────────────
class BlogEvaluation(BaseModel):
    """LLM-as-judge evaluation of the blog."""
    score: int = Field(..., description="Score from 1 to 10")
    reasoning: str = Field(..., description="Explanation for the score")
    suggestions: List[str] = Field(default_factory=list, description="Ways to improve")
    is_pass: bool = Field(default=True)


# ─────────────────────────────────────────────
# 7. LANGGRAPH STATE — Shared state across all nodes
# ─────────────────────────────────────────────
from typing import TypedDict


class AIBlogWriterState(TypedDict):
    # Input
    topic: str
    target_audience: str
    tone: str

    # Router decision
    needs_retrieval: bool

    # Retrieval layer
    retrieval_results: Optional[RetrievalResult]

    # Planning layer
    blog_plan: Optional[BlogPlan]

    # Parallel workers write into this list (reducer = operator.add)
    written_sections: Annotated[List[WrittenSection], operator.add]

    # Final output
    final_blog: Optional[FinalBlog]

    # Evaluation loop
    evaluation: Optional[BlogEvaluation]

    # Error tracking
    errors: Annotated[List[str], operator.add]
