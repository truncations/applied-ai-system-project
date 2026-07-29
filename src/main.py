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
from embeddings import MusicRecommendationAgent

project_root = Path(__file__).resolve().parent.parent

# Free-form stand-ins for the old structured test profiles, covering the same
# scenarios (straightforward matches, genre/tempo conflicts, near-ties).
test_requests = [
    ("Starter example", "I want upbeat, happy pop -- high energy, danceable, "
        "not very acoustic, positive vibe, around 140 BPM."),
    ("Conflict: genre vs tempo", "I love melancholic classical music, but I want "
        "it high energy, danceable, very positive, and fast at 180 BPM."),
    ("Tie-break: lofi/chill", "Lofi and chill, medium-low energy around 0.40, "
        "tempo about 79 BPM, mood around 0.58, and I like both danceable and "
        "acoustic-leaning tracks."),
]

def main() -> None:
    songs = load_songs(project_root / "data" / "songs.csv")
    recommender = Recommender(songs)
    agent = MusicRecommendationAgent(recommend_tool=recommend_songs_tool(recommender))

    print(f"\nLoaded songs: {len(songs)}")

    for label, request in test_requests:
        result = agent.handle_request(request)

        print(f"\n=== {label} ===")
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


if __name__ == "__main__":
    main()
