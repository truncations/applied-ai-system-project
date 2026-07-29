"""
Gemini integration for recommender.py.

Two things live here:
- Text embedding support: a cached, disk-persisted way to turn short text
  (genre/mood strings) into Gemini embedding vectors, plus a cosine
  similarity helper.
- An agent layer: given a free-form listener request, Gemini parses it into
  a structured profile, calls recommend_songs() as a tool to get real
  scored results (Gemini never invents song data or scores), and then
  rewrites those results as a natural-language explanation.

Kept separate from recommender.py so the scoring logic isn't tangled up
with API/cache plumbing.
"""

import json
import math
import os
import random
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, NamedTuple, Optional, Protocol

from dotenv import load_dotenv
from google import genai
from google.genai import errors as genai_errors
from google.genai import types


class LLMCallLog(NamedTuple):
    """One recorded LLM call, kept for later inspection (e.g. printed by main.py)."""
    timestamp: str
    call_type: str  # "embedding" | "parse" | "explain"
    model: str
    input_summary: str
    output_summary: str
    latency_seconds: float
    retries: int
    confidence: Optional[Dict[str, Any]]
    error: Optional[str]


class LLMCallLogger:
    """
    Collects every LLM call made during a run (embedding lookups, request
    parsing, result explanation) so they can be inspected or printed later.
    Shared across embeddings.py and recommender.py via the `llm_logger`
    singleton below.
    """
    def __init__(self):
        self.entries: List[LLMCallLog] = []

    def log(self, **kwargs) -> LLMCallLog:
        entry = LLMCallLog(timestamp=datetime.now().isoformat(), **kwargs)
        self.entries.append(entry)
        return entry

    def update(self, entry: LLMCallLog, **changes) -> LLMCallLog:
        """Patches a previously logged entry in place (e.g. to attach confidence extracted after the call returned)."""
        index = self.entries.index(entry)
        updated = entry._replace(**changes)
        self.entries[index] = updated
        return updated

    def get_logs(self) -> List[LLMCallLog]:
        return list(self.entries)

    def clear(self) -> None:
        self.entries.clear()


llm_logger = LLMCallLogger()


class EmbeddingClient(Protocol):
    """Anything that can turn text into an embedding vector."""

    def embed(self, text: str) -> List[float]:
        ...


class GeminiEmbeddingClient:
    """Embeds text using the Gemini API (google-genai SDK)."""

    def __init__(
        self,
        model: str = "gemini-embedding-001",
        output_dimensionality: int = 768,
    ):
        self._model = model
        self._output_dimensionality = output_dimensionality
        self._client = None  # constructed lazily so import/construction never requires an API key

    def _get_client(self):
        if self._client is None:
            load_dotenv()
            api_key = os.environ["GEMINI_API_KEY"]
            self._client = genai.Client(api_key=api_key)
        return self._client

    def embed(self, text: str) -> List[float]:
        client = self._get_client()
        start = time.time()
        try:
            response = client.models.embed_content(
                model=self._model,
                contents=text,
                config=types.EmbedContentConfig(
                    task_type="SEMANTIC_SIMILARITY",
                    output_dimensionality=self._output_dimensionality,
                ),
            )
            vector = response.embeddings[0].values
        except Exception as error:
            llm_logger.log(
                call_type="embedding",
                model=self._model,
                input_summary=text,
                output_summary="",
                latency_seconds=time.time() - start,
                retries=0,
                confidence=None,
                error=str(error),
            )
            raise
        llm_logger.log(
            call_type="embedding",
            model=self._model,
            input_summary=text,
            output_summary=f"{len(vector)}-dim vector",
            latency_seconds=time.time() - start,
            retries=0,
            confidence=None,
            error=None,
        )
        return vector


