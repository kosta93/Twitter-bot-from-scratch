import tweepy
from tweepy.streaming import StreamListener
from tweepy import Stream
import json
import pandas as pd


#Installation / Access to Twitter account
consumer_key = ''
consumer_secret = ''
access_token = ''
access_token_secret = ''

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit = True)

def profile_image(filename):
    api.update_profile_image(filename)

def update_profile_info(name, url, location, description):
    api.update_profile(name, url, location, description)

def post_tweet(text):
    api.update_status(text)

def upload_media(text, filename):
    media = api.media_upload(filename)
    api.update_status(text, media_ids = [media.media_id_string])

def favorite(tweet_id):
    api.create_favorite(str(tweet_id))

def retweet(tweet_id):
    api.retweet(str(tweet_id))

def unfavorite(tweet_id):
    api.destroy_favorite(str(tweet_id))

def unretweet(tweet_id):
    api.unretweet(str(tweet_id))

def reply(tweet_id, message):
    tweet = api.get_status(str(tweet_id))
    username = tweet.user.screen_name
    reply = api.update_status(f'@{username} ' + message, str(tweet_id))

#Scrape uesr timeline
    
def user_timeline(username):
    ot = [] #original tweet
    replies = []
    rts = []
    keyword_tweets = []
    kw_counter = 0
    tw_counter = 0
    for tweet in tweepy.Cursor(api.user_timeline, screen_name = username,
                               tweet_mode = 'extended').items(150):
        if 'tesla' in tweet.full_text.lower():
            kw_counter += 1
            tw_counter += 1
            keyword_tweets.append(tweet.full_text)
        else:
            tw_counter += 1
    print(kw_counter)
    print(tw_counter)
    return keyword_tweets
            
    '''
        if tweet.full_text.startswith('@'):
            replies.append(tweet.full_text)
        elif tweet.full_text.startswith('RT @'):
            rts.append(tweet.full_text)
        else:
            ot.append(tweet.full_text)
    print(len(ot))
    print(len(replies))
    print(len(rts))
    return ot, replies, rts
    '''
#keyword_tweets = user_timeline('elonmusk')
def search_tweets(keyword):
    for tweet in tweepy.Cursor(api.search, q = keyword,
                               tweet_mode = 'extended').items(10):
        if tweet.full_text.startswith('RT @'):
            text = tweet.retweeted_status.full_text
            print(len(text))
            print(text)
        else:
            print(len(tweet.full_text))
            print(tweet.full_text)


class Listener(StreamListener):
    def on_data(self, data):
        try:
            data = json.loads(data)
            tweet_id = data['id']
            tweet = api.get_status(id = tweet_id, tweet_mode = 'extended')
            if tweet.full_text.startswith('RT @'):
                text = tweet.retweeted_status.full_text
                print(text)
            else:
                print(tweet.full_text)
                
        except:
            print('Something went wrong!')


    def on_error(self, status):
        print(status)

class Streaming():
    def __init__(self, auth, listener):
        self.stream = tweepy.Stream(auth = auth,
                                    listener = listener)

    def start(self, keywords_list):
        self.stream.filter(track = keywords_list)

def start_streaming(keywords_list):
    if __name__ == '__main__':
        listener = Listener()
        stream = Streaming(auth, listener)
        stream.start(keywords_list)

def scrape_user_followers(username):
    followers_scraped = []
    user = api.get_user(username)
    for i, _id in enumerate(tweepy.Cursor(api.followers_ids,
                                          screen_name = username).items()):
        print(i, _id)
        followers_scraped.append(_id)
    return followers_scraped

def scrape_user_friends(username):
    friends_scraped = []
    user = api.get_user(username)
    for i, _id in enumerate(tweepy.Cursor(api.friends_ids,
                                          screen_name = username).items()):
        print(i, _id)
        friends_scraped.append(_id)
    return friends_scraped

def follow(screen_name):
    api.create_friendship(screen_name)

def unfollow(screen_name):
    api.destroy_friendship(screen_name)

'''
friends = scrape_user_friends('k_ristovski')
for i in range(len(friends)):
    screen_name = api.get_user(friends[i]).screen_name
    print(i, screen_name)
'''
def user_data(screen_name): #Screen_name and Twitter-profile ID
    user = api.get_user(screen_name)
    print(user.friends_count)
    print(user.followers_count)
    print(user.description)
    
def send_message(screen_name, text):
    profile_id = api.get_user(screen_name).id
    api.send_direct_message(str(profile_id), text = text)

def extract_messages(count):
    messages = []
    all_data = api.list_direct_messages(count = count)
    for i in range(len(all_data)):
        text = all_data[i]._json['message_create']['message_data']['text']
        messages.append(text)
    return messages        



def extract_trends(woeid, threshold):
    all_trends = api.trends_place(id = woeid)
    dataframe = pd.DataFrame(columns = ['Trend', 'Volume'], index = None)
    for i in range(len(all_trends[0]['trends'])):
        trend = all_trends[0]['trends'][i]['name']
        volume = all_trends[0]['trends'][i]['tweet_volume']
        try:
            if volume > threshold:
                new_row = {'Trend' : trend, 'Volume' : volume}
                dataframe = dataframe.append(new_row, ignore_index = True)
            else:
                pass
        except:
            pass
    dataframe = dataframe.set_index('Trend')
    dataframe = dataframe.sort_values(by = 'Volume', ascending = False)
    return dataframe
