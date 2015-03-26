#Twirps is a visual mapping of how much MPs communicate with 
#each other on social media.  It will use the parl_db database, and its
#own twirpy.db for any extra data.
import sqlite3
import requests
import dataset
import time
import tweepy
import tweepy_key as tk


def create_twirpy_db():
    with sqlite3.connect('twirpy.db') as connection:
        cur = connection.cursor()
        cur.execute('CREATE TABLE RawData (UserID Number, UserHandle Text, Type Text,\
                                            ToId Number, ToHandle Text, Count Number, \
                                            Content Text, Relevant Boolean)')
        cur.execute('CREATE TABLE UserData (UserID Number, TweetCount Number,\
                                            RetweetCount Number, BeenRetweeted Number,\
                                            FavouriteHashtag Text, HashtagCount Number ')

def authorize_twitter():
    auth = tweepy.auth.OAuthHandler(tk.consumer_key, tk.consumer_secret)
    auth.set_access_token(tk.access_token, tk.access_secret)

    api = tweepy.API(auth)
    return api 

def return_twitter_list():
    with sqlite3.connect('../parl.db') as connection:
        cur = connection.cursor()
        cur.execute('SELECT OfficialId, Address FROM Addresses WHERE Type="Twitter"')
        tuplelist = cur.fetchall()
    return tuplelist


def add_to_database(table, item):
    pass

def collect_data(api, handle):
    
    twitter_user = api.get_user(screen_name=handle)
    twirp = Twirp(twitter_user)
    
    add_to_database('users', twirp.to_database())




# def pull_tweets_from_user(api, handle):
#     print handle
#     mp = api.get_user(screen_name=handle)
#     for status in tweepy.Cursor(api.user_timeline, id=mp.id).items(1000):
#         tweet_parser(status)

#         for mention in status.entities['user_mentions']:
#             print i, mention['screen_name'], '\t', status.text
    
#     time.sleep(45)

        
class Tweet(object):
    def __init__(self, tweet):
        pass

    def parse_tweet(self, tweet):
        pass

    def to_database(self):
        pass

class Twirp(object):
    def __init__(self, user):
        self.statuses = ''
        self.followers = 0
        self.friends = 0
        self.geo = False
        self.id = 0
        self.name = ''
        self.handle = ''

        parse_entity()
        pass

    def parse_user(self, user):
        pass

    def to_database(self):
        pass




if __name__ == '__main__':
    to_do_list = return_twitter_list()
    print to_do_list[0]
    session_api = authorize_twitter()

    # pull_tweets_from_user(session_api, 'KeeleyMP')