class EmbeddingCache:
    """
    Caches text -> embedding vector on disk, keyed by the text itself (not by
    song id), so repeated genre/mood strings across songs and user profiles
    only ever get embedded once.
    """

    def __init__(self, client: EmbeddingClient, cache_path: Path):
        self._client = client
        self._cache_path = cache_path
        self._cache: Dict[str, List[float]] = {}
        if cache_path.exists():
            with open(cache_path, encoding="utf-8") as f:
                self._cache = json.load(f)

    def get(self, text: str) -> List[float]:
        key = text.strip().lower()
        if key not in self._cache:
            self._cache[key] = self._client.embed(key)
            self._save()
        return self._cache[key]

    def _save(self) -> None:
        self._cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._cache_path, "w", encoding="utf-8") as f:
            json.dump(self._cache, f)


_DEFAULT_CACHE_PATH = Path(__file__).resolve().parent.parent / "data" / "embeddings_cache.json"


def default_embedding_cache() -> EmbeddingCache:
    """The real, Gemini-backed cache used by Recommender when no cache is injected."""
    return EmbeddingCache(GeminiEmbeddingClient(), _DEFAULT_CACHE_PATH)


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Cosine similarity between two vectors, clamped to [0, 1] for use as a scoring multiplier."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return max(0.0, min(1.0, dot / (norm_a * norm_b)))


def text_similarity(text_a: str, text_b: str, cache: EmbeddingCache) -> float:
    """Embedding-based similarity between two pieces of text, using the given cache."""
    if text_a.strip().lower() == text_b.strip().lower():
        return 1.0
    return cosine_similarity(cache.get(text_a), cache.get(text_b))


# ---------------------------------------------------------------------------
# Agent layer
#
# Flow for one free-form request:
#   1. Gemini reads the request and calls recommend_songs (a FunctionDeclaration
#      below) with a structured, best-guess taste profile.
#   2. We execute the *real* tool (injected as `recommend_tool`, backed by
#      Recommender.recommend_songs) and get back real scores/reasons.
#   3. Gemini is shown only that real data and asked to rewrite it as a
#      natural-language explanation -- it is told not to invent anything.
#
# Both steps also self-report confidence (high/medium/low + a short reason)
# so uncertain guesses are visible instead of silently blended into the output.
# ---------------------------------------------------------------------------

_PROFILE_FIELDS = [
    "favorite_genre",
    "favorite_mood",
    "target_energy",
    "target_valence",
    "target_tempo_bpm",
    "likes_dance",
    "likes_acoustic",
]

_CONFIDENCE_FIELD_SCHEMA = types.Schema(
    type=types.Type.OBJECT,
    properties={
        "level": types.Schema(
            type=types.Type.STRING,
            enum=["high", "medium", "low"],
            description="How confident you are in this value.",
        ),
        "reason": types.Schema(
            type=types.Type.STRING,
            description=(
                "Short reason for the confidence level, e.g. 'stated explicitly as 140 BPM' "
                "for high, or 'no tempo given, guessed from chill mood' for medium/low."
            ),
        ),
    },
    required=["level", "reason"],
)

RECOMMEND_SONGS_DECLARATION = types.FunctionDeclaration(
    name="recommend_songs",
    description=(
        "Scores every song in the catalog against a listener's taste profile and "
        "returns the top matches with their real computed scores and reasons. "
        "Always call this tool to get recommendations -- never invent song titles, "
        "artists, scores, or reasons yourself."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "favorite_genre": types.Schema(
                type=types.Type.STRING,
                description="The listener's preferred music genre, e.g. 'pop', 'lofi', 'rock'.",
            ),
            "favorite_mood": types.Schema(
                type=types.Type.STRING,
                description="The mood the listener wants, e.g. 'happy', 'chill', 'intense'.",
            ),
            "target_energy": types.Schema(
                type=types.Type.NUMBER,
                description="Desired energy level from 0.0 (calm) to 1.0 (high energy).",
            ),
            "target_valence": types.Schema(
                type=types.Type.NUMBER,
                description="Desired positivity/mood valence from 0.0 (sad/dark) to 1.0 (happy/bright).",
            ),
            "target_tempo_bpm": types.Schema(
                type=types.Type.NUMBER,
                description="Desired tempo in beats per minute.",
            ),
            "likes_dance": types.Schema(
                type=types.Type.BOOLEAN,
                description="Whether the listener wants danceable songs.",
            ),
            "likes_acoustic": types.Schema(
                type=types.Type.BOOLEAN,
                description="Whether the listener wants acoustic-sounding songs.",
            ),
            "k": types.Schema(
                type=types.Type.INTEGER,
                description="How many songs to recommend. Defaults to 5 if not specified.",
            ),
            "confidence": types.Schema(
                type=types.Type.OBJECT,
                description=(
                    "Self-assessed confidence for each of the seven taste-profile fields above "
                    "(not for k), reflecting how directly the listener's request supported that "
                    "value versus how much you had to infer or guess."
                ),
                properties={field: _CONFIDENCE_FIELD_SCHEMA for field in _PROFILE_FIELDS},
                required=list(_PROFILE_FIELDS),
            ),
        },
        required=[
            "favorite_genre",
            "favorite_mood",
            "target_energy",
            "target_valence",
            "target_tempo_bpm",
            "likes_dance",
            "likes_acoustic",
            "confidence",
        ],
    ),
)

