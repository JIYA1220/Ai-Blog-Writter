# utils/llm.py
# ============================================================
# AI Blog Writer — LLM Client via OpenRouter
# OpenRouter is OpenAI-compatible, so we use langchain-openai.
# It routes to 100+ models (including FREE ones).
# ============================================================

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama

load_dotenv()

# Enable LangSmith Tracing if API key is present
if os.getenv("LANGSMITH_API_KEY"):
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
    os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGSMITH_PROJECT", "ai-blog-writer")


def get_llm(temperature: float = 0.7):
    """
    Returns an LLM client based on MODEL_NAME.
    Supports Google Gemini, OpenRouter, and local Ollama.
    """
    model = os.getenv("MODEL_NAME", "gemini-1.5-flash")

    # Support local Ollama models (e.g., MODEL_NAME=ollama/llama3)
    if model.startswith("ollama/"):
        ollama_model = model.replace("ollama/", "")
        return ChatOllama(
            model=ollama_model,
            temperature=temperature,
        )

    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("OPENROUTER_API_KEY")

    if not api_key or api_key == "your_gemini_api_key_here":
        raise ValueError(
            "❌ API KEY not set!\n"
            "   To use local Ollama: set MODEL_NAME=ollama/your-model (e.g., ollama/qwen2.5:7b)\n"
            "   To use Cloud: set GOOGLE_API_KEY or OPENROUTER_API_KEY"
        )

    return ChatGoogleGenerativeAI(
        model=model,
        google_api_key=api_key,
        temperature=temperature,
        max_tokens=4096,
    )
