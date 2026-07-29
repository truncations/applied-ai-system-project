# 7/7/2026
## Data Types involved in both collaborative and content-based filtering
Collaborative Filtering:
- Songs played
- Songs skipped
- Likes/dislikes
- Playlists
- Watch time (YouTube)
- Replays
- Search history
- Time of day
- Device used
Content-Based Filtering:
- Tempo of song
- Any vocals in song?
- Energy of song
- Moods

## Schema
Plan according to content-based filtering as instructed:
"Attach songs.csv and ask your AI coding assistant to analyze the available data and suggest which features would be most effective for a simple content-based recommender." (Codepath, Project: Music Recommender Simulation)

Claude Suggests the following features for determining "musical vibe" and content-based recommendations:
- Genre
- Mood
- Energy
- valence
- Danceability
- Acousticness
- Tempo_bpm

To officialize, my "algorithm recipe" or how I will score my songs will be of the order:
1. Genre 
2. Mood
3. Energy
4. Valence
5. Danceability
6. Acousticness
7. Tempo BPM
Other than Genre and Mood, they are scored numerically which means we can mathematically match towards a user's preference based on what they listen to.

Prompt a mathematical based scoring rule:
    "How can I design a mathematically-based 'Scoring Rule' for my simple content-based recommender system where I calculate the score for a song's similarity to a user's preference based on the song's attributes of the following order (for weighting; left is most weight, right is least weight generally): Genre, Mood, Energy, Valence, Danceability, Acousticness, and Tempo BPM.
    
    I understand that mathematically, we need to calculate the error and use that error to determine a score for the song's similarity, and that we'll use a Ranking Rule to determine which songs should be recommended to the user.
    
    For genre and mood matching, because they both are string-based and not actually numerical-based, how could I compute a value of error between the song's genre/mood to the user's preference? There are genres out in music that can be closely similar and I would like to know how I could handle these situations.
    
    Lastly, given the context of the recommender file that contains the classes to be used for this project, how would I determine features that the classes 'Song', 'UserProfile' would use? Does features under this context of developing a song recommender system mean what attributes from those classes would I use or methods to create for it? (Or would it be both?)"

## 7/14/2026
Define specific "taste profile":

taste_profile = {
    "favorite_genre": "pop",
    "favorite_mood": "intense",
    "target_energy":  0.90,
    "likes_acoustic": False,
    "likes_danceability": True,
    "target_tempo_bpm": 140,
    "target_valence": 0.7,
}

## Algorithm Recipe
1. Yield Song's Attributes and UserProfile's Attributes.
    - id: int      
    - title: str 
    - artist: str             
    - genre: str               favorite_genre: str
    - mood: str                favorite_mood: str
    - energy: float            target_energy: float
    - tempo_bpm: float         target_tempo_bpm: float
    - valence: float           target_valence: float
    - danceability: float      likes_danceability: bool
    - acousticness: float      likes_acoustic: bool
2. Create tuples to store pairs of values that are being compared.
    ex. (genre, favorite_genre)
3. Create a dictionary to determine which comparion operation to utilize to subscore the attribute (for which it will be added to the final score later). Keys will be of the data type respectively from the `UserProfile` attributes.
    ex.
    {
        "str": list[tuple[str,str]]
        "float": list[tuple[float,float]]
        "bool": list[tuple[float,bool]]
    }
4. For each key -> value map, use the corresponding scoring operation.
    "str": Compare whether the genre/mood of the song exactly matches with the user's preference genre/mood.
    "float": Use a basic mathematic formula to determine the error of value between the 2 float values.
        error = (| A - B |) IF AND ONLY IF A, B = [0, 1].
        such that A is the song's attribute value, and B is the user's attribute value.
    "bool": The following scenarios are to be considered:
        * If the user does NOT like the given attribute, then a lower value of the song's attribute will be scored higher.
        * If the user does LIKE the given attribute, then a higher value of the song's attribute will be scored higher.

    (!) THERE MAY BE A SPECIAL CASE WHERE WE'LL HAVE TO IMPLEMENT AN ALTERNATIVE COMPARISON SCORING METHOD FOR TEMPO_BPM.
5. To properly point-weigh each attribute of a song, we'll follow this general idea of how scoring should be weighed, from 1 being the highest and 7 being the lowest:
                1. Genre         5. Danceability
                2. Mood          6. Acousticness
                3. Energy        7. Tempo BPM
                4. Valence
Then, we'll provide numerical amounts for how much points should be awarded for a song's similarity to the user's preference.
    (*) Genre [IF EXACT MATCH] provides 7 points.
    (*) Mood [IF EXACT MATCH] provides 5 points.
    (*) Energy provides 3 * [NON-ERROR] points.
    (*) Valence provides 2 * [NON-ERROR] points.
    (*) Danceability provides 1 * [SCALE] points.
    (*) Acousticness provides 0.75 * [SCALE] points.
    (*) Tempo BPM provides 0.5 * [NON-ERROR] points.
6. After computing subscores for each comparable attribute, we will then sum the subscores to get one final official score of similarity between the `Song` and the `UserProfile`. This can then be added to a list of songs with their computed similarity scores.
7. Sort the list of computed similarity scores by highest score, and pull the first number of elements of our choosing, 5 is our default.

Some potential biases that may occur during this analysis:
    * Genre and Mood are both singular-matching cases; it may be too strict to "exactly" match the genre/mood to the user's preference because there are genres/moods that can be SIMILAR to the user's preference but not exact. Vice versa can be said.
        (!) Because they are strict and are singular-match only, for one of the attributes to fail, it could mean missing songs that are perfect for the user because of its other passing attribute.
    * Because we only determine whether the values are high enough or low enough for the attributes "acousticness" and "danceability" (through like_acoustic and like_danceability respectively), we only consider extreme values as "valuable" information even though we should be looking for a target value since a user could like acousticness, even though their target acoustic value might actually be like 0.6 than 1.0.