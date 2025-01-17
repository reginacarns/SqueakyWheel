#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 18 15:51:29 2018

@author: rcarns
"""



def RetrieveTweets(searchQuery,storagefile,maxTweets=10000):
    # the below code draws from 
    # https://stackoverflow.com/questions/38555191/get-all-twitter-mentions-using-tweepy-for-users-with-millions-of-followers

    import tweepy
    import pandas as pd
    import numpy as np
    import pickle
    from connections import twitterapi
    api = twitterapi()
    
    tweetsPerQry = 100
    sinceId = None

    

    max_id = -1

    tweetCount = 0
    tweetProgress = 0
    #fName = 'tweetlist.txt'
    #with open(fName, 'w') as fname:
    list_of_tweets = []
    while tweetCount < maxTweets:
            try:
                if (max_id <= 0):
                    if (not sinceId):
                        new_tweets = api.search(q=searchQuery, count=tweetsPerQry, tweet_mode='extended')
                    else:
                        new_tweets = api.search(q=searchQuery, count=tweetsPerQry,
                                                since_id=sinceId)
                else:
                    if (not sinceId):
                        new_tweets = api.search(q=searchQuery, count=tweetsPerQry,
                                                max_id=str(max_id - 1),tweet_mode='extended')
                    else:
                        new_tweets = api.search(q=searchQuery, count=tweetsPerQry,
                                                max_id=str(max_id - 1),
                                                since_id=sinceId)
                if not new_tweets:
                    print("No more tweets found")
                    break
                for tweet in new_tweets:
                    #print(tweet.created_at.strftime('%x %X')+' '+tweet.full_text)
                    list_of_tweets.append(tweet._json)
                tweetCount += len(new_tweets)
                if tweetCount//1000>tweetProgress:
                    print("Downloaded {0} tweets".format(tweetCount))
                    tweetProgress+=1
                max_id = new_tweets[-1].id
            except tweepy.TweepError as e:
                # Just exit if any error
                print("some error : " + str(e))
                break

    picklefile = open(storagefile,'wb')
    pickle.dump(list_of_tweets,picklefile)
    picklefile.close()
    return tweetCount

def GetTestSet(atuser,maxtweets):
    import pickle
    import pandas as pd
    #maxtweets = 250
    if not atuser[0]=='@':
        username = atuser
        atuser = '@'+ atuser
    elif atuser[0]=='@':
        username = atuser[1:]
    import time
    retweet_filter='-filter:retweets'
    reply_filter = '-filter:replies'
    searchQuery = atuser+' AND '+retweet_filter+' AND '+reply_filter# + 'AND until:2018-09-11'
    print(searchQuery)
    #storagefile = type+'tweets'+time.strftime("%Y%m%d-%H%M%S")+'.dat'
    storagefile = 'testtweetfile.dat'
    tweetCount = RetrieveTweets(searchQuery,storagefile,maxtweets)
    maxtweets = tweetCount
    #import shutil
    #shutil.copy(storagefile,type+'tweets.dat')
    
    testpickle = open('testtweetfile.dat','rb')
    testtweets = pickle.load(testpickle)
    testpickle.close()
    testfilename = username+'test_tweets.csv'
    columns=['text','mentions','choose_one','class_label']
    testframe = pd.DataFrame(columns=columns,index=range(len(testtweets)))
    i = 0
    
    for tweet in testtweets:
        tweettext = tweet['full_text']
        testframe.at[i,'text']=tweettext
        testframe.at[i,'mentions'] = tweet['entities']['user_mentions']
        testframe.at[i,'choose_one']=''
        testframe.at[i,'class_label']=2
        i+=1
    
    testframe.to_csv(testfilename)
    return testfilename