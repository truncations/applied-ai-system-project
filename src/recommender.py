import csv
import heapq
from typing import Any, Callable, List, Dict, NamedTuple, Optional
from dataclasses import dataclass

from embeddings import EmbeddingCache, default_embedding_cache, text_similarity

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    likes_dance: bool = True
    target_valence: float = 0.5
    target_tempo_bpm: float = 120.0

class Compare_Attr_Data(NamedTuple):
    """One attribute lined up for comparison: its name, the song's value, and the user's preference value."""
    key_name: str
    song_value: Any
    user_pref_value: Any

class Score_Result(NamedTuple):
    """Return type of score_song(): the total score and human-readable reasons."""
    score: float
    reasons: List[str]

class Recommendation_Result(NamedTuple):
    """One scored recommendation: the song, its score, and the reasons behind it."""
    song: Song
    score: float
    reasons: List[str]

class Attribute_Reward(NamedTuple):
    """Points earned/available for an attribute match, and the base sentence used to explain it."""
    points: float
    reason_base: str

# Maps a scoring attribute name (matches Song field names and
# attribute_points_and_reason_base keys) to the corresponding UserProfile field name.
map_to_user_profile: Dict[str, str] = {
    "genre": "favorite_genre",
    "mood": "favorite_mood",
    "energy": "target_energy",
    "valence": "target_valence",
    "danceability": "likes_dance",
    "acousticness": "likes_acoustic",
    "tempo_bpm": "target_tempo_bpm",
}

# Stores points/max points to be gained for a particular attribute.
# Additionally, stores base sentence structure for reasoning.
attribute_points_and_reason_base: Dict[str, Attribute_Reward] = {
    "genre": Attribute_Reward(7, "genre match"),
    "mood": Attribute_Reward(5, "mood match"),
    "energy": Attribute_Reward(3, "energy is similar to preference"),
    "valence": Attribute_Reward(2, "valence is similar to preference"),
    "danceability": Attribute_Reward(1, "user prefers danceability "),
    "acousticness": Attribute_Reward(0.75, "user prefers acousticness "),
    "tempo_bpm": Attribute_Reward(0.5, "tempo bpm is similar to preference"),
}

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song], embedding_cache: Optional[EmbeddingCache] = None):
        self.songs = songs
        # Lazily built on first real use, not at construction, so constructing a
        # Recommender never requires an API key/network access on its own.
        self.embedding_cache = embedding_cache or default_embedding_cache()

    def recommend_songs(self, user: UserProfile, k: int = 5) -> List[Recommendation_Result]:
        """Scores all songs against the user's preferences and returns the top k, each with its score and reasons."""
        scored = (
            Recommendation_Result(song, result.score, result.reasons)
            for song in self.songs
            for result in (score_song(user, song, self.embedding_cache),)
        )
        return heapq.nlargest(k, scored, key=lambda entry: entry.score)

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Returns the top k songs recommended for the given user."""
        return [entry.song for entry in self.recommend_songs(user, k=k)]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Returns a human-readable explanation for why a song was recommended to the user."""
        result = score_song(user, song, self.embedding_cache)
        header = f"'{song.title}' by {song.artist} scores {result.score:.3f} for this user's preferences."
        if result.reasons:
            return header + "\n" + "\n".join(result.reasons)
        return header

def recommend_songs_tool(recommender: Recommender) -> Callable[..., List[Dict[str, Any]]]:
    """
    Builds the callable the agent layer (embeddings.py) calls as its
    recommend_songs tool: takes the profile fields Gemini parsed out of a
    free-form request, runs the real scorer, and returns plain dicts (title,
    artist, score, reasons) so the LLM only ever sees real, computed results.
    """
    def _tool(
        favorite_genre: str,
        favorite_mood: str,
        target_energy: float,
        target_valence: float,
        target_tempo_bpm: float,
        likes_dance: bool,
        likes_acoustic: bool,
        k: int = 5,
    ) -> List[Dict[str, Any]]:
        user = UserProfile(
            favorite_genre=favorite_genre,
            favorite_mood=favorite_mood,
            target_energy=float(target_energy),
            likes_acoustic=bool(likes_acoustic),
            likes_dance=bool(likes_dance),
            target_valence=float(target_valence),
            target_tempo_bpm=float(target_tempo_bpm),
        )
        return [
            {
                "title": song.title,
                "artist": song.artist,
                "score": round(score, 3),
                "reasons": reasons,
            }
            for song, score, reasons in recommender.recommend_songs(user, k=k)
        ]
    return _tool

