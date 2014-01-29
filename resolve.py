#!/usr/bin/env python

#                   Lyratic Resolution: Silvertongue Edition
#                               Lyra's Jordan
#                      A blog engine by Duncan McNicholl
#                                  CC-BY-NC

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
import shutil
from scss import Scss

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
    try:
        article['tags'] = list(str(md.Meta['tags'][0]).split(', '))
        article['taglist'] = ({'tag':id} for id in article['tags'])
    except KeyError:
        pass
    return article
	
def draft_status(article):
#determine if article is post-dated
    return article['datestamp'] <= dt.today()

def sort_and_filter(articleList):
#sorts articles chronologically and filters out post-dated articles
    articleList.sort(key=lambda k: k['datestamp'], reverse=True)
    articleListForPublishing = filter(draft_status,articleList)
    return articleListForPublishing

def build_page(articles,templateName,inputFolder,outputFolder,fileName):
#turn a dictionary into a webpage
    template = read_file(templateName,inputFolder)
    data = {'updated':dt.isoformat(dt.now())+'Z',
            'tag':fileName[:-5],'articles':articles}
    html = pystache.render(template,data)
    filePath = os.path.join(outputFolder,fileName)
    codecs.open(filePath,'w','utf8').write(html)

def list_tags(articles):
#list all tags used
    tagList = []
    for article in articles:
        try:
            tags = article['tags']
            for tag in tags:
                if tag not in tagList:
                    tagList.append(tag)
        except KeyError:
            pass
    return tagList

def selectArticles(tag,articles):
#select articles with given tag
    editedList = []
    for article in articles:
        try:
            if tag in article['tags']:
                editedList.append(article)
        except KeyError:
            pass
    return editedList

def build_site(parameters):
#build the relevant pages
    draftList = []
    pm = parameters
    fileList = os.listdir(pm['input'])
    for file in fileList:
        if file.endswith('.md'):
            article = parse_file(file,pm['input'])
            draftList.append(article)
        elif file.endswith('.scss'):
            scss = read_file(file,pm['input'])
            compiler = Scss()
            css = compiler.compile(scss)
            filePath = os.path.join(pm['output'],file[:-5]+'.css')
            codecs.open(filePath,'w','utf8').write(css)
        elif file.endswith('.stache'):
            pass
        else:
            shutil.copy2(os.path.join(inputFolder,file),
                         os.path.join(outputFolder,'static',file))
    articleList = sort_and_filter(draftList)
    tagList = list_tags(articleList)
    build_page(articleList[:pm['homeLength']],'index.stache',
               pm['input'],pm['output'],'index.html')
    build_page(articleList[:pm['feedLength']],'feed.stache',
               pm['input'],pm['output'],'feed.xml')
    build_page(articleList,'archive.stache',
               pm['input'],pm['output'],'archive.html')
    for page in articleList:
        build_page(page,'page.stache',pm['input'],
                   pm['output'],page['slug'])
    for tag in tagList:
        editedList = selectArticles(tag,articleList)
        build_page(editedList,'tag.stache',
                   pm['input'],pm['output'],tag+'.html')
    print tagList

build_site(DieM)