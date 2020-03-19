from flask_paginate import Pagination, get_page_parameter, get_page_args
from flask import Flask, render_template, request
# from alchemy import db, Post, app, mail
# from flask_mail import Message
from datetime import date
# import mysql.connector
import datetime
import csv
# from ml_processor import predictor
import pandas as pd
import math
import config
import tweepy
import csv
from textblob import TextBlob
from insert import insert
import MySQLdb

import pymysql
import mysql
pymysql.install_as_MySQLdb()

def all_rows():
	db = mysql.connector.connect(host="sql12.freemysqlhosting.net", 
		user="sql12324328", passwd="3cZf18ghZV", database = 'sql12324328')
	cursor= db.cursor()
	cursor.execute("SELECT * FROM tweets")
	number_of_rows = len(cursor.fetchall())
	cursor.close()
	return number_of_rows

def get_tweets(tweets_p, offset=0, per_page=5):
	return tweets_p[offset: offset + per_page]


def limit(score):
	return float("{0:.2f}".format(score))

def get_analysis(score):
	if score < 0:
		return 'Negative'
	elif score == 0:
		return 'Neutral'
	else:
		return 'Positive'

api_key = config.API_key
api_secret_key = config.API_secret_key
access_token = config.access_token
access_token_secret = config.access_token_secret

auth = tweepy.OAuthHandler(api_key, api_secret_key)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)


def collect_tweets(num_tweets, word):
	search_words = "{}".format(word)
	if config.filter_retweets:
		search_words += "  -filter:retweets"
	tweets = tweepy.Cursor(api.search,q=search_words,lang="en").items(num_tweets)
	users_tweets = [{"id":tweet.id_str, "created_at":tweet.created_at, "text":tweet.text, "user":tweet.user.screen_name, "location":tweet.user.location, "likes":tweet.favorite_count, 'coordinates':tweet.coordinates} for tweet in tweets]

	return pd.DataFrame(users_tweets) 

colors = {-5:"#F64700", -4: "#FF8800",-3: "#FFAD59",-2: "#FFD19A",-1: "#FFEDDC",0: "#FFFFFF",1: "#EAFAE8",2: "#BEEDBD",3: "#90DF97",4: "#54CB70", 5:"#00B257"}

def tweet_color(score):
	score = score*10
	if score < 0:
		if score >-5:
			return colors[int(math.floor(score))]
		else:
			return colors[-5]
	elif score == 0:
		return colors[0]
	else:
		if score <5:
			return colors[int(math.ceil(score))]
		else:
			return colors[5]

def sentiment_text(text):
	return TextBlob(text).sentiment.polarity

app = Flask(__name__)

def csv_json(path):
	with open(path) as f:
		a = [{k: v for k, v in row.items()} for row in csv.DictReader(f, skipinitialspace=True)]
	return a

@app.route("/")
@app.route("/home")
def home():
	number_of_rows = 0#all_rows()
	key_word = ""
	num_tweets = 100
	return render_template('index.html', request= request, total_searches = number_of_rows, word = key_word, num_tweets = num_tweets)

@app.route('/search',methods = ['GET','POST'])
def search():
	if request.method == "POST":
		num_tweets = int(request.form.get('tweets'))#int(request.args.get('tweets', default = '100'))
		key_word = request.form.get('word')#request.args.get('word')
		#insert(key_word)

		df = collect_tweets(num_tweets, key_word)

		df['polarity'] = df['text'].apply(sentiment_text).apply(limit)
		df['get_analysis'] = df['polarity'].apply(get_analysis).values
		df['color'] = df['polarity'].apply(tweet_color).values

		positive = int(sum(df['get_analysis'] == 'Positive' )*100/len(df))
		negative = int(sum(df['get_analysis'] == 'Negative')*100/len(df))
		neutral  = int(sum(df['get_analysis'] == 'Neutral')*100/len(df))

		df.to_csv('data.tmp', index=False)
		with open("temp.tmp",'w') as f:
			f.seek(0)
			f.write('{}-+-{}-+-{}-+-{}-+-{}'.format(key_word,num_tweets,positive,negative,neutral))

	else:
		with open("temp.tmp",'r') as f:
			temp = f.read().split('-+-')
			key_word = temp[0]
			num_tweets = int(temp[1])
			positive = temp[2]
			negative = temp[3]
			neutral = temp[4]

	df = pd.read_csv("data.tmp")

	sentiment = {'positive':positive, 'negative':negative, 'neutral':neutral}
	number_of_rows = 0#all_rows()

	try:
		page = int(request.args.get('page'))
	except:
		page = 1

	per_page = 10
	offset = 0
	pagination_tweets = df[(page-1)*per_page:page*per_page].reset_index(drop=True)
	pagination = Pagination(page=page, per_page=per_page, total=len(df),css_framework='bootstrap4')
	print(pagination_tweets)
	return render_template('search.html', tweets = pagination_tweets, word = key_word, length = len(pagination_tweets), sentiment = sentiment, total_searches = number_of_rows, pagination = pagination, num_tweets = num_tweets)

if __name__ == '__main__':
	# Threaded option to enable multiple instances for multiple user access support
	app.run(debug = True,threaded=True, port=2000)