_PARSE_SYSTEM_INSTRUCTION = (
    "You are a music recommendation assistant. Read the listener's free-form request and "
    "call recommend_songs with your best-guess structured taste profile. Infer numeric "
    "fields (0.0-1.0 for energy/valence, a realistic BPM) from descriptive language even "
    "when the listener didn't give exact numbers. Always call the tool -- never answer "
    "directly without calling it. For every field, also fill in `confidence`: mark a field "
    "'high' only if the listener stated or clearly implied it, and 'medium'/'low' when you "
    "had to infer or guess it -- always give a short, specific reason, especially for "
    "anything below 'high'."
)

_EXPLAIN_SYSTEM_INSTRUCTION = (
    "You are a music recommendation assistant. recommend_songs already ran and gave you "
    "real results: each song's title, artist, computed score, and the specific "
    "attribute-level reasons behind that score. Rewrite those reasons as warm, natural "
    "language for the listener -- explain why each song fits their request. Use only the "
    "data provided; never invent scores, reasons, or songs that aren't in the tool result. "
    "Also report `summary_confidence` and a per-song `confidence`: these reflect how well "
    "you believe the explanation captures what the listener actually wanted -- lower it "
    "when a song's reasons only loosely support the request (e.g. a weak or missing match "
    "on an attribute the listener seemed to care about), not when the underlying score "
    "itself is just low. Always give a short, specific reason."
)

_EXPLAIN_RESPONSE_SCHEMA = types.Schema(
    type=types.Type.OBJECT,
    properties={
        "summary": types.Schema(
            type=types.Type.STRING,
            description="One short, natural sentence summarizing the picks for the listener.",
        ),
        "summary_confidence": _CONFIDENCE_FIELD_SCHEMA,
        "songs": types.Schema(
            type=types.Type.ARRAY,
            items=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "title": types.Schema(type=types.Type.STRING),
                    "explanation": types.Schema(
                        type=types.Type.STRING,
                        description=(
                            "1-2 natural, conversational sentences explaining why this "
                            "specific song was recommended, grounded only in its given "
                            "score and reasons."
                        ),
                    ),
                    "confidence": _CONFIDENCE_FIELD_SCHEMA,
                },
                required=["title", "explanation", "confidence"],
            ),
        ),
    },
    required=["summary", "summary_confidence", "songs"],
)


class FieldConfidence(NamedTuple):
    """A field-level self-assessment: how sure the LLM was, and why."""
    level: str  # "high" | "medium" | "low"
    reason: str


class SongExplanation(NamedTuple):
    """One song's natural-language explanation plus how confident it is."""
    text: str
    confidence: FieldConfidence


def _confidence_from_dict(data: Dict[str, Any]) -> FieldConfidence:
    return FieldConfidence(level=data.get("level", ""), reason=data.get("reason", ""))


