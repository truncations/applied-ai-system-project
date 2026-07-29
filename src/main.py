"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs

Requests are handled by MusicRecommendationAgent (embeddings.py): Gemini
parses each free-form request into a profile, calls recommend_songs_tool
(recommender.py) to get real scored results, and explains those results in
natural language -- it never invents song data or scores itself.
"""

import textwrap
from pathlib import Path
from recommender import load_songs, recommend_songs_tool, Recommender
from embeddings import MusicRecommendationAgent, llm_logger

project_root = Path(__file__).resolve().parent.parent

EXAMPLE_REQUESTS = [
    "I want upbeat, happy pop -- high energy, danceable, not very acoustic, "
    "positive vibe, around 140 BPM.",
    "I love melancholic classical music, but I want it high energy, danceable, "
    "very positive, and fast at 180 BPM.",
    "Lofi and chill, medium-low energy around 0.40, tempo about 79 BPM, mood "
    "around 0.58, and I like both danceable and acoustic-leaning tracks.",
]

QUIT_WORDS = {"quit", "exit", "q"}
LOG_WORDS = {"logs", "log"}

REMINDER = "(Type 'quit' to exit, or 'logs' to view the LLM call log.)"


def print_result(request: str, result) -> None:
    print("=" * 60)
    print(f"Request: {request}")
    print(f"Parsed profile: {result.profile_args}")
    print(f"\n{result.summary}\n")

    for rank, rec in enumerate(result.recommendations, start=1):
        song_explanation = result.explanations.get(rec["title"])
        explanation = song_explanation.text if song_explanation else "-"
        print(f"{rank}. {rec['title']} - {rec['artist']} (score: {rec['score']:.2f})")
        print(textwrap.fill(explanation, width=88, initial_indent="   ", subsequent_indent="   "))
        print()


def print_logs() -> None:
    logs = llm_logger.get_logs()
    if not logs:
        print("\nNo LLM calls have been logged yet.\n")
        return

    print(f"\n=== LLM Call Log ({len(logs)} entries) ===")
    for i, entry in enumerate(logs, start=1):
        status = f"ERROR: {entry.error}" if entry.error else "ok"
        print(f"{i}. [{entry.timestamp}] {entry.call_type} via {entry.model} ({status})")
        print(f"   input: {entry.input_summary}")
        print(f"   output: {entry.output_summary}")
        print(f"   latency: {entry.latency_seconds:.2f}s, retries: {entry.retries}")
        if entry.confidence:
            print(f"   confidence: {entry.confidence}")
        print()


def main() -> None:
    songs = load_songs(project_root / "data" / "songs.csv")
    recommender = Recommender(songs)
    agent = MusicRecommendationAgent(recommend_tool=recommend_songs_tool(recommender))

    print(f"\nLoaded songs: {len(songs)}")
    print("\nDescribe the kind of music you're in the mood for, in your own words.")
    print("For example:")
    for example in EXAMPLE_REQUESTS:
        print(f"  - {example}")
    print(f"\n{REMINDER}\n")

    request_count = 0
    while True:
        prompt = "Your new request: " if request_count > 0 else "Your request: "
        request = input(prompt).strip()
        if not request:
            continue
        if request.lower() in QUIT_WORDS:
            break
        if request.lower() in LOG_WORDS:
            print_logs()
            print(f"{REMINDER}\n")
            continue

        try:
            result = agent.handle_request(request)
        except Exception as error:
            print(f"\nSorry, something went wrong with that request: {error}\n")
            continue

        request_count += 1
        print()
        print_result(request, result)
        print(f"{REMINDER}\n")


if __name__ == "__main__":
    main()
