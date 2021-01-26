#Writen by Curtis Harris for notnullisland.com

import requests
import pandas as pd
from datetime import datetime, timedelta

#Define Viz of the Day endpoint
#Notice we are only pulling the most recent 12 (see count=12) vizzes of the day, which is absolutely fine for this use case
url = 'https://public.tableau.com/api/gallery?page=0&count=12&galleryType=viz-of-the-day&language=en-us'
print('Viz of the Day URL set...')


#Request data from Viz of the Day endpoint
r = requests.get(url)
print('Viz of the Day data retrieved...')


#Transform the response text into JSON
j = r.json() 
print('Viz of the Day data converted to JSON...')


#Create a dataframe restricted to the metadata realted to vizzes of the day
#The endpoint contains additional elements that we don't need for this use case
df = pd.DataFrame(j['items'])
print('Viz of the Day data converted to dataframe...')


#Restrict the dataframe to the first row... the last viz of the day
df = df.iloc[0]
print('Most recent Viz of the Day selected...')


#Gallery publication date converted to timestamp
df['galleryItemPublicationDate'] = pd.to_datetime(df['galleryItemPublicationDate'],unit='ms')


#Get time one day ago
yesterday = datetime.now() - timedelta(days=1)


#Convert to start of yesterday
yesterday_begin = yesterday.replace(hour=0, minute=0, second=0, microsecond=000000)


#Convert to end of yesterday
yesterday_end = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)


#Check to see if most recent Viz of the Day is from yesterday
df['date_check'] = (df['galleryItemPublicationDate'] > yesterday_begin) & (df['galleryItemPublicationDate'] < yesterday_end)


#The rest is a very crude way to formulate the appropriate JSON to send in the body of your Slack POST
#The following lines are taking specific values from the viz of the day data, and creating specific strings to embedd in our JSON
#Store field from dataframe as a variable
#Replace the {} with desired variable
author_name = df['authorName']
author_name = '"author_name": "{}",'.format(author_name)


author_link = df['authorUrl']
author_link = '"author_link": "{}",'.format(author_link)


title = df['title']
title = '"title": "{}",'.format(title)


title_link = df['sourceUrl']
title_link = '"title_link": "{}",'.format(title_link)


image_url = df['screenshot']
image_url = '"image_url": "{}",'.format(image_url)
print('Requisite fields converted to strings for JSON...')


#There is definitely a better way to do this out there, but I'm a rookie, and I just couldn't find it
#The following is a convulated way to create a very long string, that is in fact, valid JSON
payload = '{' \
'"attachments": [' \
'{' \
'"fallback": "Required plain-text summary of the attachment.",' \
'"color": "#E80A89",' \
'"pretext": "Tableau Viz of the Day",' \
+author_name \
+author_link \
+title \
+title_link \
+image_url \
+'"footer": "Provided by Data Insights and Analytics",' \
'"footer_icon": "https://cdn4.iconfinder.com/data/icons/logos-brands-5/24/pluralsight-512.png"' \
'}' \
']' \
'}'
print('Slack JSON created...')


#If most recent Viz of the Day is from yesterday, use payload defined above, else use empty JSON
payload = payload if df['date_check'] else '{}'


#Your Slack webhook from your custom integration
webhook = 'paste your webhook URL here'
print('Slack webhook set...')


#Send the payload to Slack and post the message
requests.post(webhook, payload)
print('Viz of the Day posted to Slack!')