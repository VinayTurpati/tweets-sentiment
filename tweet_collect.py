import config
import tweepy
import csv
from pathlib import Path
import TextBlob
path = Path(__file__).parent.absolute()

api_key = config.API_key
api_secret_key = config.API_secret_key

access_token = config.access_token
access_token_secret = config.access_token_secret

auth = tweepy.OAuthHandler(api_key, api_secret_key)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)

num_tweets = config.num_tweets
word = config.word

search_words = f"{word}"

if config.filter_retweets:
	search_words += "  -filter:retweets"

tweets = tweepy.Cursor(api.search,q=search_words,lang="en").items(num_tweets)
users_tweets = [[tweet.id_str, tweet.created_at, tweet.text, tweet.user.screen_name, tweet.user.location, tweet.favorite_count] for tweet in tweets]

with open(str(path) + f'/{word}_tweets.csv', 'w') as f:
	file = csv.writer(f)
	file.writerow(["id","created_at","text","user","location","likes"])
	file.writerows(users_tweets)


# def get_all_tweets(screen_name):
# 	# initialize a list to hold all the Tweets
# 	alltweets = []
# 	# make initial request for most recent tweets 
# 	# (200 is the maximum allowed count)

# 	new_tweets = api.user_timeline(screen_name = screen_name, count=100)
# 	# try:
# 	# 	new_tweets = api.user_timeline(screen_name = screen_name,count=100)
# 	# except tweepy.error.TweepError:
# 	# 	pass
	
# 	# save most recent tweets
# 	alltweets.extend(new_tweets)
# 	# save the id of the oldest tweet less one to avoid duplication
# 	oldest = alltweets[-1].id - 1
# 	# keep grabbing tweets until there are no tweets left
# 	while len(new_tweets) != 100:
# 		print("getting tweets before %s" % (oldest))
# 		# all subsequent requests use the max_id param to prevent
# 		# duplicates
# 		new_tweets = api.user_timeline(screen_name = screen_name,count=100,max_id=oldest)
# 		# save most recent tweets
# 		alltweets.extend(new_tweets)
# 		# update the id of the oldest tweet less one
# 		oldest = alltweets[-1].id - 1
# 		print("...%s tweets downloaded so far" % (len(alltweets)))
# 		### END OF WHILE LOOP ###
# 	# transform the tweepy tweets into a 2D array that will 
# 	# populate the csv
# 	outtweets = [[tweet.id_str, tweet.created_at, tweet.text, tweet.favorite_count,tweet.in_reply_to_screen_name, tweet.retweeted] for tweet in alltweets]
# 	# write the csv
# 	with open(str(path) + f'/{screen_name}_tweets.csv', 'w') as f:
# 		writer = csv.writer(f)
# 		writer.writerow(["id","created_at","text","likes","in reply to","retweeted"])
# 		writer.writerows(outtweets)
# 	pass
