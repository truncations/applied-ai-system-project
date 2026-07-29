# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

**MusicFitRecommender 1.0**

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

My recommender is designed to help people, or recommend to people new songs to listen to based on the music that they prefer. The assumptions that it makes about the user is that it assumes the user has one set of preferences, and that if the user likes acousticness/danceability, that the extreme amounts of danceability and acousticness will be considered highly valuable. This is for real users who want to find music on their own.

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

The features that are being used for comparison to determine similarities with a song and a user's preference are of the following from the song: genre, energy, mood, valence, acousticness, danceability, tempo_bpm. The user preferences that are considered are the features being considered from the songs. In order to turn these features into a score, we use mathematical formulas and analysis to observe similarities.
    - For values, we calculate the error/absolute difference between a song's feature and the user's target value
    - For words/text, we simply check if the song's feature is exactly matching the user's target.
    - For true/false situations, we calculate the error from the song's feature to the extreme values like 0, 1 depending on if the user likes the feature or doesn't (acousticness and danceability exclusive)
Then, for each score after being computed, we scale them/weigh them based on this following list where the first entry in the list is the highest weight, and the last entry is the lowest weight and shows the maximum number of points that can be awarded:
    1. genre: 7
    2. mood: 5
    3. energy: 3
    4. valence: 2
    5. danceability: 1
    6. acousticness: 0.75
    7. tempo_bpm: 0.5
After computing each score for each feature, we'll add/sum the scores together to get a final similarity score for the song provided.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

The dataset the model uses is simply a list of songs with their features, like title, artist, genre, and more. There are 18 songs in the catalog. The genres/moods being represented generally try to touch on most of the music that are out in public, although it still misses genres/moods like "R&B, reggae, punk, EDM, K-pop" and "anxious, anger, playful, silly" and whatnot. I added data and didn't remove any data.

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

When genre+mood matches are successful, they distinguish the songs very well from "full matching" to "partial matching" with genre/mood generally. It gives a wide score gap that is heavily deserved. Additionally, the numerical tiebreaking is successful and is shown when testing with "lofi-chill" user profile, where the songs Midnight Coding and Library Rain both exactly match the user's preferences with Genre+Mood, but the tiebreaker occurs for Midnight Coding to win because it had closer energy/danceability similarity. Furthermore, one case where the recommendations matched my intuition almost closely was when testing the "rock-intense" user profile, I was able to get the top 5 songs to be mostly in the ballpark, with "Storm Runner" and "Iron Descent" being the top few songs which supported my intuition.

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

Some limitations of my systems that create bias are that genres and moods must be exactly matching, even though some genres and moods can be similar but not exact to the user's preference. (TLDR; hybrid genres are highly penalized) Mood is heavily fragmented as most of the dataset have their own unique moods, and so it leads to genre+mood being relied on rather than actual music taste. Additionally, for the acousticness/danceability attributes of a song, they are strictly based on whether a user likes acousticness or likes danceability, where if they do "like" acousticness/danceability that higher values reward more, and vice versa rather than actually finding the target acousticness/danceability value that someone would prefer which creates bias; for example, some users may like acousticness but not heavy acoustic.

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

I checked whether the recommender behaved as expected by testing user profiles. As shown in main.py, I tested for user profiles such as "lofi-chill", "classical-melancholic", and "rock-intense". For each profile and their recommended songs, I analyzed the top 5 recommended song's attributes and manually determined similarities based on knowledge of music as well as numbers given (from data/songs.csv)--I took the recommended song's name, found it in the dataset and observed comparisons and differences from the user's profile. For example, on "lofi-chill", I made sure that the top songs were also similar by having the same genre or mood. What surprised me the most was when I tested "rock-intense" profile where it seemingly preferred the music "Gym Hero" over "Iron Descent" even though "Iron Descent" is clearly more similar (Metal-aggressive) than "Gym Hero" (pop-intense). This bias occurred since we only do exact-matching moods/genres. Additionally, another surprise was that my scoring system focused on label matching rather than genuine musical similarity, which made it hard to observe other behavior. However, one I noticed was that "rock-intense" profile preferred songs with lower acousticness-danceability and higher energy, while "lofi-chill" focused on lower energy with higher acousticness.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

For the next time, I would like to improve the model by adding further capabilities to the system. I would like to add features that improve accuracy such as "hybrid-genre/mood matching" where if a genre/mood is similar to a user's preferred genre/mood but isn't exact, still give some compensating points. Then, I would like to add the ability to limit the number of songs that are created by the same artist so that there is an improved diversity among the top results. Furthermore, a user may not just have one single preference they stick to, they may have multiple preferences of music, such as listening to rock or lofi, and that should be considered rather than assuming one set of preferences for one single genre is enough. This implementation would then further improve the dilemma with improving diversity among the top results.

Lastly, I very likely should've used the classes to further support my evidence that upon testing the program using the test cases provided by tests/test_recommender.py, that the program would prove to be successful in at least completing it's main goals.

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  

What I learned about recommender systems is that they're not exactly magical in tha tthey can magically recommend songs that fit what you exactly want, it is simply a systesm of prediction; they make guesses upon what should be recommended to you based on statistics, numbers, and comparison methods like similarity, so if a song has values that aren't far off hwat oyu may prefer (as recommender systems usually would build data on what you prefer), then it will recommend it to you even if it is heavily contrasting. One thing I didn't expect is that this whole system resonates with machine learning and how you can take simple algorithms like a basic mathematical error formula (1 - |A - B|) and manage to make a prediction model that guesses what may occur next, which is what this music recommender system showed. Using AI tools helped me to implement my program and find improvements to my initial plans of constructing an algorithm for a recommendation system. Additionally, AI helped to find errors in my system that I may not catch super easily (which would ironically take me hours). If I had to extend this project, I would try to make it so that the recommender system learns about the person rather than giving a set data of user preferences so that I can give a more accurate recommendation of songs.