def _parse_value(value: str):
    """Converts a CSV string field to int/float when possible, else leaves it as a string."""
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        return value

def load_songs(csv_path: str) -> List[Song]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            parsed_row = {key: _parse_value(value) for key, value in row.items()}
            songs.append(Song(**parsed_row))
    return songs

def attr_score_str(data: Compare_Attr_Data, embedding_cache: EmbeddingCache) -> Attribute_Reward:
    """
    Scores a string-valued attribute by embedding similarity between the song's value
    and the user's preference. Exact matches get full points without any embedding
    lookup; near-matches (e.g. "synthpop" vs "pop") get partial credit scaled by
    cosine similarity instead of scoring 0.
    """
    reward = attribute_points_and_reason_base[data.key_name]
    similarity = text_similarity(data.song_value, data.user_pref_value, embedding_cache)
    if similarity <= 0:
        return Attribute_Reward(0, "")
    if similarity >= 1.0:
        return reward
    return Attribute_Reward(reward.points * similarity, f"{reward.reason_base} (semantic similarity: {similarity:.2f})")

def attr_score_float(data: Compare_Attr_Data) -> Attribute_Reward:
    """Scores a numeric attribute by how close the song's value is to the user's preference."""
    attribute_name = data.key_name
    song_value = data.song_value
    user_pref_value = data.user_pref_value

    reward = attribute_points_and_reason_base[attribute_name]

    if attribute_name == "tempo_bpm": #tempo bpm is > 1 so:
        return Attribute_Reward(reward.points * (min(song_value, user_pref_value) / max(song_value, user_pref_value)), reward.reason_base)
    else:
        return Attribute_Reward(reward.points * (1 - abs(song_value - user_pref_value)), reward.reason_base)

def attr_score_bool(data: Compare_Attr_Data) -> Attribute_Reward:
    """Scores a boolean preference attribute based on the song's corresponding numeric value."""
    attribute_name = data.key_name
    song_value = data.song_value
    user_pref_value = data.user_pref_value

    reward = attribute_points_and_reason_base[attribute_name]
    if user_pref_value: # PREFERS
        return Attribute_Reward(reward.points * song_value, reward.reason_base + "more")
    else: # DOES NOT PREFER
        return Attribute_Reward(reward.points * (1 - song_value), reward.reason_base + "less")

def score_song(user_prefs: UserProfile, song: Song, embedding_cache: EmbeddingCache) -> Score_Result:
    """
    Scores a single song against user preferences.
    Required by Recommender.recommend_songs() and src/main.py
    """
    attributes_dict: Dict[str, List[Compare_Attr_Data]] = {}
    total_score = 0
    reasons: list[str] = []

    for key, profile_attr in map_to_user_profile.items():
        user_pref_value = getattr(user_prefs, profile_attr)
        data = Compare_Attr_Data(key, getattr(song, key), user_pref_value)
        data_type = type(user_pref_value).__name__
        attributes_dict.setdefault(data_type, [])
        attributes_dict[data_type].append(data)

    for key, list_tuples in attributes_dict.items():
        for tuple_data in list_tuples:
            reward_data = None
            if key == "str":
                reward_data = attr_score_str(tuple_data, embedding_cache)
            elif key in ("float", "int"):
                reward_data = attr_score_float(tuple_data)
            elif key == "bool":
                reward_data = attr_score_bool(tuple_data)
            else:
                raise Exception("score_song() FAILED | There is another data type in this set!")

            total_score += reward_data.points
            if reward_data.points > 0:
                reasons.append(f"(+{reward_data.points:.3f}) - {reward_data.reason_base}")

    return Score_Result(total_score, reasons)

def user_profile_from_dict(user_prefs: Dict) -> UserProfile:
    """
    Builds a UserProfile from a preference dict keyed by canonical attribute
    names (genre, mood, energy, valence, danceability, acousticness, tempo_bpm),
    e.g. the user_prefs dicts in src/main.py. Uses map_to_user_profile to translate
    each canonical key to its UserProfile field name.
    """
    return UserProfile(**{
        profile_attr: user_prefs[key]
        for key, profile_attr in map_to_user_profile.items()
        if key in user_prefs
    })