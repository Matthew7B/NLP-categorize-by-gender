# NLP-categorize-by-gender

Using BERT we can make a text predictor that's 75% accurate in distinguishing users who identify themselves as male/female using their chat messages from the social platform discord.
It's trained on a small sample set of discord chat which isn't included in this repo. The model I've trained also is unavailable due to file size restrictions.

Since the model only requires text as an input we can run it on other content such as movie dialogue from Marvel Avengers, which would return:
  NICK FURY ♂ 83%
  COULSON ♂ 73%
  FURY ♂ 73%
  LOKI ♂ 59%
  NATASHA ♂ 92%
  BRUCE ♂ 60%
  BANNER ♂ 83%
  STEVE ♂ 87%
  TONY ♂ 80%
  PEPPER ♀ 59%
  CAPTAIN AMERICA ♂ 56%
  IRON MAN ♂ 76%
  THOR ♂ 75%

There are many limitations of this project, such as the small size of the training data, quality of the training data, lack of fine tuning, and the developers lack of familiarity with the data.
