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
            "errors": [],
        }
        
        # Progress Tracking
        progress_bar = st.progress(0, "Initializing pipeline...")
        status_text = st.empty()
        
        try:
            # Stage 1: Router
            status_text.text("Analyzing topic (Routing)...")
            progress_bar.progress(15)
            
            # Since LangGraph execution is typically a single call, 
            # we'll use streaming if possible, but for simplicity here 
            # we invoke the graph and show progress updates.
            
            start_time = time.time()
            
            # Use streaming to get updates
            final_state = None
            for event in ai_blog_writer_graph.stream(inputs, config={"recursion_limit": 50}):
                # Update progress based on node events
                for node_name, state_update in event.items():
                    if node_name == "router":
                        status_text.text("Researching (Retriever)..." if state_update.get("needs_retrieval") else "Planning (Planner)...")
                        progress_bar.progress(30)
                    elif node_name == "retriever":
                        status_text.text("Planning (Planner)...")
                        progress_bar.progress(50)
                    elif node_name == "planner":
                        status_text.text("Writing Sections (Parallel Writers)...")
                        progress_bar.progress(70)
                    elif node_name == "section_writer":
                        # Parallel workers don't stream one by one in a way that's easy to count here 
                        # without more complex logic, but we can show they are working.
                        status_text.text("Finalizing sections...")
                        progress_bar.progress(85)
                    elif node_name == "reducer":
                        status_text.text("Assembling final blog...")
                        progress_bar.progress(95)
                
                # Keep track of latest state
                final_state = event
            
            # Final result is in the last emitted event's state
            # LangGraph stream emits {node: update}
            # To get the full final state, we should invoke or accumulate
            final_state = ai_blog_writer_graph.invoke(inputs)
            
            elapsed = time.time() - start_time
            progress_bar.progress(100)
            status_text.success(f"Generation complete in {elapsed:.1f}s!")
            
            final_blog = final_state.get("final_blog")
            if final_blog:
                st.divider()
                st.subheader(final_blog.title)
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
