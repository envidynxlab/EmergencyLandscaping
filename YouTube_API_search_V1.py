# -*- coding: utf-8 -*-
"""
Created on Thu Nov  4 11:39:05 2021

@author: dt1n19
"""
####### Intro - using YouTube API to explore Emergency Landscaping ############

# author Dominique Townsend

# This script uses the Youtube API to carry out a systematic review of videos
# which show 'Emergency Landscaping' being carried out in coastal environments.

# User must have following modules installed to environment: 
#       google-api-python-client
#       pandas

# Must update working directory (section 2.), search term (section 3.) 
# and create user's own auth.py file before running.

# V1. 01/12/2021

########################### 1. import modules #################################

import json
import pandas as pd
from googleapiclient.discovery import build
import csv # for saving results (i.e. response_json) to csv file
import os 
import glob
from auth import api_key

######################### 2. set working directory ############################

# Set a blank folder for your working folder

os.chdir("C:/Users/dt1n19/Documents/Python/EmergencyLandscaping") 

# Set the location of where you would like the search results to be saved

YT_results_save_loc = "C:/Users/dt1n19/Documents/Python/EmergencyLandscaping/Results_20211201/"

######################## 3. set search term ###################################

search_term = 'coast*+*dozer*'

######################## 4. making our request to youtube #####################

youtube = build('youtube','v3',developerKey=api_key)

request = youtube.search().list(q= search_term, part='snippet', maxResults=50) # this is the first time the request is made

##################### 5. request returned is a dictionary #####################

response_dict =request.execute()
#print(type(response_dict))
#print(response_dict)

###################### 6.what is the next page token ##########################

pageKey = response_dict["nextPageToken"]

###################### 7.request from dictionary to json ######################

response_json = json.dumps(response_dict)
#print(response_json)

file = open("YT_json.txt", "w")
file.write(response_json) # creates json file
file.close()

################################ 8. json to csv ###############################
####################### 8a.  def get leaves function ##########################

def get_leaves(item, key=None):
    if isinstance(item, dict):
        leaves = {}
        for i in item.keys():
            leaves.update(get_leaves(item[i], i))
        return leaves
    elif isinstance(item, list):
        leaves = {}
        for i in item:
            leaves.update(get_leaves(i, key))
        return leaves
    else:
        return {key : item}

################################ 8. json to csv ###############################
########################### 8b. run leaves function ###########################

with open('YT_json.txt') as f_input:
    json_data = json.load(f_input)['items']

# First parse all entries to get the complete fieldname list
fieldnames = set()

for entry in json_data:
    fieldnames.update(get_leaves(entry).keys())

with open('YT_search.csv', 'w', encoding='utf-8-sig', newline='') as f_output:
    csv_output = csv.DictWriter(f_output, fieldnames=sorted(fieldnames))
    csv_output.writeheader()
    csv_output.writerows(get_leaves(entry) for entry in json_data)
#file.write(json.dumps(response))

####################### 9. repeat for ten pages ###############################

for requests in range(1,10):
    if pageKey:     
        request = youtube.search().list(q=search_term, part='snippet',pageToken= pageKey, maxResults=50) # this is the first time the request is made
        response_dict =request.execute()
        # update the page key for the next page
        pageKey = response_dict["nextPageToken"]
            ### request from dictionary to json
        response_json = json.dumps(response_dict)
        file = open("YT_json_%s.txt" % requests, "w")
        file.write(response_json) # creates json file
        file.close()
        ### json to csv
        ### run leaves function
        with open("YT_json_%s.txt" % requests) as f_input:
            json_data = json.load(f_input)['items']
    
        # First parse all entries to get the complete fieldname list
        fieldnames = set()
    
        for entry in json_data:
            fieldnames.update(get_leaves(entry).keys())
    
        with open('YT_search_%s.csv' % requests, 'w', encoding='utf-8-sig', newline='') as f_output:
            csv_output = csv.DictWriter(f_output, fieldnames=sorted(fieldnames))
            csv_output.writeheader()
            csv_output.writerows(get_leaves(entry) for entry in json_data)
    else:
        continue
        
###################### 10. amalgamate csv files ###############################

#use glob to match pattern 'csv' 
extension = 'csv'
all_filenames = [i for i in glob.glob('*.{}'.format(extension))]

#combine all files in the list
combined_csv = pd.concat([pd.read_csv(f, encoding='ISO-8859-1') for f in all_filenames ])

#export to csv
combined_csv.to_csv( "combined_csv.csv", index=False, encoding='utf-8-sig')

################### 11. Add link to video and reorder csv #####################

df = pd.read_csv('combined_csv.csv')
df ["Link"] = "https://www.youtube.com/watch?v=" + df['videoId']
df_reorder = df[['publishTime', 'title', 'description', 'Link', 'channelTitle']] # rearrange column here

############################## 12. Save result ################################
#remove special characters from search term
save_search_term = search_term
special_char = "*"
for char in special_char:
    save_search_term = save_search_term.replace(char, "")
#print(save_search_term)

save_results = YT_results_save_loc + 'YT_' + save_search_term
print(save_results)
df_reorder.to_csv('%s.csv' % save_results, index=False)

############################### References ####################################

# Youtube API documentation: https://developers.google.com/youtube/v3/docs/search/list 
# Nested json to csv: https://stackoverflow.com/questions/56451585/jsontocsv-with-python-nested-json/56451619#56451619 
# Amalgamating csvs: https://www.freecodecamp.org/news/how-to-combine-multiple-csv-files-with-8-lines-of-code-265183e0854/


