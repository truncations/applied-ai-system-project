## Original Project

Originally named: 🎵 Music Recommender Simulation

Originally, the goal of this program was to recommend songs to a person based on their preferences and the content that already existed. It's capabilities were to take songs, score them based on whether it was near the user's preference targets, and find the top number of songs with the highest scores (which represented a high similarity to the user's preference of songs)

## Title And Summary

**🎵 Friendly Music Recommender Station+**

This project recommends music a person based on the person's chosen preferences and attempts to find content/music that is most similar to the person's preferences and provide friendly reasoning for the song, all of which uses Artifical Intelligence (Gemini API Embedding/Gemini Flash Latest & Gemini Flash Latest Lite) to help with the process. This project matters as it helps for a person to find new music that they may want to listen to instead of listening to the same old music.

## Architecture Overview

There are 5 components that all tie together to make this system work:
- CLI Runner: Load catalog of songs, wait for the person to request some action (show logs, recommend me music, or quit the program). This is where all the results are shown.
- Embeddings: Parse what the user wants for their recommended music into a structured UserProfile and document confidence for each attribute of a song. This is also where results will be turned into natural language reasons that a human can read to show the reasoning behind the song being recommended. The process of calling both main functions for embedding is stored in a logger.
- Scoring Engine: Score songs (with weight) based on their similarity to the user's preference using algorithms for numbers, Gemini AI for text to understand whether the attribute is exact, close, or not close to the user's preference, and boolean matches if needed.
- Data Layer: Contains the 50-song catalog, a cached embeddings file to reduce the amount of cost of using the Gemini Embedding API.
- Human-In-The-Loop: Use pytest to do unit testing on scoring logic without having the LLM involved. Additionally, the user/developer can spot-check of low confidence results by checking the CLI output or by the logs command.

## Setup Instructions

### 1. Create a virtual environment (recommended)

```bash
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
# or
.venv\Scripts\activate      # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup .env for Gemini API

If there is not an ".env" file in the project folder, create one like so:
<PROVIDE IMAGE PLEASE>
Then, navigate to https://aistudio.google.com/app/api-keys to get a Gemini API key (This program ONLY works with Gemini AI). Once a Gemini API key is generated, copy and paste the API key and write to ur .env file as shown below:

```env
GEMINI_API_KEY = <PASTE API KEY HERE>
```

## Sample Interactions

### Interaction/Input 1:
    **I want some new exciting music that could keep my energy high while I dance to it. I really enjoy music that are quite fast like rave DJ music.**
```
Parsing your request into a taste profile...
Writing a natural-language explanation of your recommendations...

============================================================
Request: I want some new exciting music that could keep my energy high while I dance to it. I really enjoy music that are quite fast like rave DJ music.
Parsed profile: {'favorite_genre': 'electronic', 'target_energy': 0.9, 'favorite_mood': 'exciting', 'target_tempo_bpm': 130, 'likes_dance': True, 'likes_acoustic': False, 'target_valence': 0.75, 'k': 5}

Here are five high-energy electronic tracks with fast tempos and exciting beats to keep you dancing.

1. Warehouse 3AM - Kilotone (score: 17.77)
   With its strong electronic genre match and high-energy feel, Warehouse 3AM brings the
   exact exciting rave vibe you need to keep dancing. Its fast tempo and low
   acousticness make it perfect for intense dance sessions.

2. Electric Bloom - Wavecrest (score: 17.51)
   Electric Bloom hits an exciting mood with an electronic beat that aligns well with
   your requested tempo and energy. It offers a great balance of danceable rhythm and
   upbeat synth tones to keep you moving.

3. Gym Hero - Max Pulse (score: 17.23)
   Designed to keep your heart pumping, Gym Hero delivers high danceability and
   energetic drive matching your fast-paced rave preference. Its bright valence and
   electronic punch make it an exciting pick for dancing.

4. Marathon Mind - Max Pulse (score: 17.21)
   Featuring upbeat energy and high danceability, Marathon Mind maintains a fast tempo
   to power your dance session. Its synthetic production ensures you get the full thrill
   of a rave DJ set.

5. Boardwalk Skank - The Offbeats (score: 17.10)
   Boardwalk Skank brings a high-mood match with cheerful valence and danceable beats
   that suit an energetic dance party. Its non-acoustic, driven style keeps your energy
   high throughout.
```

### Interaction/Input 2:
    **I am feeling a little quiet today, I would like music that is slow and a little bit more calming mood to get me through the day.**
```
============================================================
Request: I am feeling a little quiet today, I would like music that is slow and a little bit more calming mood to get me through the day.
Parsed profile: {'target_tempo_bpm': 70, 'likes_dance': False, 'target_energy': 0.2, 'favorite_mood': 'calm', 'target_valence': 0.4, 'favorite_genre': 'lofi', 'likes_acoustic': True, 'k': 5}

Here are five slow, calming, and gentle tracks to help you relax and comfortably navigate a quiet day.

1. Paper Boats - Paper Lanterns (score: 17.79)
   With its lofi style and calm atmosphere, Paper Boats delivers a gentle, low-energy
   sound with a slow tempo and soft acoustic feel ideal for a quiet day.

2. Quiet Snowfall - Elena Voss (score: 17.69)
   Quiet Snowfall captures an exceptionally calming mood with low energy, slow pacing,
   and acoustic warmth to give you a peaceful background for your day.

3. Library Rain - Paper Lanterns (score: 17.36)
   Library Rain provides a soothing lofi soundscape with a slow tempo and low energy
   that creates an effortless, quiet listening experience.

4. Hallway Echoes - Orbit Bloom (score: 17.13)
   Featuring a calm vibe and slow tempo, Hallway Echoes offers a mellow, low-energy
   listen with warm acoustic tones.

5. Afterglow - LoRoom (score: 17.10)
   Afterglow brings a relaxing lofi style with low energy and slow tempo to keep your
   day feeling peaceful and soft.
```

### Interaction/Input 3:
    **I am feeling absolutely crazy today! I am a HUGE rock fan and I am looking for music in rock that is insanely fast, maximum intensity, maximum energy, maximum dance, and absolutely high BPM like 300-400! Just make sure it has 0 acousticness or I will be upset. :)**
```
============================================================
Request: I am feeling absolutely crazy today! I am a HUGE rock fan and I am looking for music in rock that is insanely fast, maximum intensity, maximum energy, maximum dance, and absolutely high BPM like 300-400! Just make sure it has 0 acousticness or I will be upset. :)
Parsed profile: {'target_tempo_bpm': 350, 'target_valence': 0.9, 'target_energy': 1, 'likes_dance': True, 'favorite_genre': 'rock', 'favorite_mood': 'crazy', 'likes_acoustic': False, 'k': 5}

