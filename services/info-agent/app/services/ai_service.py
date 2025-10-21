
import logging
import httpx
import redis
import traceback
from ..config import settings

logger = logging.getLogger(__name__)

try:
    from langchain_redis import RedisChatMessageHistory
    from langchain.memory import ConversationBufferMemory
except ImportError:
    RedisChatMessageHistory = None
    ConversationBufferMemory = None
    logger.warning("langchain or langchain-redis not installed; Redis memory functionality will be disabled")

class AIService:
    """Service for handling AI/LLM interactions with Ollama and Redis-based memory"""

    def __init__(self, session_id: str = "default"):
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model
        self.temperature = settings.ollama_temperature
        self.redis_url = settings.redis_url
        self.session_id = session_id
        self.system_prompt = settings.system_prompt
        self._memory = None
        # Adaptive summarization parameters (now from settings)
        self.token_budget = getattr(settings, "token_budget", 8192)
        self.summary_token_budget = getattr(settings, "summary_token_budget", 1000)
        self.recent_messages_to_keep = getattr(settings, "recent_messages_window", 6) or 6
        self.messages_to_summarize = getattr(settings, "messages_to_summarize", 10)
        self.summarization_prompt_tokens = getattr(settings, "summarization_prompt_tokens", 100)
        # Internal conversation representation (list of {role, content})
        self.message_summary_char_limit = getattr(settings, "message_summary_char_limit", 600)
        self.conversation_history = []
        if not self.redis_url:
            logger.warning("No Redis URL found for AI service; memory will be disabled")
        else:
            logger.info(f"Using Redis URL: {self.redis_url}")

    @property
    def memory(self):
        """Lazy initialization of Redis-based memory"""
        if self._memory is None and RedisChatMessageHistory is not None and ConversationBufferMemory is not None:
            try:
                logger.info("Initializing Redis-based memory")
                logger.debug(f"Redis URL: {self.redis_url}")
                logger.debug(f"Session ID: {self.session_id}")
                chat_history = RedisChatMessageHistory(
                    session_id=self.session_id,
                    redis_url=self.redis_url
                )
                logger.info("Redis chat history initialized")
                self._memory = ConversationBufferMemory(
                    memory_key="chat_history",
                    chat_memory=chat_history,
                    return_messages=True
                )
                logger.info("Conversation buffer memory initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Redis memory: {str(e)}")
                logger.warning("Continuing without memory functionality")
                self._memory = None
        return self._memory

    async def generate_response(self, question: str, language: str = None) -> str:
        """Generate AI response using the system prompt, adaptive summarization, and last N messages.

        Adaptive summarization logic:
        - Maintain a running conversation_history (rebuilt from Redis each call)
        - If token usage exceeds (token_budget - summary_token_budget - summarization_prompt_tokens),
          summarize oldest messages_to_summarize into a system summary message and replace them.
        - Always include system prompt, any summary system message, and the last `recent_messages_to_keep` messages.
        """
        try:
            if language is None:
                language = getattr(settings, "default_language", "english")
            logger.info(f"Generating response for question: {question[:50]} in language: {language}")
            # Construct prompt based on language
            prompt = f"Answer briefly in {language}: {question}"

            logger.debug(f"Using prompt: {prompt}")

            # Get messages from memory
            history_messages = []
            if self.memory is not None and hasattr(self.memory, "chat_memory") and hasattr(self.memory.chat_memory, "messages"):
                for m in self.memory.chat_memory.messages:
                    if hasattr(m, "type") and hasattr(m, "content"):
                        if m.type == "human":
                            history_messages.append({"role": "user", "content": m.content})
                        elif m.type == "ai":
                            history_messages.append({"role": "assistant", "content": m.content})

            # Rebuild internal conversation history from Redis memory
            self.conversation_history = history_messages

            # Apply adaptive summarization if needed
            await self._apply_adaptive_summarization(language)


            # Prepare final context messages
            messages = self._prepare_context_messages(prompt)

            payload = {
                "model": self.model,
                "temperature": self.temperature,
                "messages": messages,
                "options": {
                    "num_ctx": self.token_budget
                }
            }
            logger.debug(f"Payload for Ollama: {payload}")

            content = await self._call_ollama_api(payload)
            if content is None:
                return "[Error: Exception during Ollama API call]"

            # Save to Redis memory
            self._save_to_memory(prompt, content)

            logger.info(f"Generated AI response for question: {question[:50]}...")

            logger.debug(f"AI response: {content}")

            return content

        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            logger.error(traceback.format_exc())
            return "[Error: Unable to get response from Ollama LLM]"


    def is_available(self) -> bool:
        try:
            resp = httpx.get(f"{self.base_url}/v1/models", timeout=5)
            return resp.status_code == 200
        except Exception:
            return False

    # -------------------- Adaptive Summarization Helpers --------------------
    def _estimate_token_count(self, text: str) -> int:
        """Rough token estimation (1 token ~= 4 characters)."""
        return max(1, len(text) // 4)

    def _is_summarization_needed(self) -> bool:
        """Determine if summarization threshold has been exceeded for the oldest messages to summarize."""
        messages_to_check = self._get_messages_to_summarize()
        text_to_check = self.system_prompt + " " + " ".join([m.get("content", "") for m in messages_to_check])
        total_tokens = self._estimate_token_count(text_to_check)
        threshold = self.token_budget - self.summary_token_budget - self.summarization_prompt_tokens
        logger.debug(f"Adaptive summary check (oldest messages): total_tokens={total_tokens} threshold={threshold}")
        return total_tokens > threshold

    def _get_messages_to_summarize(self):
        return self.conversation_history[:self.messages_to_summarize]

    async def _summarize_messages(self, messages, language=None):
        if not messages:
            return "Summary: (no content)"
        # Prepare transcript for LLM summarization
        transcript = "\n".join([f"{m.get('role','user')}: {m.get('content','')[:self.message_summary_char_limit]}" for m in messages])
        lang = language or getattr(settings, "default_language", "english")
        system_prompt = (
            f"You are an assistant that summarizes a conversation in {lang}. Include user intents, key information provided, and next recommended action. "
            f"Maximum {self.summary_token_budget} tokens. Do not fabricate details. Respond with only the summary."
        )
        user_intro = "Conversation transcript:"
        payload = {
            "model": self.model,
            "temperature": 0.0,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"{user_intro}\n{transcript}"}
            ],
            "options": {
                "num_ctx": self.token_budget
            }
        }
        summary = await self._call_ollama_api(payload)
        logger.debug("Generated LLM summary.")
        return f"Summary: {summary.strip() if summary else '(no content)'}"

    async def _apply_adaptive_summarization(self, language=None):
        """Replace oldest messages with a system summary if needed."""
        try:
            if not self.conversation_history:
                return
            if self._is_summarization_needed():
                to_summarize = self._get_messages_to_summarize()
                summary_text = await self._summarize_messages(to_summarize, language)
                # Replace the first block with a system summary message
                self.conversation_history = ([{"role": "system", "content": summary_text}] +
                                             self.conversation_history[self.messages_to_summarize:])
                logger.info("Applied adaptive summarization to conversation history.")
        except Exception as e:
            logger.warning(f"Adaptive summarization failed: {e}")

    def _prepare_context_messages(self, prompt):
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        # Include any system summary message (role == system) produced by summarization
        for msg in self.conversation_history:
            if msg.get("role") == "system" and msg.get("content", "").startswith("Summary:"):
                messages.append(msg)
                break  # Only include the first summary system message
        # Append last N recent messages
        recent_slice = self.conversation_history[-self.recent_messages_to_keep:]
        messages.extend(recent_slice)
        # Add current user prompt
        messages.append({"role": "user", "content": prompt})
        return messages
    
    async def _call_ollama_api(self, payload):
        logger.debug("Sending request to Ollama API")
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(f"{self.base_url}/v1/chat/completions", json=payload)
                response.raise_for_status()
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                logger.debug("Received response from Ollama")
                return content
        except httpx.HTTPStatusError as http_err:
            logger.error(f"HTTP error from Ollama: {http_err.response.status_code} {http_err.response.text}")
            logger.error(traceback.format_exc())
            return None
        except Exception as api_exc:
            logger.error(f"Exception during Ollama API call: {str(api_exc)}")
            logger.error(traceback.format_exc())
            return None
    
    def _save_to_memory(self, prompt, content):
        logger.debug("Saving conversation to Redis memory")
        if self.memory is not None:
            try:
                logger.debug("Memory is available, saving context")
                self.memory.save_context({"input": prompt}, {"output": content})
                logger.debug("Successfully saved conversation to Redis memory")
            except Exception as memory_error:
                logger.warning(f"Failed to save conversation to Redis memory: {str(memory_error)}")
        else:
            logger.debug("No memory available; skipping save to Redis")
