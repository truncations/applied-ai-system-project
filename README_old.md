# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Explain your design in plain language.

Some prompts to answer:

- What features does each `Song` use in your system
  - For example: genre, mood, energy, tempo
- What information does your `UserProfile` store
- How does your `Recommender` compute a score for each song
- How do you choose which songs to recommend

You can include a simple diagram or bullet list if helpful.

In order to recommend a song based on the knowledge of how real world recommendations for large-scale applications like YouTube and Spotify, scores are assigned to each song in a given data set based on the song's attributes similiarity to the user's preferences (content-based filtering) for which after scores are assigned, the songs with their scores are organized in a high score to low score manner, and we'll pull the top songs from the list; the number of songs we get starting from the top varies.
For the system, I would have a `Song` use the attributes already provided in `recommender.py` as provided: 
    - id: int
    - title: str
    - artist: str
    - genre: str
    - mood: str
    - energy: float
    - tempo_bpm: float
    - valence: float
    - danceability: float
    - acousticness: float
These store essential information that I would need for a song in general. Of these attributes for the `Song` class, I would use the following attributes to develop the recommender system and compute a similarity value: "genre", "mood", "energy", "tempo_bpm", "valence", "danceability", "acousticness". 

The information that `UserProfile` will store would be what `Song` stores except that it would store a target value for each `Song` attribute (basically getting a user's preference for genre, mood,  energy, tempo_bpm, valence, danceability, and acousticness). If there are missing variables that need to be added, it will be done so during system implementation. (likes_danceability, target_valence, target_tempo_bpm)

In order for `Recommender` to compute a score for each song, we'll use a basic mathematical error analysis between a `Song`'s attribute (values) and the `UserProfile`'s information. We may use the error formula (1 - |A - B|) as one example. If they are strings, we'll simply determine if the string itself matches with the user's preferences. Then we'll weigh each attribute being used to determine a song for recommendation. Once weighed, we'll add sub-scores to the final score for each considered attribute (and consider their weight towards the final score). This score will be then used to compute a list of songs sorted by top score to lowest score, and we'll pick out the first few top elements.

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
    
## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Paste a sample of your recommender's output here as a text block so a reader can see what it produces:

Assuming the following:
user_prefs = {
    "genre": "pop",
    "mood": "happy",
    "energy":  0.90,
    "acousticness": False,
    "danceability": True,
    "tempo_bpm": 140,
    "valence": 0.7,
}

```
Loaded songs: 18

Top Recommendations
============================================================

1. Sunrise City - Score: 18.31
   Artist: Neon Echo
   Reasons:
     - (+7.000) - genre match
     - (+5.000) - mood match
     - (+2.760) - energy is similar to preference
     - (+1.720) - valence is similar to preference
     - (+0.615) - user prefers acousticness less
     - (+0.790) - user prefers danceability more
     - (+0.421) - tempo bpm is similar to preference

2. Gym Hero - Score: 13.83
   Artist: Max Pulse
   Reasons:
     - (+7.000) - genre match
     - (+2.910) - energy is similar to preference
     - (+1.860) - valence is similar to preference
     - (+0.712) - user prefers acousticness less
     - (+0.880) - user prefers danceability more
     - (+0.471) - tempo bpm is similar to preference

3. Rooftop Lights - Score: 11.11
   Artist: Indigo Parade
   Reasons:
     - (+5.000) - mood match
     - (+2.580) - energy is similar to preference
     - (+1.780) - valence is similar to preference
     - (+0.488) - user prefers acousticness less
     - (+0.820) - user prefers danceability more
     - (+0.443) - tempo bpm is similar to preference

4. Neon Pulse Rave - Score: 6.57
   Artist: DJ Fractal
   Reasons:
     - (+2.940) - energy is similar to preference
     - (+1.600) - valence is similar to preference
     - (+0.660) - user prefers acousticness less
     - (+0.910) - user prefers danceability more
     - (+0.457) - tempo bpm is similar to preference

5. Concrete Kingdom - Score: 6.54
   Artist: MC Ironside
   Reasons:
     - (+2.700) - energy is similar to preference
     - (+1.960) - valence is similar to preference
     - (+0.690) - user prefers acousticness less
     - (+0.850) - user prefers danceability more
     - (+0.339) - tempo bpm is similar to preference
```

## System Evaluation Results
user_prefs_test_2 = {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.20,
        "acousticness": True,
        "danceability": False,
        "tempo_bpm": 70,
        "valence": 0.4,
    }

```
=== Test 2 (lofi/chill) ===
============================================================
Selected preferences:
   genre: lofi
   mood: chill
   energy: 0.2
   acousticness: True
   danceability: False
   tempo_bpm: 70
   valence: 0.4

1. Library Rain - Score: 17.70
   Artist: Paper Lanterns
   Reasons:
     - (+7.000) - genre match
     - (+5.000) - mood match
     - (+2.550) - energy is similar to preference
     - (+1.600) - valence is similar to preference
     - (+0.645) - user prefers acousticness more
     - (+0.420) - user prefers danceability less
     - (+0.486) - tempo bpm is similar to preference

2. Midnight Coding - Score: 17.38
   Artist: LoRoom
   Reasons:
     - (+7.000) - genre match
     - (+5.000) - mood match
     - (+2.340) - energy is similar to preference
     - (+1.680) - valence is similar to preference
     - (+0.532) - user prefers acousticness more
     - (+0.380) - user prefers danceability less
     - (+0.449) - tempo bpm is similar to preference

3. Focus Flow - Score: 12.44
   Artist: LoRoom
   Reasons:
     - (+7.000) - genre match
     - (+2.400) - energy is similar to preference
     - (+1.620) - valence is similar to preference
     - (+0.585) - user prefers acousticness more
     - (+0.400) - user prefers danceability less
     - (+0.438) - tempo bpm is similar to preference

4. Spacewalk Thoughts - Score: 10.97
   Artist: Orbit Bloom
   Reasons:
     - (+5.000) - mood match
     - (+2.760) - energy is similar to preference
     - (+1.500) - valence is similar to preference
     - (+0.690) - user prefers acousticness more
     - (+0.590) - user prefers danceability less
     - (+0.429) - tempo bpm is similar to preference

5. Winter's Requiem - Score: 6.63
   Artist: Elena Voss
   Reasons:
     - (+2.850) - energy is similar to preference
     - (+1.800) - valence is similar to preference
     - (+0.712) - user prefers acousticness more
     - (+0.800) - user prefers danceability less
     - (+0.471) - tempo bpm is similar to preference
```

user_prefs_test_3 = {
        "genre": "rock",
        "mood": "intense",
        "energy": 0.95,
        "acousticness": False,
        "danceability": False,
        "tempo_bpm": 160,
        "valence": 0.2,
    }

```
=== Test 3 (rock/intense) ===
============================================================
Selected preferences:
   genre: rock
   mood: intense
   energy: 0.95
   acousticness: False
   danceability: False
   tempo_bpm: 160
   valence: 0.2

1. Storm Runner - Score: 17.81
   Artist: Voltline
   Reasons:
     - (+7.000) - genre match
     - (+5.000) - mood match
     - (+2.880) - energy is similar to preference
     - (+1.440) - valence is similar to preference
     - (+0.675) - user prefers acousticness less
     - (+0.340) - user prefers danceability less
     - (+0.475) - tempo bpm is similar to preference

2. Gym Hero - Score: 10.04
   Artist: Max Pulse
   Reasons:
     - (+5.000) - mood match
     - (+2.940) - energy is similar to preference
     - (+0.860) - valence is similar to preference
     - (+0.712) - user prefers acousticness less
     - (+0.120) - user prefers danceability less
     - (+0.412) - tempo bpm is similar to preference

3. Iron Descent - Score: 6.49
   Artist: Grave Circuit
   Reasons:
     - (+2.940) - energy is similar to preference
     - (+1.900) - valence is similar to preference
     - (+0.728) - user prefers acousticness less
     - (+0.450) - user prefers danceability less
     - (+0.476) - tempo bpm is similar to preference

4. Night Drive Loop - Score: 5.02
   Artist: Neon Echo
   Reasons:
     - (+2.400) - energy is similar to preference
     - (+1.420) - valence is similar to preference
     - (+0.585) - user prefers acousticness less
     - (+0.270) - user prefers danceability less
     - (+0.344) - tempo bpm is similar to preference

5. Concrete Kingdom - Score: 4.73
   Artist: MC Ironside
   Reasons:
     - (+2.550) - energy is similar to preference
     - (+1.040) - valence is similar to preference
     - (+0.690) - user prefers acousticness less
     - (+0.150) - user prefers danceability less
     - (+0.297) - tempo bpm is similar to preference
```

user_prefs_conflict_genre_vs_tempo = {
        "genre": "classical",
        "mood": "melancholic",
        "energy": 0.90,
        "acousticness": False,
        "danceability": True,
        "tempo_bpm": 180,
        "valence": 0.9,
    }

```
=== Conflict: genre vs tempo ===
============================================================
Selected preferences:
   genre: classical
   mood: melancholic
   energy: 0.9
   acousticness: False
   danceability: True
   tempo_bpm: 180
   valence: 0.9

1. Winter's Requiem - Score: 14.27
   Artist: Elena Voss
   Reasons:
     - (+7.000) - genre match
     - (+5.000) - mood match
     - (+1.050) - energy is similar to preference
     - (+0.800) - valence is similar to preference
     - (+0.038) - user prefers acousticness less
     - (+0.200) - user prefers danceability more
     - (+0.183) - tempo bpm is similar to preference

2. Neon Pulse Rave - Score: 6.87
   Artist: DJ Fractal
   Reasons:
     - (+2.940) - energy is similar to preference
     - (+2.000) - valence is similar to preference
     - (+0.660) - user prefers acousticness less
     - (+0.910) - user prefers danceability more
     - (+0.356) - tempo bpm is similar to preference

3. Gym Hero - Score: 6.61
   Artist: Max Pulse
   Reasons:
     - (+2.910) - energy is similar to preference
     - (+1.740) - valence is similar to preference
     - (+0.712) - user prefers acousticness less
     - (+0.880) - user prefers danceability more
     - (+0.367) - tempo bpm is similar to preference

4. Sunrise City - Score: 6.37
   Artist: Neon Echo
   Reasons:
     - (+2.760) - energy is similar to preference
     - (+1.880) - valence is similar to preference
     - (+0.615) - user prefers acousticness less
     - (+0.790) - user prefers danceability more
     - (+0.328) - tempo bpm is similar to preference

5. Concrete Kingdom - Score: 6.06
   Artist: MC Ironside
   Reasons:
     - (+2.700) - energy is similar to preference
     - (+1.560) - valence is similar to preference
     - (+0.690) - user prefers acousticness less
     - (+0.850) - user prefers danceability more
     - (+0.264) - tempo bpm is similar to preference
```

user_prefs_conflict_impossible_combo = {
        "genre": "house",
        "mood": "euphoric",
        "energy": 0.88,
        "acousticness": True,
        "danceability": True,
        "tempo_bpm": 128,
        "valence": 0.90,
    }

```
=== Conflict: impossible combo ===
============================================================
Selected preferences:
   genre: house
   mood: euphoric
   energy: 0.88
   acousticness: True
   danceability: True
   tempo_bpm: 128
   valence: 0.9

1. Neon Pulse Rave - Score: 18.50
   Artist: DJ Fractal
   Reasons:
     - (+7.000) - genre match
     - (+5.000) - mood match
     - (+3.000) - energy is similar to preference
     - (+2.000) - valence is similar to preference
     - (+0.090) - user prefers acousticness more
     - (+0.910) - user prefers danceability more
     - (+0.500) - tempo bpm is similar to preference

2. Sunrise City - Score: 6.09
   Artist: Neon Echo
   Reasons:
     - (+2.820) - energy is similar to preference
     - (+1.880) - valence is similar to preference
     - (+0.135) - user prefers acousticness more
     - (+0.790) - user prefers danceability more
     - (+0.461) - tempo bpm is similar to preference

3. Rooftop Lights - Score: 6.03
   Artist: Indigo Parade
   Reasons:
     - (+2.640) - energy is similar to preference
     - (+1.820) - valence is similar to preference
     - (+0.262) - user prefers acousticness more
     - (+0.820) - user prefers danceability more
     - (+0.484) - tempo bpm is similar to preference

4. Gym Hero - Score: 5.99
   Artist: Max Pulse
   Reasons:
     - (+2.850) - energy is similar to preference
     - (+1.740) - valence is similar to preference
     - (+0.038) - user prefers acousticness more
     - (+0.880) - user prefers danceability more
     - (+0.485) - tempo bpm is similar to preference

5. Noche Caliente - Score: 5.81
   Artist: Sol y Ritmo
   Reasons:
     - (+2.460) - energy is similar to preference
     - (+1.860) - valence is similar to preference
     - (+0.225) - user prefers acousticness more
     - (+0.870) - user prefers danceability more
     - (+0.391) - tempo bpm is similar to preference
```

user_prefs_tiebreak_lofi_chill = {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.40,
        "acousticness": True,
        "danceability": True,
        "tempo_bpm": 79,
        "valence": 0.58,
    }

```
=== Tie-break: lofi/chill ===
============================================================
Selected preferences:
   genre: lofi
   mood: chill
   energy: 0.4
   acousticness: True
   danceability: True
   tempo_bpm: 79
   valence: 0.58

1. Midnight Coding - Score: 18.55
   Artist: LoRoom
   Reasons:
     - (+7.000) - genre match
     - (+5.000) - mood match
     - (+2.940) - energy is similar to preference
     - (+1.960) - valence is similar to preference
     - (+0.532) - user prefers acousticness more
     - (+0.620) - user prefers danceability more
     - (+0.494) - tempo bpm is similar to preference

2. Library Rain - Score: 18.49
   Artist: Paper Lanterns
   Reasons:
     - (+7.000) - genre match
     - (+5.000) - mood match
     - (+2.850) - energy is similar to preference
     - (+1.960) - valence is similar to preference
     - (+0.645) - user prefers acousticness more
     - (+0.580) - user prefers danceability more
     - (+0.456) - tempo bpm is similar to preference

3. Focus Flow - Score: 13.66
   Artist: LoRoom
   Reasons:
     - (+7.000) - genre match
     - (+3.000) - energy is similar to preference
     - (+1.980) - valence is similar to preference
     - (+0.585) - user prefers acousticness more
     - (+0.600) - user prefers danceability more
     - (+0.494) - tempo bpm is similar to preference

4. Spacewalk Thoughts - Score: 10.98
   Artist: Orbit Bloom
   Reasons:
     - (+5.000) - mood match
     - (+2.640) - energy is similar to preference
     - (+1.860) - valence is similar to preference
     - (+0.690) - user prefers acousticness more
     - (+0.410) - user prefers danceability more
     - (+0.380) - tempo bpm is similar to preference

5. Coffee Shop Stories - Score: 6.30
   Artist: Slow Stereo
   Reasons:
     - (+2.910) - energy is similar to preference
     - (+1.740) - valence is similar to preference
     - (+0.667) - user prefers acousticness more
     - (+0.540) - user prefers danceability more
     - (+0.439) - tempo bpm is similar to preference
```


**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

I mostly did experiments to see what occurred when changing my weights accordingly.

One test I did was to try to increase the weighing with "vibe"-based features of the song rather than content-based features like "genre" and "mood" which doesn't always tell the full feeling of the song. I reduced the weights of genre and mood respectively; 7 to 4, and 5 to 3.5, while increased the rest:
    energy: 3 -> 3.5
    valence: 2 -> 2.25
    danceability: 1 -> 1.5
    acousticness: 0.75 -> 1
    tempo_bpm: 0.5 -> 0.75
Unfortunately, even with these changes the #1 recommendation in all tests for the user profiles never changed because of the fact that genre+mood made up nearly 50% of the score which can be highly impactful with how similar a song can be based on what the recommender thinks. Sometimes, some songs had their margins of score reduced and some songs in ranking changed thanks to actually correctly weighing on vibes than just "content" fitting like when testing with "lofi-chill" where "Focus Flow" is now ranked lower than "Spacewalk Thoughts" since the feeling of the song matches more than "Focus Flow".

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

Some limitations of my systems that create bias are that genres and moods must be exactly matching, even though some genres and moods can be similar but not exact to the user's preference. (TLDR; hybrid genres are highly penalized) Mood is heavily fragmented as most of the dataset have their own unique moods, and so it leads to genre+mood being relied on rather than actual music taste. Additionally, for the acousticness/danceability attributes of a song, they are strictly based on whether a user likes acousticness or likes danceability, where if they do "like" acousticness/danceability that higher values reward more, and vice versa rather than actually finding the target acousticness/danceability value that someone would prefer which creates bias; for example, some users may like acousticness but not heavy acoustic.

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this

Recommenders turn data into predictions by parsing the data and using algorithms to generate a score that can then be used for to deduce a prediction. The recommending systems take a song's features (ex. genre, mood, title, artist) and use that information to compare it to a user's preference to determine whether the song's features match with the user's preferences. Once they have determined the similarity amount of each feature being compared, they will parse this into a score that will then be used to recommend songs to the user.
Unfortunately, bias shows up in these kinds of systems when the dataset is too small leading to representation bias in the catalog where the songs being recommended may have a ridiculously low similarity score since it's possible in this case that most other songs may not fit with the user's preference. With this, the only accurate set of data for recommending songs would be "lofi" as a genre since it has more than one entry in the dataset. Additionally, with how the score is weighed by features of the song, some features may not be prioritized into the score as much as others which can create bias in whether the recommender system recommends music to the user because the genre/mood is the same, rather than recommending music to the uesr because it "vibes" with them.
 

