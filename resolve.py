#!/usr/bin/env python

#                   Lyratic Resolution: Silvertongue Edition
#                                  The Spies
#                       A blog engine by Duncan McNicholl
#                                   CC-BY-NC

#start with blog parameters
DieM = {'input':'/path/to/input',
        'output':'/path/to/output',
        'feedLength':12,
        'homeLength':6}
        
AWS = {'access':'AWS_ACCESS_KEY',
       'secret':'AWS_SECRET_KEY',
       'bucket':'BUCKET_NAME'}

#import necessary modules
from datetime import datetime as dt
import string
import codecs
import os
import shutil
import gzip
import markdown
import pystache
try:
  from scss import Scss
  from boto.s3.connection import S3Connection
  from boto.s3.key import Key
except ImportError:
  pass

def build_site(parameters):
#build the relevant pages and process files
  pm = parameters
  if pm['output'] == 's3':
    pm['output'] = connect_to_s3(AWS)
  draftList = wrangle_files(pm['input'],pm['output'])    
  articleList = sort_and_filter(draftList)
    
  for article in articleList:
    if (article not in os.listdir(pm['output']) or 
    modTime(output,article['slug']) < modTime(input,article['sourceFile'])):
      build_page(article,'page.stache',pm['input'],
                 pm['output'],article['slug'])

  tagList = list_tags(articleList)
  for tag in tagList:
    editedList = select_tagged_articles(tag,articleList)
    build_page(editedList,'tag.stache',
               pm['input'],pm['output'],tag+'.html')

  build_page(articleList[:pm['homeLength']],'index.stache',
             pm['input'],pm['output'],'index.html')
  build_page(articleList[:pm['feedLength']],'feed.stache',
             pm['input'],pm['output'],'feed.xml')
  build_page(articleList,'archive.stache',
             pm['input'],pm['output'],'archive.html')
  if type(pm['output']) == str:
    compress_output(pm['output'])

def wrangle_files(input,output):
#process input folder for markdown and sass files
  draftList = []
  fileList = os.listdir(input)
  existingOutput = os.listdir(output)
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
    elif file not in existingOutput:
      copy_file(file,input,output)
  return draftList

def sort_and_filter(articleList):
#sorts articles chronologically and filters out post-dated articles
  articleList.sort(key=lambda k: k['datestamp'], reverse=True)
  articleListForPublishing = filter(draft_status,articleList)
  return articleListForPublishing
  	
def draft_status(article):
#determine if article is post-dated
  return article['datestamp'] <= dt.today()

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

def select_tagged_articles(tag,articles):
#select articles with given tag
  editedList = []
  for article in articles:
    try:
      if tag in article['tags']:
        editedList.append(article)
    except KeyError:
      pass
  return editedList

def parse_article(fileName,input):
#read contents of file into dictionary
  md = markdown.Markdown(extensions = ['meta','smarty'])
  post = read_file(fileName,input)
  modifiedTime = modTime(input,fileName)
  article = {}
  article['body'] = md.convert(post)
  try: #try to get title from front matter
    article['title'] = md.Meta['title'][0]
  except KeyError: #use filename if not present
    article['title'] = os.path.splittext(fileName)[0]
  try: #try to get date from front matter
    article['datestamp'] = dt.strptime(md.Meta['date'][0],'%Y-%m-%d')
  except KeyError: #use modified date if not present
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
  article['updated'] = dt.fromtimestamp(modifiedTime).isoformat()+'Z'
  lowerTitle = str(article['title']).lower().translate(None,string.punctuation)
  article['slug'] = '-'.join(lowerTitle.split())+'.html'
  article['wordcount'] = len(article['body'].split())+1
  article['readtime'] = str(int(article['wordcount']/200)+2)
  article['sourceFile'] = fileName
  return article
    
def build_page(articles,templateName,input,output,fileName):
#turn a dictionary and template into a webpage
  template = read_file(templateName,input)
  data = {'updated':dt.isoformat(dt.utcnow())+'Z',
          'tag':fileName[:-5],'articles':articles}
  html = pystache.render(template,data)
  write_file(fileName,output,html)

def connect_to_s3(AWS):
#open connection to s3 bucket
  conn = S3Connection(AWS['access'],AWS['secret'])
  bucket = conn.get_bucket(AWS['bucket'])
  return bucket
  
def read_file(fileName,input):
#read contents of file into unicode string
  filePath = os.path.join(input,fileName)
  fileContents = codecs.open(filePath,'r','utf8').read()
  return unicode(fileContents)

def write_file(fileName,output,content):
#write unicode string out to file
  if type(output) == str:
    filePath = os.path.join(output,fileName)
    codecs.open(filePath,'w','utf8').write(content)
  else:
    k = Key(output)
    k.key = fileName
    k.set_contents_from_string(content)

def copy_file(fileName,input,output):
#copy production-ready files to output
  if type(output) == str:
    shutil.copy2(os.path.join(input,fileName),
                 os.path.join(output,fileName))
  else:
    k = Key(output)
    k.key = fileName
    k.set_contents_from_filename(os.path.join(input,fileName))

def modTime(dir,file):
#retrieve modification time for file
  return os.path.getmtime(os.path.join(dir,file))
  
def sassify(file,input,output):
#process scss file using Sass
  scss = read_file(file,input)
  compiler = Scss(scss_opts={'style':'compact'})
  css = compiler.compile(scss)
  fileName = file[:-4]+'css'
  write_file(fileName,output,css)

def compress_output(output):
#compress text files in output
  fileList = os.listdir(output)
  for file in fileList:
    if file.endswith(('.html','.xml','.css')):
      f_in = open(os.path.join(output,file), 'rb')
      f_out = gzip.open(os.path.join(output,file) + '.gz', 'wb')
      f_out.writelines(f_in)
      f_out.close()
      f_in.close()

if __name__ == '__main__':
  build_site(DieM)