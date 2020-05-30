import string

import twint
import re
from langdetect import detect, detect_langs
from contextlib import suppress

from langdetect.lang_detect_exception import LangDetectException
from nltk import PorterStemmer, word_tokenize
from nltk.corpus import stopwords

c = twint.Config()
c.Username = user
c.Limit = 1
c.Pandas = True
# Run
twint.run.Search(c)

key_words = open('KeyWords.csv', 'r').read().split('\n')

# now you will have some tweets
Tweets_df = twint.storage.panda.Tweets_df

eng_count = 0
key_count = 0

for index, row in Tweets_df.iterrows():
    tweet = row['tweet']

    # Make Lower case
    tweet = tweet.lower()
    # Remove links
    tweet = re.sub(r'http\S+', '', tweet)
    # remove non https links
    tweet = re.sub("\\s*[^ /]+/[^ /]+", "", tweet)

    ##check if english
    with suppress(LangDetectException):
        lang = detect(tweet)
        if lang == 'en':
            eng_count+=1

            ## Then check if contains key words
            # Remove Numbers
            tweet = re.sub(r'\d+', '', tweet)
            # Remove special chars
            tweet = re.sub(r"\W+|_", " ", tweet)
            # remove spaces
            tweet = tweet.translate(str.maketrans('', '', string.punctuation))

            stop_words = set(stopwords.words('english'))
            stemmer = PorterStemmer()
            text2 = word_tokenize(tweet)
            full_processed_tweet = [stemmer.stem(i) for i in text2 if not i in stop_words]

            if(set(full_processed_tweet) & set(key_words)):
                key_count+=1



if key_count > 0:
    #save name in different db torrie
