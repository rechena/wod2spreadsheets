#!/usr/bin/python
from datetime import datetime, timedelta
import tweepy
import csv, re
import pandas as pd
import gspread
import argparse

parser = argparse.ArgumentParser(
    description=__doc__)

parser.add_argument('-s', '--spreadsheet', help='Pass the spreadsheet as a option (If the spreadsheet has spaces in the name pass it with "" (e.g.: "this is a test")')
parser.add_argument('-w', '--worksheet', help='Pass the sheet as a option. (If the spreadsheet has spaces in the name pass it with "" (e.g.: "this is a test")')
parser.add_argument('-d', '--days', help='In case we want to search back more than 1 day. If you use 0 as an argument it will search tweets for the current date (default is 1 day)',nargs='?', default=1, type=int)
parser.add_argument('--dryrun', help='Run in DryRun Mode - Do not update spreadsheets', action="store_true")
parser.add_argument('--version', action='version', version='%(prog)s 1.0')

args = parser.parse_args()

spreadsheet = args.spreadsheet
worksheet = args.worksheet
dryrun = args.dryrun
days = args.days

from oauth2client.service_account import ServiceAccountCredentials

#gdrive
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

#authfile for google drive
authfile = ('/PATH TO AUTH FILE/gdrive.json')
credentials = ServiceAccountCredentials.from_json_keyfile_name(authfile, scope)

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

# words to replace
words = ["#wodify", "Comment:"]

# twitter accounts to check for #wodify
listofaccounts = ["twitteraccount1", "twitteraccount2"]

# spreadsheet where the data will be pushed if not passed as a arg
if not spreadsheet:
	spreadsheet = "Wodify - Crossfit"

# date
onedayback = datetime.today() - timedelta(days=days)

formateddate = onedayback.strftime("%Y,%-m,%-d")

def main():
	global worksheet
	if dryrun:
		print "[INFO] Running in dryrun mode, no data will be updated or worksheets created at \"%s\" " % (spreadsheet)
		print "====================\n"
	try:
		for accounts in listofaccounts:
			for theaccount in api.user_timeline(screen_name = accounts, count = 10):
				if theaccount.created_at.strftime("%Y,%-m,%-d") == formateddate:
					if "#wodify" in theaccount.text:
						if not worksheet:
							#uses the first name of your twitter auther.name
							worksheet = theaccount.author.name.split()[0]
						try:
							wks = gc.open(spreadsheet).worksheet(worksheet)
						except gspread.exceptions.WorksheetNotFound:
							if not dryrun:
								print "[INFO] No worksheet with named %s exists. Creating..." % (worksheet)
								wks = gc.open(spreadsheet).add_worksheet(title=worksheet, rows="100", cols="20")
								wks = gc.open(spreadsheet).worksheet(worksheet)
								#Add Header row
								insertheader = ["Date","Exercise","Reps/Time","Weight","Comments"]
								wks.append_row(insertheader)	
						print "Tweet:", (theaccount.created_at, theaccount.author.name, theaccount.text)
						exercise = ' '.join(i for i in theaccount.text.split() if i not in words).split("|")
						if len(exercise) < 2:
							exercise.append(None)
						if "metcon" not in exercise[0].lower():
							splitexcercise = (re.split("[,@|:]+", exercise[0].rstrip()))
							if len(splitexcercise) < 3:
								splitexcercise.append(None)
							insertvalue = [theaccount.created_at.strftime("%Y/%m/%d"), splitexcercise[0],splitexcercise[1], splitexcercise[2], exercise[1]]
							print "Columns:", insertvalue
							if not dryrun:
								wks.append_row(insertvalue)
						else:
							splitexcercise = (re.split("[,@| ]+", exercise[0].rstrip()))
							if len(splitexcercise) < 2:
								splitexcercise.append(None)
							insertvalue = [theaccount.created_at.strftime("%Y/%m/%d"), splitexcercise[0].split(":")[0], splitexcercise[1], None, exercise[1]]
							print "Columns:", insertvalue
							if not dryrun:
								wks.append_row(insertvalue)
	except Exception as e:
		print e

if __name__ == "__main__":
    main()