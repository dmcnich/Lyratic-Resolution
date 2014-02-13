#!/usr/bin/env python

#                   Lyratic Resolution: Silvertongue Edition
#                              The Throwing Nets
#                       A blog engine by Duncan McNicholl
#                                   CC-BY-NC

#start with blog parameters
DieM = {'input':'/path/to/input',
        'output':'/path/to/output',
        'feedLength':12,
        'homeLength':6}

#import necessary modules
from datetime import datetime as dt
import string
import codecs
import os
import shutil
import markdown
import pystache
try:
  from scss import Scss
except ImportError:
  pass

def read_file(fileName, input):
#read contents of file into unicode string
  filePath = os.path.join(input,fileName)
  fileContents = codecs.open(filePath,'r','utf8').read()
  return unicode(fileContents)

def parse_article(fileName,input):
#read contents of file into dictionary
  try: #use smartypants if it's installed
    md = markdown.Markdown(extensions = ['meta','smartypants'])
  except ImportError:
    md = markdown.Markdown(extensions = ['meta'])
  post = read_file(fileName,input)
  article = {}
  article['body'] = md.convert(post)
  try: #try to get title from front matter
    article['title'] = md.Meta['title'][0]
  except KeyError: #use filename if not present
    article['title'] = fileName[:fileName.index('.')]
  try: #try to get date from front matter
    article['datestamp'] = dt.strptime(md.Meta['date'][0],'%Y-%m-%d')
  except KeyError: #use modified date if not present
    modifiedTime = os.path.getmtime(os.path.join(input,fileName))
    article['datestamp'] = dt.fromtimestamp(modifiedTime)
  try: #try to get abstract from front matter
    article['abstract'] = md.Meta['abstract'][0]
  except KeyError: #use first sentence if not present
    article['abstract'] = article['body'][:article['body'].index('.')]
  try: #try to get tags from front matter
    article['tags'] = list(str(md.Meta['tags'][0]).split(', '))
    article['taglist'] = ({'tag':id} for id in article['tags'])
  except KeyError:
    pass
  #then generate further useful attributes from metadata
  article['date'] = article['datestamp'].strftime('%A, %d %B \'%y')
  article['updated'] = article['datestamp'].isoformat()+'Z'
  lowerTitle = str(article['title']).lower().translate(None,string.punctuation)
  article['slug'] = '-'.join(lowerTitle.split())+'.html'
  article['wordcount'] = len(article['body'].split())+1
  article['readtime'] = str(int(article['wordcount']/200)+2)
  return article
	
def draft_status(article):
#determine if article is post-dated
  return article['datestamp'] <= dt.today()

def sort_and_filter(articleList):
#sorts articles chronologically and filters out post-dated articles
  articleList.sort(key=lambda k: k['datestamp'], reverse=True)
  articleListForPublishing = filter(draft_status,articleList)
  return articleListForPublishing

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

def select_articles(tag,articles):
#select articles with given tag
  editedList = []
  for article in articles:
    try:
      if tag in article['tags']:
        editedList.append(article)
    except KeyError:
      pass
  return editedList
    
def sassify(file,input,output):
#process scss file using Sass
  scss = read_file(file,input)
  compiler = Scss()
  css = compiler.compile(scss)
  filePath = os.path.join(output,file[:-4]+'css')
  codecs.open(filePath,'w','utf8').write(css)

def wrangle_files(input,output):
#process input folder for markdown and sass files
  draftList = []
  fileList = os.listdir(input)
  for file in fileList:
    if file.endswith(('.md','.txt')):
      article = parse_article(file,input)
      draftList.append(article)
    elif file.endswith('.scss'):
      sassify(file,input,output)
    elif file.endswith('.stache'):
      pass
    elif file.startswith('.'):
      pass
    else:
      shutil.copy2(os.path.join(input,file),
                   os.path.join(output,'static',file))
  return draftList

def build_page(articles,templateName,input,output,fileName):
#turn a dictionary and template into a webpage
  template = read_file(templateName,input)
  data = {'updated':dt.isoformat(dt.now())+'Z',
          'tag':fileName[:-5],'articles':articles}
  html = pystache.render(template,data)
  filePath = os.path.join(output,fileName)
  codecs.open(filePath,'w','utf8').write(html)

def build_site(parameters):
#build the relevant pages and process files
  pm = parameters
  draftList = wrangle_files(pm['input'],pm['output'])    
  articleList = sort_and_filter(draftList)
    
  for article in articleList:
    build_page(article,'page.stache',pm['input'],
               pm['output'],article['slug'])

  tagList = list_tags(articleList)
  for tag in tagList:
    editedList = select_articles(tag,articleList)
    build_page(editedList,'tag.stache',
               pm['input'],pm['output'],tag+'.html')

  build_page(articleList[:pm['homeLength']],'index.stache',
             pm['input'],pm['output'],'index.html')
  build_page(articleList[:pm['feedLength']],'feed.stache',
             pm['input'],pm['output'],'feed.xml')
  build_page(articleList,'archive.stache',
             pm['input'],pm['output'],'archive.html')

if __name__ == '__main__':
  build_site(DieM)