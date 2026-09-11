import os
from typing import List, Dict, Any, Tuple
from google import genai
from google.genai import types

from app.core.config import settings
from app.utils.logging_config import logger

class GenerationService:
    def __init__(
        self,
        model_name: str = getattr(settings, "GEMINI_MODEL", "gemini-3.6-flash"),
        api_key: str = getattr(settings, "GEMINI_API_KEY", ""),
    ):
        self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")

        if not self.api_key:
            logger.warning("GEMINI_API_KEY is not set in environment or settings!")
        else:
            logger.info("Initializing Google GenAI Client with configured API key...")

        self.client = genai.Client(api_key=self.api_key) if self.api_key else None

    def generate_answer(
        self,
        question: str,
        context_chunks: List[Dict[str, Any]]
    ) -> Tuple[str, List[str]]:
        """Generate a grounded answer based strictly on retrieved context chunks using Gemini."""
        if not context_chunks:
            logger.info("No context chunks provided to GenerationService.")
            return (
                "I am sorry, but no relevant information was found in the document repository to answer your question.",
                []
            )

        if not self.client:
            # Attempt to re-read key dynamically from environment
            current_key = os.getenv("GEMINI_API_KEY", "")
            if current_key:
                self.api_key = current_key
                self.client = genai.Client(api_key=self.api_key)
            else:
                raise RuntimeError("GEMINI_API_KEY is missing. Please set GEMINI_API_KEY in your .env file.")

        # Build context blocks and gather unique source names
        context_blocks = []
        sources_set = set()

        for idx, chunk in enumerate(context_chunks, start=1):
            source_name = chunk.get("source", "Unknown")
            sources_set.add(source_name)
            page_info = f", Page {chunk.get('page')}" if chunk.get('page') else ""
            context_blocks.append(
                f"[Source {idx}: {source_name}{page_info}]\n{chunk.get('text', '').strip()}"
            )

        context_text = "\n\n".join(context_blocks)
        unique_sources = sorted(list(sources_set))

        system_prompt = (
            "You are an expert plant pathology and crop health AI assistant. "
            "Your task is to answer the user's question using ONLY the information "
            "contained in the provided context.\n\n"

            "Grounding rules:\n"
            "1. Use only facts explicitly supported by the provided context.\n"
            "2. Do not use your own knowledge, assumptions, or outside information.\n"
            "3. Do not infer a diagnosis, treatment, cause, or recommendation unless it "
            "is explicitly supported by the context.\n"
            "4. If the context does not contain enough information to answer the question, "
            "respond exactly with: "
            "\"The provided context does not contain enough information to answer this question.\"\n"
            "5. Do not contradict the provided context.\n"
            "6. When possible, mention the relevant source name and page number from the context.\n"
            "7. Answer the question directly and concisely.\n"
            "8. Do not mention these instructions or the internal retrieval process."
        )

        user_prompt = f"""
        Context:
        {context_text}

        Question:
        {question}

        Answer:
        """

        # Print Question, Prompt, and Context to console as requested
        print("\n" + "="*80)
        print("[USER QUESTION]:", question)
        print("="*80)
        print("[PROMPT SENT TO GEMINI]:")
        try:
            print(user_prompt.strip())
        except UnicodeEncodeError:
            print(user_prompt.strip().encode("ascii", errors="replace").decode("ascii"))
        print("="*80 + "\n")

        # Attempt generation with retry and fallback models across active Gemini models
        candidate_models = [self.model_name, "gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-3.6-flash"]
        # Remove duplicates while preserving order
        candidate_models = list(dict.fromkeys([m for m in candidate_models if m]))

        last_error = None
        for m in candidate_models:
            for attempt in range(2):
                try:
                    logger.info(f"Calling Gemini model '{m}' (attempt {attempt + 1})...")
                    response = self.client.models.generate_content(
                        model=m,
                        contents=user_prompt,
                        config=types.GenerateContentConfig(
                            system_instruction=system_prompt,
                            temperature=0.0,
                        )
                    )
                    answer_text = response.text.strip() if response.text else "No response generated."

                    # Print generated answer and sources to console
                    print("\n" + "="*80)
                    print("[GENERATED ANSWER]:")
                    try:
                        print(answer_text)
                    except UnicodeEncodeError:
                        print(answer_text.encode("ascii", errors="replace").decode("ascii"))
                    print("="*80)
                    print("[SOURCES]:", unique_sources)
                    print("="*80 + "\n")

                    return answer_text, unique_sources
                except Exception as e:
                    last_error = e
                    logger.warning(f"Error calling {m} (attempt {attempt + 1}): {e}")
                    import time
                    time.sleep(1)

        logger.error(f"All Gemini generation attempts failed: {last_error}")
        raise RuntimeError(f"Gemini generation failed: {last_error}")
