#!/usr/bin/python
from datetime import datetime, timedelta
import tweepy
import csv, re
import pandas as pd
import gspread

from oauth2client.service_account import ServiceAccountCredentials

#gdrive
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name('gdrive.json', scope)

gc = gspread.authorize(credentials)


# Twitter auth - Consumer keys and access tokens, used for OAuth  
consumer_key = '<add consumer_key>'  
consumer_secret = '<add consumer_secret>'  
access_token = '<add access_token>'  
access_token_secret = '<add access_token_secret'
  
# OAuth process, using the keys and tokens  
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)  
auth.set_access_token(access_token, access_token_secret)  
api = tweepy.API(auth,wait_on_rate_limit=True)

#words to replace
words = ["#wodify", "Comment:"]

#accounts to look for tweets
listofaccounts = ["twitteraccount1", "twitteraccount2"]

#spreadsheet where the data will be pushed
spreadsheet = "Wodify - Crossfit"

#date
days_to_subtract = 1
onedayback = datetime.today() - timedelta(days=days_to_subtract)

formateddate = onedayback.strftime("%Y,%-m,%-d")

for accounts in listofaccounts:
	for theaccount in api.user_timeline(screen_name = accounts, count = 10):
		worksheet = theaccount.author.name.split()[0]
		wks = gc.open(spreadsheet).worksheet(worksheet)
		if theaccount.created_at.strftime("%Y,%-m,%-d") == formateddate:
			if "#wodify" in theaccount.text:
				print "Tweet:", (theaccount.created_at, theaccount.author.name, theaccount.text)
				exercise = ' '.join(i for i in theaccount.text.split() if i not in words).split("|")
				if len(exercise) < 2:
					exercise.append(None)
				if "metcon" not in exercise[0].lower():
					splitexcercise = (re.split("[,@|:]+", exercise[0]))
					insertvalue = [theaccount.created_at.strftime("%Y/%m/%d"), splitexcercise[0],splitexcercise[1], splitexcercise[2], exercise[1]]
					print "Columns:", insertvalue
					wks.append_row(insertvalue)
				else:
					splitexcercise = (re.split("[,@| ]+", exercise[0].rstrip()))
					insertvalue = [theaccount.created_at.strftime("%Y/%m/%d"), splitexcercise[0].split(":")[0], splitexcercise[1], None, exercise[1]]
					print "Columns:", insertvalue
					wks.append_row(insertvalue)