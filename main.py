import requests
import pandas as pd
import twint
from bs4 import BeautifulSoup
import time
import json
import datetime
from pymongo import MongoClient
import pymongo
import string

import twint
import re
from langdetect import detect, detect_langs
from contextlib import suppress

from langdetect.lang_detect_exception import LangDetectException
from nltk import PorterStemmer, word_tokenize
from nltk.corpus import stopwords
import nltk


def executeQuery(user, AcceptedUserCol, keyWords):
    c = twint.Config()
    c.Username = user
    c.Limit = 30
    c.Pandas = True
    # Run
    twint.run.Search(c)

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
                eng_count += 1

                ## Then check if contains key words
                # Remove Numbers
                tweet = re.sub(r'\d+', '', tweet)
                # Remove special chars
                tweet = re.sub(r"\W+|_", " ", tweet)
                # remove spaces
                tweet = tweet.translate(str.maketrans('', '', string.punctuation))

                stop_words = nltk.download('stopwords')
                stemmer = PorterStemmer()
                text2 = word_tokenize(tweet)
                full_processed_tweet = [stemmer.stem(i) for i in text2 if not i in stop_words]

                if (set(full_processed_tweet) & set(keyWords)):
                    key_count += 1

    if key_count > 0:
        query = {"user": user}
        AcceptedUserCol.insert(query)


def main():
    client = MongoClient(
        "mongodb+srv://thomas:thomas123@cluster0-0kckv.mongodb.net/test?retryWrites=true&w=majority")

    acceptedUserCol = client['twitter']['accepteduser']
    todoCol = client['twitter']['usersToDo']
    keyWords = client['twitter']['keyWords']
    currentQuery = todoCol.find_one_and_delete({})
    while currentQuery != None:
        print(currentQuery)
        executeQuery(currentQuery["user"], acceptedUserCol, keyWords.find_one({})['keyWords'])
        print(currentQuery["user"])
        currentQuery = todoCol.find_one_and_delete({})


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    main()
# [END gae_python38_app]