class AgentResult(NamedTuple):
    """What the agent produced for one free-form request."""
    profile_args: Dict[str, Any]
    profile_confidence: Dict[str, FieldConfidence]  # profile field name -> confidence
    recommendations: List[Dict[str, Any]]
    summary: str
    summary_confidence: FieldConfidence
    explanations: Dict[str, SongExplanation]  # song title -> explanation + confidence


_TRANSIENT_RETRY_STATUS_CODES = {429, 503}  # rate limited / model overloaded
_MAX_RETRIES_PER_MODEL = 3
_INITIAL_BACKOFF_SECONDS = 2.0

_DEFAULT_MODELS = ["gemini-flash-latest", "gemini-flash-lite-latest"]

_SUMMARY_MAX_CHARS = 300


def _summarize_contents(contents) -> str:
    """Short text summary of a generate() `contents` argument, for log readability."""
    parts_text = []
    for content in contents:
        for part in getattr(content, "parts", None) or []:
            if getattr(part, "text", None):
                parts_text.append(part.text)
            elif getattr(part, "function_call", None) is not None:
                parts_text.append(f"function_call:{part.function_call.name}({dict(part.function_call.args or {})})")
            elif getattr(part, "function_response", None) is not None:
                parts_text.append(f"function_response:{part.function_response.name}")
    summary = " | ".join(parts_text) or str(contents)
    return summary if len(summary) <= _SUMMARY_MAX_CHARS else summary[:_SUMMARY_MAX_CHARS] + "..."


def _summarize_response(response: types.GenerateContentResponse) -> str:
    """Short text summary of a generate_content() response, for log readability."""
    call = _first_function_call(response)
    if call is not None:
        summary = f"function_call:{call.name}({dict(call.args or {})})"
    else:
        summary = response.text or ""
    return summary if len(summary) <= _SUMMARY_MAX_CHARS else summary[:_SUMMARY_MAX_CHARS] + "..."


class GeminiAgentClient:
    """
    Wraps the Gemini generative model(s) used by MusicRecommendationAgent.

    Tries each model in `models` in order. A transient error (429 rate limit,
    503 overloaded) is retried a few times against the same model before
    moving on to the next one; any other error moves on immediately.
    """

    def __init__(self, models: Optional[List[str]] = None):
        self._models = models or _DEFAULT_MODELS
        self._client = None  # constructed lazily so import/construction never requires an API key

    def _get_client(self):
        if self._client is None:
            load_dotenv()
            api_key = os.environ["GEMINI_API_KEY"]
            self._client = genai.Client(api_key=api_key)
        return self._client

    def generate(
        self, contents, call_type: str = "unknown", **config_kwargs
    ) -> "tuple[types.GenerateContentResponse, LLMCallLog]":
        """
        Calls Gemini, retrying/falling back across self._models as before, and
        logs the outcome to llm_logger. `call_type` (e.g. "parse", "explain")
        is just a label for the log entry -- it doesn't affect the request.
        Returns (response, log_entry) so the caller can later attach
        confidence info to the same log entry via llm_logger.update().
        """
        client = self._get_client()
        config = types.GenerateContentConfig(**config_kwargs)
        start = time.time()
        total_attempts = 0

        last_error: Optional[genai_errors.APIError] = None
        for model_index, model in enumerate(self._models):
            backoff = _INITIAL_BACKOFF_SECONDS
            for attempt in range(_MAX_RETRIES_PER_MODEL + 1):
                total_attempts += 1
                try:
                    response = client.models.generate_content(
                        model=model,
                        contents=contents,
                        config=config,
                    )
                    log_entry = llm_logger.log(
                        call_type=call_type,
                        model=model,
                        input_summary=_summarize_contents(contents),
                        output_summary=_summarize_response(response),
                        latency_seconds=time.time() - start,
                        retries=total_attempts - 1,
                        confidence=None,
                        error=None,
                    )
                    return response, log_entry
                except genai_errors.APIError as error:
                    last_error = error
                    if error.code not in _TRANSIENT_RETRY_STATUS_CODES or attempt == _MAX_RETRIES_PER_MODEL:
                        break
                    sleep_seconds = backoff + random.uniform(0, 1)
                    print(
                        f"{model} returned {error.code} (attempt {attempt + 1}/{_MAX_RETRIES_PER_MODEL}); "
                        f"retrying in {sleep_seconds:.1f}s..."
                    )
                    time.sleep(sleep_seconds)
                    backoff *= 2

            if model_index < len(self._models) - 1:
                print(f"{model} unavailable ({last_error.code}); falling back to {self._models[model_index + 1]}...")

        llm_logger.log(
            call_type=call_type,
            model=self._models[-1],
            input_summary=_summarize_contents(contents),
            output_summary="",
            latency_seconds=time.time() - start,
            retries=total_attempts - 1,
            confidence=None,
            error=str(last_error),
        )
        raise last_error


