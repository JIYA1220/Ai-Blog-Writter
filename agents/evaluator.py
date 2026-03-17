# agents/evaluator.py
# ============================================================
# AI Blog Writer — Evaluator Node (LLM-as-Judge)
# Critiques the final blog based on tone, audience, and content.
# Provides a score and suggestions for improvement.
# ============================================================

import json
from utils.llm import get_llm
from utils.logger import log_stage, log_info, log_success
from schemas.models import BlogEvaluation, AIBlogWriterState

EVALUATOR_PROMPT = """You are a senior editor. Evaluate the following blog post.

Topic: {topic}
Target Audience: {audience}
Requested Tone: {tone}

Blog Content:
{content}

Evaluate based on:
1. Relevance to topic and audience.
2. Adherence to the requested tone.
3. Logical flow and structure.
4. Depth of information and factual grounding (if applicable).

Respond ONLY with valid JSON:
{{
  "score": (int 1-10),
  "reasoning": "detailed explanation of the score",
  "suggestions": ["suggestion 1", "suggestion 2"],
  "is_pass": true/false (true if score >= 7)
}}
"""

async def evaluator_node(state: AIBlogWriterState) -> dict:
    """
    Evaluator Node — LLM-as-judge.
    Critiques the final blog and provides a score.
    """
    final_blog = state.get("final_blog")
    if not final_blog or not final_blog.full_content:
        return {"evaluation": None}

    log_stage("EVALUATOR", "Evaluating final blog quality...")

    llm = get_llm(temperature=0.1)
    prompt = EVALUATOR_PROMPT.format(
        topic=state["topic"],
        audience=state.get("target_audience", "general readers"),
        tone=state.get("tone", "informative"),
        content=final_blog.full_content[:4000]  # Cap context for evaluation
    )

    try:
        response = await llm.ainvoke(prompt)
        raw = response.content.strip()

        # Clean markdown fences
        if raw.startswith("```"):
            lines = raw.splitlines()
            if lines[0].startswith("```"):
                raw = "\n".join(lines[1:-1])
        raw = raw.strip()
        if raw.startswith("json"):
            raw = raw[4:].strip()

        data = json.loads(raw)
        
        evaluation = BlogEvaluation(
            score=data.get("score", 0),
            reasoning=data.get("reasoning", "No reasoning provided"),
            suggestions=data.get("suggestions", []),
            is_pass=data.get("is_pass", False)
        )

        if evaluation.is_pass:
            log_success(f"Evaluation PASSED (Score: {evaluation.score}/10)")
        else:
            log_stage("EVALUATOR", f"Evaluation FAILED (Score: {evaluation.score}/10)", style="bold yellow")

        return {"evaluation": evaluation}

    except Exception as e:
        log_stage("EVALUATOR", f"Evaluation failed: {e}", style="bold red")
        return {"evaluation": None, "errors": [f"Evaluator error: {str(e)}"]}
