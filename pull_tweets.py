import tweepy
import time
from datetime import date
import pandas as pd
import argparse
import tweeter_auth as ta

SEARCH_QUERY = 'eczema'


def get_place_info(place):
    '''
    Args: 
        place (place)

    Returns:
        tuple of place name, place country, and place bounding box coordinate list
    '''
    if place is not None:
        place_name = place.full_name
        place_country = place.country_code
        place_box = place.bounding_box.coordinates
        return (place_name, place_country, place_box)
    else: 
        return (None, None, None)

def get_tweets(search_query, out_dir):
    '''
    Generate csv file containing tweet information with search query

    Args:
        search_query (str)
    '''
    auth = tweepy.OAuthHandler(ta.consumer_key, ta.consumer_secret)
    auth.set_access_token(ta.access_token, ta.access_token_secret)

    api = tweepy.API(auth, wait_on_rate_limit=True)

    count = 0
    d = {}
    for page in tweepy.Cursor(api.search, q=SEARCH_QUERY, lan='en', tweet_mode='extended', rpp=100).pages():
        count +=1
        # wait 1 min after going through 50 pages
        if count % 50 == 0:
            print(count)
            time.sleep(60)
        for tweet in page:
            tweet_id = tweet.id_str
            place = tweet.place
            place_name, place_country, place_box = get_place_info(place)
            d[tweet_id] = {'tweet_time': tweet.created_at,
                           'coords': tweet.coordinates,
                           'place_name': place_name,
                           'place_country': place_country,
                           'place_box': place_box,
                           'user_id': tweet.user.id_str,
                           'tweeter_loc': tweet.user.location,
                           'has_geo': tweet.user.geo_enabled,
                           'content': tweet.full_text}

    df = pd.DataFrame.from_dict(d).T
    date_str = str(date.today())
    df.to_csv(out_dir+'{}_eczema_tweets.txt'.format(date_str), sep='\t', index=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get tweets')
    parser.add_argument('-s', '--search_query', required=False, default=SEARCH_QUERY, type=str)
    parser.add_argument('-o', '--out_dir', required=False, default='./', type=str)

    args = parser.parse_args()
    get_tweets(args.search_query, args.out_dir)