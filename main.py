# from flask_paginate import Pagination, get_page_parameter, get_page_args
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
	return users_tweets 

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

app = Flask(__name__)

def csv_json(path):
	with open(path) as f:
		a = [{k: v for k, v in row.items()} for row in csv.DictReader(f, skipinitialspace=True)]
	return a

@app.route("/")
@app.route("/home")
def home():
	number_of_rows = all_rows()
	return render_template('index.html', request= request, total_searches = number_of_rows)

@app.route('/search',methods = ['GET','POST'])
def search():
	num_tweets = int(request.args.get('tweets', default = '100'))
	key_word = request.args.get('word')
	insert(key_word)
	all_tweets = collect_tweets(num_tweets, key_word)

	number_of_rows = all_rows()
	tweet_polarity = []
	tweets = pd.DataFrame(all_tweets)['text']
	for tweet in tweets:
		tweet_polarity.append(TextBlob(tweet).sentiment.polarity)

	df = pd.DataFrame(all_tweets)
	df['polarity'] = pd.Series(tweet_polarity).apply(limit)

	df['get_analysis'] = df['polarity'].apply(get_analysis).values
	df['color'] = df['polarity'].apply(tweet_color).values
	sentiment = {'positive':int(sum(df['get_analysis'] == 'Positive' )*100/len(tweets)), 'negative':int(sum(df['get_analysis'] == 'Negative')*100/len(tweets)), 'neutral':int(sum(df['get_analysis'] == 'Neutral')*100/len(tweets))}

	return render_template('search.html', tweets = all_tweets, df = df, word = key_word, colors = colors, length = len(all_tweets), sentiment = sentiment, total_searches = number_of_rows)
if __name__ == '__main__':
	# Threaded option to enable multiple instances for multiple user access support
	app.run(debug = True,threaded=True, port=2000)