def _first_function_call(response: types.GenerateContentResponse) -> Optional[types.FunctionCall]:
    """Pulls the first function call out of a Gemini response, or None if it didn't make one."""
    candidates = response.candidates or []
    if not candidates or not candidates[0].content or not candidates[0].content.parts:
        return None
    for part in candidates[0].content.parts:
        if part.function_call is not None:
            return part.function_call
    return None


class MusicRecommendationAgent:
    """
    Turns a free-form listener request into grounded recommendations: Gemini
    parses the request into a recommend_songs() tool call, the real scoring
    tool runs (so Gemini can't invent song data or scores), and Gemini then
    explains only what that tool actually returned.
    """

    def __init__(
        self,
        recommend_tool: Callable[..., List[Dict[str, Any]]],
        client: Optional[GeminiAgentClient] = None,
    ):
        self._recommend_tool = recommend_tool
        self._client = client or GeminiAgentClient()

    def handle_request(self, user_request: str) -> AgentResult:
        tool = types.Tool(function_declarations=[RECOMMEND_SONGS_DECLARATION])

        request_content = types.Content(role="user", parts=[types.Part(text=user_request)])
        parse_response, parse_log = self._client.generate(
            contents=[request_content],
            call_type="parse",
            system_instruction=_PARSE_SYSTEM_INSTRUCTION,
            tools=[tool],
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        )

        call = _first_function_call(parse_response)
        if call is None or call.name != "recommend_songs":
            raise RuntimeError(
                f"Gemini didn't call recommend_songs for this request: {parse_response.text!r}"
            )

        args = dict(call.args or {})
        confidence_raw = args.pop("confidence", {})
        profile_confidence = {
            field: _confidence_from_dict(confidence_raw.get(field, {}))
            for field in _PROFILE_FIELDS
        }
        llm_logger.update(parse_log, confidence=confidence_raw)

        k = int(args.pop("k", 5) or 5)
        recommendations = self._recommend_tool(**args, k=k)

        function_response_content = types.Content(
            role="user",
            parts=[
                types.Part(
                    function_response=types.FunctionResponse(
                        name="recommend_songs",
                        response={"recommendations": recommendations},
                    )
                )
            ],
        )
        explain_response, explain_log = self._client.generate(
            contents=[
                request_content,
                parse_response.candidates[0].content,
                function_response_content,
            ],
            call_type="explain",
            system_instruction=_EXPLAIN_SYSTEM_INSTRUCTION,
            response_mime_type="application/json",
            response_schema=_EXPLAIN_RESPONSE_SCHEMA,
        )

        explained = json.loads(explain_response.text)
        summary_confidence = _confidence_from_dict(explained.get("summary_confidence", {}))
        explanations = {
            song["title"]: SongExplanation(
                text=song["explanation"],
                confidence=_confidence_from_dict(song.get("confidence", {})),
            )
            for song in explained.get("songs", [])
        }
        llm_logger.update(
            explain_log,
            confidence={
                "summary_confidence": explained.get("summary_confidence", {}),
                "songs": {
                    song["title"]: song.get("confidence", {}) for song in explained.get("songs", [])
                },
            },
        )

        return AgentResult(
            profile_args={**args, "k": k},
            profile_confidence=profile_confidence,
            recommendations=recommendations,
            summary=explained.get("summary", ""),
            summary_confidence=summary_confidence,
            explanations=explanations,
        )