Here are high-energy rock picks tailored to your intense, crazy mood with maximum power, zero acoustic vibe, and great danceability.

1. Storm Runner - Voltline (score: 16.72)
   This track is an exact rock genre match with maximum energy and a great fit for a
   crazy mood, keeping acousticness strictly at bay while offering high intensity.

2. Gym Hero - Max Pulse (score: 16.36)
   Gym Hero packs intense energy and uplifting mood alignment, giving you an electric,
   non-acoustic rock feel with strong danceability.

3. Marathon Mind - Max Pulse (score: 16.35)
   Delivering huge energy and zero acoustic downtime, this rock track pairs strong
   danceability with a wild mood match to keep you moving.

4. Neon Pulse Rave - DJ Fractal (score: 16.34)
   With high danceability, great positive intensity, and strong rock energy, this track
   delivers a purely non-acoustic surge for your crazy mood.

5. Champagne Static - DJ Fractal (score: 16.24)
   Champagne Static brings high energy, strong danceability, and high valence wrapped in
   a heavy, non-acoustic rock style.
```

## Design Decisions
Some design decisions I made:
- I kept hard-coded point values per attributes because it would prevent the AI from hallucinating scores that might not accurately represent a user's tastes. However, to reduce hallucinations, it means of some limitations such as the genre/mood having more importance always over other attributes used in consideration like energy or danceability, even if the user cares way more about those particular aspects.
- I made sure the LLM couldn't just think of anything on its own. In fact the only time the LLM actually does anything is to parse text and rewrite text already provided which helps to reduce the chances of hallucination especially in song data/scores, but it actually increased the cost of using the LLM (to 2 instead of 1).
- The LLM grades itself for confidence which isn't always a valid metric to use to determine the LLM's performance for recommending music. However, it was the fastest way to be able to at least test the LLM's performance in the first place.

## Testing Summary
    In order to prove that the AI works, we can do multiple tests that I implemented throughout this program.

    You can use pytest to test for some of the basic functions of recommending music, shown in tests/test_recommender.py. (Both pass).

    Additionally, the AI logs its confidence for each attribute scored and whether any errors occurred during the process of calling the Gemini API embedder/Gemini AI. You can access these logs using "logs" or "log" as the command during your next request. Overall, when I used the sample interactions, upon checking the logs, it seems that the AI felt highly more confident when the user was explicit with their requests (ex. I want a song with a tempo BPM of 100, maximum energy, maximum acousticness!). However, there were no times where the AI didn't feel "unconfident" of their prediction (the 'level' wasn't 'low').

## Reflection
    This project taught me that using Artificial Intelligence has some uses and some negatives, and to consider it as an option for implementation to improve user engagement, especially as shown with this music recommender system as it tries to appeal to the person and explain to them in natural language the reasoning almost as if a companion for music searching. Additionally, this project helped me to problem solve in situations where I got stuck due to errors in the program I made. I would talk to Artificial Intelligence to diagnose the problem, asking why writing the code the way I did would lead to such error, and what are some more pythonic ways to write code that is either more efficient or more readable. 