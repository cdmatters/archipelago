import sqlite3
import time 
import sys
import json
import unicodedata
import operator

START_TIME = time.time()


def return_top_10():
    stored_names = generate_stored_twirp_list()

    with open('hashtag_freq.json', 'r') as f:
        hashtag_dict = json.load(f)
    with open('mention_freq.json', 'r') as m:
        mention_dict = json.load(m)
    with open('word_freq.json', 'r') as w:
        word_dict = json.load(w)

    for name, user_id in stored_names:
        sorted_hashtags = sorted(hashtag_dict[name].items(), key=operator.itemgetter(1), reverse=True)
        sorted_mentions = sorted(mention_dict[name].items(), key=operator.itemgetter(1), reverse=True)
        sorted_words = sorted(word_dict[name].items(), key=operator.itemgetter(1), reverse=True)
        print 'NAME: %s' %name, '\n'
        
        top_h = sorted_hashtags[:10]
        top_m = sorted_mentions[:10]
        top_w = sorted_words[:10]

        if len(top_h)<10:
            top_h.extend([(0,0)]*(10-len(top_h)))
        if len(top_m)<10:
            top_m.extend([(0,0)]*(10-len(top_m)))
        if len(top_w)<10:
            top_w.extend([(0,0)]*(10-len(top_w)))

        template = "{0:5}|{1:25}{2:5}||{3:15}{4:5}||{5:15}{6:5}||"
    
        print template.format('Order', 'HASHTAG','No.','WORDS','No.','MENTIONS','No.')
        for i in range(0,10):
            in_tuple = (i, top_h[i][0], top_h[i][1], top_w[i][0], top_w[i][1], top_m[i][0], top_m[i][1])
            try:
                print template.format(*in_tuple)
            except:
                print 'Error'


        print '\n\n\n'
    lap_time()





def generate_hashtag_frequency_json():
    stored_names = generate_stored_twirp_list()
    results = {}

    for name, user_id in stored_names:
        print name
        results[name] = {}
        tweet_list = select_entities_by_twirp(user_id, 'hashtag')

        for hashtag in tweet_list:
            if hashtag[3].lower() in results[name].keys():
                results[name][hashtag[3].lower()] +=1
            else:
                results[name][hashtag[3].lower()] =1

    with open('hashtag_freq.json', 'w+') as f:
        f.write(json.dumps(results))
    lap_time()
    pass


def generate_word_frequency_json():
    stored_names = generate_stored_twirp_list()
    results = {}

    tbl = dict.fromkeys(i for i in xrange(sys.maxunicode)
                      if unicodedata.category(unichr(i)).startswith('P'))
    
    for name, user_id in stored_names:
        print name
        results[name] = {}
        tweet_list = select_tweets_by_twirp(user_id)

        for tweet_record in tweet_list:
            if tweet_record[5]=='NULL' or tweet_record[5]=='REPLY':
                words = tweet_record[4].translate(tbl)
                words = words.lower().split()
                for word in words:
                    if word in results[name].keys():
                        results[name][word] +=1
                    else:
                        results[name][word] = 1
    
    with open('word_freq.json', 'w+') as f:
        f.write(json.dumps(results))
    lap_time()
    pass

def generate_mention_frequency_json():
    stored_names = generate_stored_twirp_list()
    results = {}

    for name, user_id in stored_names:
        print name
        results[name] = {}
        tweet_list = select_entities_by_twirp(user_id, 'mention')

        for mention in tweet_list:
            if mention[3] in results[name].keys():
                results[name][mention[3]] +=1
            else:
                results[name][mention[3]] =1

    with open('mention_freq.json', 'w+') as f:
        f.write(json.dumps(results))
    lap_time()
    pass




def generate_stored_twirp_list():
    with sqlite3.connect('twirpy.db') as connection:
        cur = connection.cursor()
        cur.execute('SELECT DISTINCT Userhandle, UserID FROM TweetData')
        twirp_list = cur.fetchall()
        return twirp_list

def select_tweets_by_twirp(user_id):
    with sqlite3.connect('twirpy.db') as connection:
        cur = connection.cursor()
        cur.execute('SELECT * FROM TweetData WHERE UserID=?', (user_id,))
        return cur.fetchall()

def select_entities_by_twirp(user_id, entity):
    with sqlite3.connect('twirpy.db') as connection:
        cur = connection.cursor()
        cur.execute('SELECT * FROM TweetEntities WHERE UserID=? AND EntityType=?', (user_id,entity))
        return cur.fetchall()


def tally_retweets():
    pass

def tally_favourites():
    pass

def monitor_twirps():
    with sqlite3.connect('twirpy.db') as connection:
        cur = connection.cursor()
        cur.execute('SELECT COUNT(DISTINCT UserHandle) FROM TweetData')
        mp_no = cur.fetchall()
        print mp_no[0][0]
        
        name_list = generate_stored_twirp_list()

        for name, _  in name_list:

            cur.execute('SELECT COUNT(*) FROM TweetData WHERE UserHandle=?', (name,))
            tally = cur.fetchall()

            cur.execute('SELECT TweetCount FROM TwirpData WHERE Handle=?', (name,))
            tweet_count = cur.fetchall()

            print name, '\t', tally[0][0], '\t', tweet_count[0][0]

def lap_time():
    lap = time.time()
    print '---%s s ---' %(START_TIME-lap)

def main():
    words = sys.argv
    if len(words) ==1:
        print 'print arg: [monitor, map]'
    elif words[1]=='monitor':
        monitor_twirps()
    elif words[1]=='map':
        generate_map()
    elif words[1]=='twirp_list':
        generate_stored_twirp_list()
    elif words[1]=='word_freq':
        generate_word_frequency_json()
    elif words[1]=='hashtag':
        generate_hashtag_frequency_json()
    elif words[1]=='mention':
        generate_mention_frequency_json()
    elif words[1]=='top_10':
        return_top_10()
    else:
        print 'bad arguments'
    


if __name__=='__main__':
    main()