#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib2
import urllib
import json
import time
import os

#rootPath = os.getcwd() + "/wikiWomensStats/"

#dataPath = rootPath + 'data.json'

fullDataPath = 'data.json'

headers = { 'User-Agent' : 'Womens edit a thon India' }

cmtitle = "பகுப்பு:2015 பெண்கள் வரலாற்று மாதத்தில் உருவாக்கிய அல்லது மேம்படுத்திய கட்டுரைகள்"
apiUrl = 'https://ta.wikipedia.org/w/api.php'

eventStartTimestamp = 20150301000000

categoryData =  {
                  'action' : 'query',
                  'list' : 'categorymembers',
                  'cmtitle' : '',
                  'cmcontinue' : '',
                  'format' : 'json'
                  }

def getArticleList(cmtitle):
    articleList = []
    while True:
        categoryData['cmtitle'] = cmtitle
        req = urllib2.Request(apiUrl, headers=headers, data = urllib.urlencode(categoryData))
        response = json.loads(urllib2.urlopen(req).read())

        for article in response['query']['categorymembers']:
            articleList.append(article)
        if 'query-continue' not in response:
            break;
        categoryData['cmcontinue'] = response['query-continue']['categorymembers']['cmcontinue']
    return articleList

def getEdits(title,pageId):
    articleData =   {
                   'action' : 'query',
                   'prop' : 'revisions',
                   'format' : 'json',
                   'rvprop' : 'timestamp|user|comment',
                   'rvstart' : eventStartTimestamp,
                   'rvdir' : 'newer',
                   'titles' : ''
                   }
    edits = []
    while True:
        articleData['titles'] = title.split(':')[-1].encode('utf-8')
        print articleData['titles']
        req = urllib2.Request(apiUrl, headers=headers, data = urllib.urlencode(articleData))
        response = json.loads(urllib2.urlopen(req).read())
        pageId = response['query']['pages'].keys()[0]
        print pageId
        print response['query']['pages'][pageId]

        if response['query']['pages'][pageId].get("revisions"):
	  for edit in response['query']['pages'][pageId].get("revisions"):
            edits.append(edit)
            pass
        if 'query-continue' not in response:
            break;
        articleData['rvcontinue'] = response['query-continue']['revisions']['rvcontinue']
    return edits

def createInfoParams(article):
    infoData['title'] = article
    return urllib.urlencode(infoData)

def getCount():
    counts = {}
    articles = {}
    participants = {}
    anon = {}
    articleList = getArticleList(cmtitle)
    for article in articleList:
        articleTitle = article['title'].split(':')[-1].replace(' ','_')
        articleId = article['pageid']
        edits = getEdits(articleTitle,str(articleId))
        editCount = len(edits)

        for edit in edits:
            if 'anon' not in edit:
                user = edit['user'].replace(' ','_')
                if not ('bot' in user or 'Bot' in user):
                    if user in participants:
                        participants[user] += 1
                    else:
                        participants[user] = 1
            else:
                if edit['user'] in anon:
                        anon[edit['user']] += 1
                else:
                    anon[edit['user']] = 1
        articles[articleTitle] = editCount

    counts['articles'] = articles
    counts['participants'] = participants
    counts['anon'] = anon
    return counts

def writeJson():
    temp = getCount()
    with open(fullDataPath,'a') as f:
        temp['timestamp'] = time.time()
        f.write(json.dumps(temp)+'\n')
    f.close()

def readJson():
    pointer = -2
    with open(fullDataPath,'r') as f:
        while f.read(1) != '\n':
            f.seek(pointer,2)
            pointer -= 1
        latest = f.readline()
    f.close()
    return json.loads(latest)

if __name__ == "__main__":
    writeJson()

