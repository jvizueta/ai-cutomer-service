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
        self.num_of_recent_messages_to_keep = getattr(settings, "recent_messages_window", 6) or 6
        self.num_of_messages_to_summarize = getattr(settings, "messages_to_summarize", 10)
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

            msgs_to_summarize = self._build_msgs_to_summarize()
            logger.debug(f"Messages to summarize count: {len(msgs_to_summarize)}")
            logger.debug(f"Messages to summarize: {msgs_to_summarize}")
            context_messages = self._get_context_messages()
            logger.debug(f"Context messages count: {len(context_messages)}")
            logger.debug(f"Context messages: {context_messages}")

            is_summarization_needed = self._is_summarization_needed(context_messages)
            logger.debug(f"Is summarization needed: {is_summarization_needed}")
            if is_summarization_needed:
                summary_text = await self._summarize_messages(msgs_to_summarize, language)
                logger.debug(f"Generated summary text: {summary_text}")

            content = await self._ask(question, summary_text, context_messages)
            logger.info(f"Generated AI response for question: {question[:50]}...")
            logger.debug(f"AI response from Ollama: {content[:50]}")

            if content is None:
                return "[Error: Exception during Ollama API call]"

            # Save to Redis memory
            self._save_to_memory(prompt, content)

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
    
    def _build_msgs_to_summarize(self):
        # Get messages to summarize from memory
        msgs_to_summarize = []
        msgs_to_summarize_count = 0
        if self.memory is not None and hasattr(self.memory, "chat_memory") and hasattr(self.memory.chat_memory, "messages"):
            N = self.num_of_recent_messages_to_keep + self.num_of_messages_to_summarize
            logger.debug(f"Building messages to summarize from last {N} messages")
            chat_memory_msgs = self.memory.chat_memory.messages[-N:-self.num_of_recent_messages_to_keep]
            # Iterate backwards for efficiency
            for m in chat_memory_msgs:
                if hasattr(m, "type") and hasattr(m, "content"):
                    if m.type == "human":
                        msgs_to_summarize.append({"role": "user", "content": m.content})
                    elif m.type == "ai":
                        msgs_to_summarize.append({"role": "assistant", "content": m.content})
            # Reverse to restore chronological order
        return msgs_to_summarize
    
    async def _ask(self, question, summary_text, context_messages):
        messages = []
        # Add system prompt
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        # Add summary if available
        if summary_text:
            messages.append({"role": "system", "content": summary_text})
        # Add context messages
        messages.extend(context_messages)
        # Add current question
        messages.append({"role": "user", "content": question})
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
        return content

    # -------------------- Adaptive Summarization Helpers --------------------
    def _estimate_token_count(self, text: str) -> int:
        """Rough token estimation (1 token ~= 4 characters)."""
        return max(1, len(text) // 4)

    def _is_summarization_needed(self, messages_to_check) -> bool:
        """Determine if summarization threshold has been exceeded for the oldest messages to summarize."""
        logger.debug("Checking if summarization is needed based on token budget")
        text_to_check = " ".join([m.get("content", "") for m in messages_to_check])
        total_tokens = self._estimate_token_count(text_to_check)
        threshold = self.token_budget - self.summary_token_budget - self.summarization_prompt_tokens
        logger.debug(f"Adaptive summary check (oldest messages): total_tokens={total_tokens} threshold={threshold}")
        return total_tokens > threshold

    async def _summarize_messages(self, messages, language=None):
        if not messages:
            return "Summary: (no content)"
        # Prepare transcript for LLM summarization
        logger.debug("Preparing messages for summarization")
        transcript = "\n".join([f"{m.get('role','user')}: {m.get('content','')[:self.message_summary_char_limit]}" for m in messages])
        logger.debug(f"Transcript for summarization: {transcript}")
        lang = language or getattr(settings, "default_language", "english")
        summarization_prompt = (
            f"You are an assistant that summarizes a conversation in {lang}. Include user intents, key information provided, and next recommended action. "
            f"Maximum {self.summary_token_budget} tokens. Do not fabricate details. Respond with only the summary."
        )
        user_intro = "Conversation transcript:"
        payload = {
            "model": self.model,
            "temperature": 0.0,
            "messages": [
                {"role": "system", "content": summarization_prompt},
                {"role": "user", "content": f"{user_intro}\n{transcript}"}
            ],
            "options": {
                "num_ctx": self.token_budget
            }
        }
        summary = await self._call_ollama_api(payload)
        logger.debug("Generated LLM summary.")
        return f"Summary: {summary.strip() if summary else '(no content)'}"

    def _get_context_messages(self):
        return self.memory.chat_memory.messages[-self.num_of_recent_messages_to_keep:]
    
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
