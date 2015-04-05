#Twirps is a visual mapping of how much MPs communicate with 
#each other on social media.  It will use the parl_db database, and its
#own twirpy.db for any extra data.
from __future__ import unicode_literals
import sqlite3
import requests
import dataset
import time
import tweepy
import json
import os
import tweepy_key as tk




def create_twirpy_db():
    '''Creates a database with tables for TweetData and TwirpData'''
    
    if not os.path.exists('./twirpy.db'):
        with sqlite3.connect('twirpy.db') as connection:
            cur = connection.cursor()
            cur.execute('CREATE TABLE TweetData (UserID Number, UserHandle Text, FavouriteCount Number, \
                                                RetweetCount Number, Content Text, Retweet Text, \
                                                CreatedDate Text, TwitterID Number UNIQUE)')
            cur.execute('CREATE TABLE TwirpData (UserID Number UNIQUE, UserName Text, Handle Text, \
                                                FollowersCount Number, FriendsCount Number,\
                                                TweetCount Number, RetweetCount Number, \
                                                BeenRetweeted Number, FavouriteHashtag Text, \
                                                HashtagCount Number, OfficialId Number)')
            cur.execute('CREATE TABLE TweetEntities (TweetID Number, UserId Number,\
                                                EntityType Text, Entity Text, ToUser Number)')


def authorize_twitter():
    '''Authorizes the session for access to twitter API'''

    auth = tweepy.auth.OAuthHandler(tk.consumer_key, tk.consumer_secret)
    auth.set_access_token(tk.access_token, tk.access_secret)

    api = tweepy.API(auth)
    return api 




def return_twitter_list():
    '''Returns a list of tuples, each containing an MPs OfficialId and Twitter handle'''

    with sqlite3.connect('../parl.db') as connection:
        cur = connection.cursor()
        cur.execute('SELECT OfficialId, Address FROM Addresses WHERE Type="Twitter"')
        tuplelist = cur.fetchall()
    complete_mp_list = [(o_id, handle[20:]) for o_id, handle in tuplelist]
    return complete_mp_list

def return_skip_list():
    '''Returns a list of tuples, each containing OfficialId and Twitter handle for 
Twirps that have already been collected'''

    with sqlite3.connect('twirpy.db') as connection:
        cur = connection.cursor()
        cur.execute('SELECT OfficialId, Handle FROM TwirpData')
        tuplelist = cur.fetchall()
    return tuplelist

def collect_twirp_data(api, handle, official_id):
    '''Feeding in the session, a handle and it's mp's official id, this queries the
the twitter API, instantiates Twirp class with the data and populates the database 
with that record'''

    twitter_user = api.get_user(screen_name=handle)
    twirp = Twirp(twitter_user, 'twitter')
    twirp.official_id = official_id

    print unicode(twirp)
    twirp.to_database()

def collect_tweet_data(api, user_id, since_id=None):
    '''Feeding in the session, a user_id and possibly tweet id, this queries the 
twitter API, instantiates a Tweet class with data and populates the database with 
that tweet'''

    for tweet_data in tweepy.Cursor(api.user_timeline, id=user_id).items(20):

        try:
            tweet = Tweet(tweet_data, 'twitter')
            #print tweet, '\n'
            tweet.to_database()
        except Exception, e:
            print e


def monitor_calls(api):
    '''This function will return the number of requests remaining and the 
session expiration time, for a certain request, specified in the ar'''

    monitor = api.rate_limit_status()
    print json.dumps(monitor, sort_keys=True,
                    indent=4, separators=(',', ': '))
    return ()

def get_twirps_main(api):
    complete_mp_list = return_twitter_list()
    fetched_mp_list = return_skip_list()

    remaining_mp_list = list(set(complete_mp_list)-set(fetched_mp_list))

    print remaining_mp_list 

    for mp_tuple in remaining_mp_list:
        try:
            collect_twirp_data(api, mp_tuple[1], mp_tuple[0])
        except Exception, e:
            print e

def get_tweets_main(api):
    pass


        
class Tweet(object):
    def __init__(self, tweet, source):
        self.tweetid = 0
        self.userid = 0
        self.handle = ''
        self.mentions = [] 
        self.content = ''
        self.retweet = 'NULL'
        self.retweet_count = 0
        self.favourite_count = 0
        self.hashtags = []
        self.date = ''
        self.urls = []

        if source=='twitter':
            self.from_twitter(tweet)

        elif source=='database':
            self.from_database(tweet)

    def from_twitter(self, tweet):
        self.tweetid  = tweet.id
        self.userid = tweet.user.id
        self.handle = tweet.user.screen_name
        self.mentions = [ (ent['id'],ent['screen_name'] 
                            ) for ent in tweet.entities['user_mentions'] ]
        self.content = tweet.text
        if tweet.retweeted:
            self.retweet = 'YES'
            #tweet.retweeted_status['user']['id']
        self.retweet_count = tweet.retweet_count
        self.favourite_count  = tweet.favorite_count
        self.hashtags =  [ent['text'] for ent in tweet.entities['hashtags']]
        self.date = tweet.created_at
        self.urls = [urls['expanded_url'] for urls in tweet.entities['urls']]

        if tweet.in_reply_to_user_id != None:
            #self.mentions.append((tweet.in_reply_to_user_id, tweet.in_reply_to_screen_name))
            self.retweet = 'reply'
        pass

    def __str__(self):
        return u'Tweet %d %s ||RC: %d FC:%d RT:%s||\n @ %s || # %s || Url %s\nContent: %s' %(
            self.tweetid, self.handle, self.retweet_count, self.favourite_count,
            self.retweet, str(self.mention_handles), str(self.hashtags), str(self.urls),
            unicode(self.content) )

    def from_database(self, tweet):
        pass

    def to_database(self):
        input_tuple = (self.userid, self.handle,  self.favourite_count, self.retweet_count,
            self.content, self.retweet,  self.date, self.tweetid )

        with sqlite3.connect('twirpy.db') as connection:
            cur = connection.cursor()
            cur.execute('INSERT OR REPLACE INTO TweetData\
                        VALUES (?,?,?,?,?,?,?,?) ', input_tuple)
            for h in self.hashtags:
                cur.execute('INSERT INTO TweetEntities VALUES (?,?,?,?,0)',
                    (self.tweetid, self.userid, 'hashtag', h))
            for u in self.urls:
                cur.execute('INSERT INTO TweetEntities VALUES (?,?,?,?,0)',
                    (self.tweetid, self.userid, 'url', u))
            for m in self.mentions:
                cur.execute('INSERT INTO TweetEntities VALUES (?,?,?,?,?)',
                    (self.tweetid, self.userid, 'mention', m[1], m[0]))

        



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
        return u'||%s : %s\n||Id %d; Fol %d; Fri %d; Geo %s ' % (
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
    session_api = authorize_twitter()
    create_twirpy_db()

    #get_twirps_main(session_api)
    collect_tweet_data(session_api, 388954439)
    #monitor_calls(session_api)



# def pull_tweets_from_user(api, handle):
#     print handle
#     mp = api.get_user(screen_name=handle)
#     for status in tweepy.Cursor(api.user_timeline, id=mp.id).items(1000):
#         tweet_parser(status)

#         for mention in status.entities['user_mentions']:
#             print i, mention['screen_name'], '\t', status.text
    
#     time.sleep(45)


