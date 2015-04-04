#Twirps is a visual mapping of how much MPs communicate with 
#each other on social media.  It will use the parl_db database, and its
#own twirpy.db for any extra data.
import sqlite3
import requests
import dataset
import time
import tweepy
import json
import os
import tweepy_key as tk


def create_twirpy_db():
    
    if not os.path.exists('./twirpy.db'):
        with sqlite3.connect('twirpy.db') as connection:
            cur = connection.cursor()
            cur.execute('CREATE TABLE TweetData (UserID Number, UserHandle Text,\
                                                ToIds Number, ToHandle Text, Count Number, \
                                                Content Text, Retweet Text, Hashtags Text )')
            cur.execute('CREATE TABLE TwirpData (UserID Number UNIQUE, UserName Text, Handle Text, \
                                                FollowersCount Number, FriendsCount Number,\
                                                TweetCount Number, RetweetCount Number, \
                                                BeenRetweeted Number, FavouriteHashtag Text, \
                                                HashtagCount Number, OfficialId Number)')

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


def collect_twirp_data(api, handle, official_id):
    
    twitter_user = api.get_user(screen_name=handle)
    twirp = Twirp(twitter_user, 'twitter')
    twirp.official_id = official_id
    
    print twirp
    twirp.to_database()

# def pull_tweets_from_user(api, handle):
#     print handle
#     mp = api.get_user(screen_name=handle)
#     for status in tweepy.Cursor(api.user_timeline, id=mp.id).items(1000):
#         tweet_parser(status)

#         for mention in status.entities['user_mentions']:
#             print i, mention['screen_name'], '\t', status.text
    
#     time.sleep(45)


def monitor_calls(api):
    '''This function will return the number of requests remaining and the 
    session expiration time, for a certain request, specified in the ar'''

    monitor = api.rate_limit_status()
    print json.dumps(monitor, sort_keys=True,
                    indent=4, separators=(',', ': '))
    return ()

        
class Tweet(object):
    def __init__(self, tweet):
        pass

    def parse_tweet(self, tweet):
        pass

    def to_database(self):
        pass



class Twirp(object):
    def __init__(self, user, source):
        self.statuses = 0
        self.followers_count = 0
        self.friends_count = 0
        self.geo = False
        self.id = 0
        self.name = ''
        self.handle = ''
        self.official_id = 0 
        self.retweet_count = 0
        self.been_retweet_count = 0 
        self.favourite_hashtag = 'NULL'
        self.hashtag_count = 0

        if source=='twitter':
            self.from_twitter(user)

        elif source=='database':
            self.from_database(user)

    def __str__(self):
        return '||%s : %s\n||Id %d; Fol %d; Fri %d; Geo %s ' % (
            self.handle, self.name, self.id, 
            self.followers_count, self.friends_count, self.geo )

    def from_twitter(self, user ):
        self.statuses = user.statuses_count
        self.followers_count = user.followers_count
        self.friends_count = user.friends_count
        self.geo = user.geo_enabled
        self.id = user.id
        self.name = user.name
        self.handle = user.screen_name
        self.official_id = 0

    def to_database(self):
        input_tuple =  (self.id, self.name, self.handle, self.followers_count, 
                        self.friends_count, self.statuses, self.retweet_count, 
                        self.been_retweet_count, self.favourite_hashtag,
                        self.hashtag_count, self.official_id)

        with sqlite3.connect('twirpy.db') as connection:
            cur = connection.cursor()
            cur.execute('INSERT OR REPLACE INTO TwirpData\
                        VALUES (?,?,?,?,?,?,?,?,?,?,?) ', input_tuple)


    def from_database(self, user):
        pass




if __name__ == '__main__':
    to_do_list = return_twitter_list()
    print to_do_list[0]
    session_api = authorize_twitter()
    create_twirpy_db()

    collect_twirp_data(session_api, 'KeeleyMP',1)
    monitor_calls(session_api)

