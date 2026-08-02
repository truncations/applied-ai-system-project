## Limitations and Biases in System

### Limitations
1. Small catalog of music. Although there is a variety of genres, there's not enough music that are in each genre.
2. Each song has a single label for genre and mood. However, most songs in the real world usually combine genre and moods. So songs that have hybrid genre/moods (if it were integrated into the dataset) would be punished for this mixing.
3. Because the memory of the AI isn't stored, there's a full refresh everytime, and so results can sometimes skew heavily from a slight difference in wording.
4. The genre/mood always has more importance over other attributes used in consideration like energy or danceability, even if the user cares way more about those particular aspects. 

### Biases

1. False confidence by AI means it could/can potentially give songs that may not fit the user's preferences even if they explicitly state it for a particular field.
2. There is representational bias in the dataset provided where music in electronic have their own sub-genres but everything else doesn't which could lead to homogenizing recommendations for those genres.
3. As described above in limitations, the weighing of music is not distributed well and is merely only accurate towards whether the song's content features (genre/mood) are truly similar rather than the feeling of the song (tempo/energy/acousticness).
4. Gemini is trained on data and attempts to associate words with some sort of value (for our system) which can lead to widely skewed predicted user preferences if two users describe the same personal taste but in different words due to Gemini's stereotype of the genre they named.

## Could AI be misused in this program?

This is probably my biggest flaw, and it is likely so. Since the scoring formula is standardized to what I gave it in recommender.py (the weighing for each attribute for each song never changes, it's the same), someone can make a song that could theoretically maximize a score by "beating the algorithm" even if it doesn't fit towards the user's preferences. Additionally, there's some vulnerability with prompt injection anytime a user is asked to provide their preferences (to be recommended music). A possible response could potentially manipulate scores/confidence to make the AI seem more confident than it actually is, misleading the user to a recommended song.

In order to prevent this, I would have to overhaul the scoring system and weigh it based on the user's request, determining what they are prioritizing so that the attribute weights can be distributed properly. Additionally, in order to reduce prompt injection I should've written a guardrail that prevents manipulation of AI behavior and only keeps to what has already been provided.

## Surprises during testing of AI's reliability

A slight change in wording to request songs that the user prefers will adjust the outcome (un-negligibly), even if the words in a sentence are reordered.

For example, 
"I would like some intense rock music that is highly upbeat and energetic, something to keep me awake."
vs.
"I would like some rock intense  music that is highly upbeat and energetic, something to keep me awake."

produces quite different results (the song list is the same but the ranks of the songs are kind of reordered). In fact, the average of the scores of the top 5 songs being recommended is higher on the 2nd prompt (16.85) than if the 1st prompt (16.688) was sent. 

## Collaboration with AI during this project.

My collaboration with Artifical Intelligence during this project has been the same as my past projects, using it to assist me in developing my architected ideas. I asked it questions to understand why it wrote the program the way it did, and when I felt that something was wrong or an error was produced realtime/during compiling, I noted this to the LLM I utilized to help tailor it to provide me improved results.

One instance that I accepted was how it implemented the `attr_score_str` method, as it now uses a similarity score and is overall clean programming. When I saw this suggestion, upon observation of the code, I felt confident immediately that it would work first try. 

However, one instance that I denied was the lack of implementation of a cache to store already embedded words to prevent the AI from having to recompile them again. When I went through with the process of text embedding to do similarity scoring of genre/intensity, I noticed it completely glossed over the idea of caching, a way of preventing recompiling of data if it already has compiled it before, reducing the cost and improving performance. When I noticed this, I denied the suggestion because I thought about the cost of using an AI Embedding API and how much this would tank my usage (which is bad to say the least).