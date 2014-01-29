#!/usr/bin/env python
#
#     Lyratic Resolution: Silvertongue Edition
#             The Decanter of Tokay
#        A blog engine by Duncan McNicholl
#                   CC-BY-NC
#
#start with blog parameters

DieM = {'input':'/path/to/input/files',
        'output':'/path/to/output/files',
        'feedLength':12,
        'homeLength':6}

#import necessary modules
import markdown
from datetime import datetime as dt
import string
import codecs
import os
import pystache

def read_file(fileName, directory):
#read contents of file into unicode string
    filePath = os.path.join(directory,fileName)
    fileContents = codecs.open(filePath,'r','utf8').read()
    return unicode(fileContents)

def parse_file(fileName,directory):
#read contents of file into dictionary
    post = read_file(fileName,directory)
    md = markdown.Markdown(extensions = ['meta'])
    md.convert(post)
    article = {'title' : md.Meta['title'][0],
               'abstract' : md.Meta['abstract'][0],
               'body' : md.convert(post),
               'datestamp' : dt.strptime(md.Meta['date'][0],'%Y-%m-%d')}
    article['date'] = article['datestamp'].strftime('%A, %d %B \'%y')
    article['updated'] = article['datestamp'].isoformat()+'Z'
    lowerTitle = str(article['title']).lower().translate(None,string.punctuation)
    article['slug'] = '-'.join(lowerTitle.split())+'.html'
    return article
	
def draft_status(article):
#determine if article is post-dated
    return article['datestamp'] <= dt.today()

def make_list(inputFolder):
#produce list of dictionaries from directory
    articleList = []
    fileList = os.listdir(inputFolder)
    for file in fileList:
        if file.endswith('.md'):
            article = parse_file(file,inputFolder)
            articleList.append(article)
    articleList.sort(key=lambda k: k['datestamp'], reverse=True)
    articleListForPublishing = filter(draft_status,articleList)
    return articleListForPublishing

def build_page(articles,templateName,inputFolder,outputFolder):
#turn a dictionary into a webpage
    template = read_file(templateName,inputFolder)
    data = {'updated':dt.isoformat(dt.now())+'Z','articles':articles}
    html = pystache.render(template,data)
    if templateName == 'page.stache':
        fileName = articles['slug']
    elif templateName == 'feed.stache':
        fileName = templateName[:-7]+'.xml'
    else:
        fileName = templateName[:-7]+'.html'
    filePath = os.path.join(outputFolder,fileName)
    codecs.open(filePath,'w','utf8').write(html)

def build_site(parameters):
#build the relevant pages
    articleList = make_list(parameters['input'])
    pm = parameters
    build_page(articleList[:pm['homeLength']],'index.stache',
               pm['input'],pm['output'])
    build_page(articleList[:pm['feedLength']],'feed.stache',
               pm['input'],pm['output'])
    build_page(articleList,'archive.stache',
               pm['input'],pm['output'])
    for page in articleList:
        build_page(page,'page.stache',pm['input'],pm['output'])

build_site(DieM)