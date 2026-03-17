import streamlit as st
import os
import time
from datetime import datetime
from dotenv import load_dotenv
from graph import ai_blog_writer_graph
from pathlib import Path

# Configuration
load_dotenv()
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Sidebar: Past Blogs Browser ──
def sidebar_blog_browser():
    st.sidebar.title("Past Blogs")
    
    # Get all markdown files in output directory
    files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".md")]
    files.sort(key=lambda x: os.path.getmtime(os.path.join(OUTPUT_DIR, x)), reverse=True)
    
    if not files:
        st.sidebar.info("No blogs generated yet.")
        return None
    
    search_query = st.sidebar.text_input("Search", placeholder="Topic...")
    
    filtered_files = [f for f in files if search_query.lower() in f.lower()]
    
    st.sidebar.divider()
    
    for f in filtered_files:
        clean_name = f.replace(".md", "").replace("_", " ").title()
        if st.sidebar.button(f"{clean_name}", key=f, use_container_width=True):
            return f
    return None

# ── Main Header ──
st.set_page_config(page_title="AI Blog Writer", page_icon=None, layout="wide")

selected_blog = sidebar_blog_browser()

st.title("AI Blog Writer")
st.caption("Production-Grade Agentic Blog Generation System • LangGraph • Ollama • OpenRouter • Tavily")

# ── Main Generation Form ──
with st.container(border=True):
    col1, col2 = st.columns([2, 1])
    
    with col1:
        topic = st.text_input("Blog Topic", placeholder="e.g., The Future of Quantum Computing in 2025")
        audience = st.text_input("Target Audience", placeholder="e.g., tech-curious professionals")
    
    with col2:
        tone = st.selectbox("Choose Tone", [
            "informative and engaging",
            "conversational and friendly",
            "technical and precise",
            "bold and opinionated"
        ])
        start_btn = st.button("Generate Blog", use_container_width=True, type="primary")

import asyncio

# ── Execution Logic ──
if start_btn:
    if not topic or not audience:
        st.error("Please provide both a topic and a target audience.")
    else:
        # Initial State
        inputs = {
            "topic": topic,
            "target_audience": audience,
            "tone": tone,
            "needs_retrieval": False,
            "retrieval_results": None,
            "blog_plan": None,
            "written_sections": [],
            "final_blog": None,
            "evaluation": None,
            "errors": [],
        }
        
        # Progress Tracking
        progress_bar = st.progress(0, "Initializing pipeline...")
        status_text = st.empty()
        
        try:
            start_time = time.time()
            
            # Since Streamlit doesn't support async naturally in this context,
            # we use asyncio.run to execute the async pipeline.
            
            status_text.text("Running pipeline (Async)...")
            progress_bar.progress(50)
            
            final_state = asyncio.run(ai_blog_writer_graph.ainvoke(
                inputs, 
                config={"recursion_limit": 50, "max_concurrency": 4}
            ))
            
            elapsed = time.time() - start_time
            progress_bar.progress(100)
            status_text.success(f"Generation complete in {elapsed:.1f}s!")
            
            final_blog = final_state.get("final_blog")
            if final_blog:
                st.divider()
                st.subheader(final_blog.title)
                
                # Show Evaluation in an expander
                eval_data = final_state.get("evaluation")
                if eval_data:
                    with st.expander(f"Editor's Evaluation (Score: {eval_data.score}/10)", expanded=eval_data.is_pass):
                        st.write(f"**Reasoning:** {eval_data.reasoning}")
                        if eval_data.suggestions:
                            st.write("**Suggestions for improvement:**")
                            for s in eval_data.suggestions:
                                st.write(f"- {s}")
                
                st.markdown(final_blog.full_content)
                
                # Download Button
                filename = topic.lower().replace(" ", "_").replace("/", "_")[:50] + ".md"
                st.download_button(
                    label="Download Markdown",
                    data=final_blog.full_content,
                    file_name=filename,
                    mime="text/markdown"
                )
            else:
                st.error("Generation failed to produce a final blog. Check your API keys and logs.")
                
        except Exception as e:
            st.error(f"Pipeline error: {str(e)}")
            st.info("Check if your API keys are correctly set in the .env file.")

# ── Display Selected Blog from Sidebar ──
elif selected_blog:
    filepath = os.path.join(OUTPUT_DIR, selected_blog)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    st.divider()
    st.markdown(content)
    
    # Download Button for existing blog
    st.download_button(
        label="Download Markdown",
        data=content,
        file_name=selected_blog,
        mime="text/markdown"
    )
