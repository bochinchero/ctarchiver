import requests
import json
import markdownify
import os
import re
from pywebcopy import save_webpage

def readLocalSecrets():
    # this function reads the local files for API key and url
    # intended to be used when there is no connectionDict specified in the request functions
    # if any of the files is not found a blank dict will be returned.
    try:
        output = {'url': open('./sURL', 'r').readline(), 'key': open('./sKey', 'r').readline()}
    except:
        print('readLocalSecrets: Error loading url/key files')
        output = {'url':'','key':''}
    return output


def requester(url,endpoint,key=None,otherParams=None):
    # generic requests function, will retry 10 times
    attempts = 10
    for attempt in range(attempts):
        try:
            targetUrl = url + endpoint
            if key is not None:
                targetUrl += '?key=' + key
            if otherParams is not None:
                targetUrl += otherParams
            response = requests.get(targetUrl)
            response.json()
        except requests.exceptions.Timeout:
            print('requester: timeout on '+endpoint)
        except requests.exceptions.TooManyRedirects:
            print('requester: too many retries on '+endpoint)
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)
        else:
            return response.json()
    else:
        print('requester: failed after '+str(attempts)+' attempts.')


def getPosts(secrets=None):
    # this function gets all the posts and combines them into a single dictionary
    if secrets is None:
        # if the connection data is not provided into the function it will be grabbed from local files
        secrets = readLocalSecrets()
    # grab the first page
    outputDict = requester(secrets['url'],'posts/',secrets['key'],'&include=tags,authors')
    # create a posts dictionary
    postsDict = outputDict.get('posts')
    # get the number of pages to iterate
    numPages = outputDict.get('meta').get('pagination').get('pages')
    for i in range(2,numPages):
        # iterate through all the pages in the api endpoint to get all posts
        otherParams = '&page=' + str(i) + '&include=tags,authors'
        outputDict = requester(secrets['url'], 'posts/', secrets['key'], otherParams)
        # add them to the postsDict
        postsDict.append(outputDict.get('posts'))
    # return postsDict
    return postsDict


def postParser(post,archivePath):
    # this function is meant to be executed to recreate a
    pDate = post.get('published_at').split("T",1)[0]
    slug = post.get('slug')
    # this function parses the post data
    data = post.get('html')
    title = post.get('title')
    excerpt = post.get('custom_excerpt')
    feature_image = post.get('feature_image')
    path = archivePath + pDate + '-' + slug + '/'
    # adds feature image, title, excerpt to the html data
    if excerpt is not None:
        data = '<h3>'+excerpt+'</h3><br>'+post.get('html')
    if feature_image is not None:
        data = '<img src="' + feature_image + '"\><br>' + data
    if title is not None:
        data = '<h1>'+title+'</h1><br>'+data
    post.pop('html', None)
    # prettify json to get the metadata into an exportable format
    metadata = json.dumps(post, indent=6)
    # convert HTML into markdown
    mdText = markdownify.markdownify(data)
    # write to file
    writeToFile(path,'post.html',data)
    writeToFile(path,'post.md',mdText)
    writeToFile(path,'metadata.json',metadata)
    # copy web page info
    return


def writeToFile(path,file,text):
    # function for writing files/folders
    try:
        if not os.path.exists(path):
            os.makedirs(path)
        fileName = path + file
        # remove file if it exists
        if os.path.isfile(fileName):
            os.remove(fileName)
        # write files
        with open(fileName, 'w+') as file:
            file.write(text)
    except:
        print('Error writing the file '+path + file )
