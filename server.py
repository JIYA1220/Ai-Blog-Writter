# server.py
# ============================================================
# AI Blog Writer — FastAPI Server
# Exposes the LangGraph pipeline as a production-ready API.
# Supports async execution and structured I/O.
# ============================================================

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from graph import ai_blog_writer_graph
import uuid

app = FastAPI(
    title="AI Blog Writer API",
    description="Agentic Blog Generation System via LangGraph",
    version="2.0.0"
)

class BlogRequest(BaseModel):
    topic: str
    target_audience: str = "general readers"
    tone: str = "informative and engaging"

class BlogResponse(BaseModel):
    run_id: str
    title: str
    content: str
    score: Optional[int]
    evaluation: Optional[str]
    word_count: int

@app.get("/")
async def root():
    return {"status": "online", "message": "AI Blog Writer API is ready."}

@app.post("/generate", response_model=BlogResponse)
async def generate_blog(request: BlogRequest):
    """
    Triggers the full agentic pipeline to generate a blog.
    """
    inputs = {
        "topic": request.topic,
        "target_audience": request.target_audience,
        "tone": request.tone,
        "needs_retrieval": False,
        "retrieval_results": None,
        "blog_plan": None,
        "written_sections": [],
        "final_blog": None,
        "evaluation": None,
        "errors": [],
    }
    
    try:
        # Run the graph asynchronously
        final_state = await ai_blog_writer_graph.ainvoke(
            inputs,
            config={"recursion_limit": 50, "max_concurrency": 4}
        )
        
        final_blog = final_state.get("final_blog")
        evaluation = final_state.get("evaluation")
        
        if not final_blog:
            raise HTTPException(status_code=500, detail="Generation failed to produce content.")
            
        return BlogResponse(
            run_id=str(uuid.uuid4()),
            title=final_blog.title,
            content=final_blog.full_content,
            score=evaluation.score if evaluation else None,
            evaluation=evaluation.reasoning if evaluation else None,
            word_count=final_blog.total_words
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
