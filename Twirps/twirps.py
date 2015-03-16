#Twirps is a visual mapping of how much MPs communicate with 
#each other on social media.  It will use the parl_db database, and its
#own twirpy.db for any extra data.
import sqlite3
import requests
import tweepy
import tweepy_key as tk


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


def pull_tweets_from_user(api, handle):
    
    mp = api.get_user(screen_name=handle)

    for status in tweepy.Cursor(api.user_timeline, id=mp.id).items(1000):
        print status.text


if __name__ == '__main__':
    to_do_list = return_twitter_list()
    print to_do_list[0]
    session_api = authorize_twitter()

    pull_tweets_from_user(session_api, 'KeeleyMP')