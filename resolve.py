#!/usr/bin/env python3

#                   Lyratic Resolution: Silvertongue Edition
#                                  Fog and Ice
#                       A blog engine by Duncan McNicholl
#                                   CC-BY-NC

#import necessary modules
from datetime import datetime as dt
import string
import codecs
import os
import shutil
import gzip
import argparse
import markdown
import pystache
try:
  from scss import Scss
except ImportError:
  pass

def build_site(parameters):
#build the relevant pages and process files
  pm = parameters
  draftList,templateList = wrangle_files(pm['input'],pm['output'])    
  articleList = sort_by_date(draftList)
  articleList = filter_drafts(articleList)
  articleList = older_and_newer(articleList)
    
  for article in articleList:
    if (article not in os.listdir(pm['output']) or 
    modTime(output,article['slug']) < modTime(input,article['sourceFile'])):
      build_page(article,templateList['page.stache'],
                 pm['output'],article['slug'])

  tagList = list_tags(articleList)
  for tag in tagList:
    editedList = select_tagged_articles(tag,articleList)
    build_page(editedList,templateList['tag.stache'],
               pm['output'],tag+'.html')

  for page in pm['pages']:
    if len(articleList)>page[1]:
        nextPage = articleList[page[1]]['slug']
    else:
        nextPage = 0
    build_page(articleList[:page[1]],templateList[os.path.splitext(page[0])[0]+
               '.stache'],pm['output'],page[0],nextPage)

  compress_output(pm['output'])

def wrangle_files(input,output):
#process input folder for markdown and sass files
  draftList = []
  templateList = {}
  fileList = os.listdir(input)
  existingOutput = os.listdir(output)
  for file in fileList:
    if file.endswith(('.md','.txt')):
      article = parse_article(file,input)
      draftList.append(article)
    elif file.endswith('.scss'):
      sassify(file,input,output)
    elif file.endswith('.stache'):
      template = parse_template(file,input)
      templateList[file] = template
    elif file.startswith('.'):
      pass
    elif file not in existingOutput:
      copy_file(file,input,output)
  return draftList,templateList

def sort_by_date(articleList):
#sorts articles chronologically
  articleList.sort(key=lambda k: k['datestamp'], reverse=True)
  return articleList

def filter_drafts(articleList):
#filters out post-dated articles
  for article in articleList:
    if article['datestamp'] >= dt.today():
      articleList.remove(article)
  return articleList

def older_and_newer(articleList):
#add hooks for older/newer articles buttons
  n=0
  for article in articleList[1:]:
    article['newer']={'newer':articleList[n]['slug']}
    n+=1
  n=1
  for article in articleList[:-1]:
    article['older']={'older':articleList[n]['slug']}
    n+=1
  return articleList

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

def parse_template(fileName,input):
#pre-parse mustache template
  template = read_file(fileName,input)
  parsedTemplate = pystache.parse(template)
  return parsedTemplate

def parse_article(fileName,input):
#read contents of file into dictionary
  md = markdown.Markdown(extensions = ['meta','smarty'])
  post = read_file(fileName,input)
  modifiedTime = modTime(input,fileName)
  body = md.convert(post)
  article = md.Meta
  for key in article:
    article[key]='\n'.join(article[key])
  article.setdefault('title',os.path.splitext(fileName)[0])
  article.setdefault('date',dt.fromtimestamp(modifiedTime).strftime('%Y-%m-%d'))
  article['datestamp']=dt.strptime(article['date'],'%Y-%m-%d')
  article['body'] = body
  if 'tags' in article:
    article['tags'] = list(article['tags'].split(', '))
    article['taglist'] = ({'tag':id} for id in article['tags'])
  #then generate further useful attributes from metadata
  article['date'] = article['datestamp'].strftime('%A, %d %B \'%y')
  article['weekday'] = article['datestamp'].strftime('%A')
  article['updated'] = dt.fromtimestamp(modifiedTime).isoformat()+'Z'
  remove_punct_map = dict.fromkeys(map(ord, string.punctuation))
  lowerTitle = str(article['title']).lower().translate(remove_punct_map)
  article['slug'] = '-'.join(lowerTitle.split())+'.html'
  article['wordcount'] = len(article['body'].split())+1
  article['readtime'] = str(int(article['wordcount']/200)+2)
  article['sourceFile'] = fileName
  return article
    
def build_page(articles,template,output,fileName,nextPage=0):
#turn a dictionary and template into a webpage
  data = {'updated':dt.isoformat(dt.utcnow())+'Z',
          'tag':fileName[:-5],
          'nextPage':nextPage,
          'articles':articles}
  html = pystache.render(template,data)
  write_file(fileName,output,html)
  
def read_file(fileName,input):
#read contents of file into unicode string
  filePath = os.path.join(input,fileName)
  fileContents = codecs.open(filePath,'r','utf8').read()
  return fileContents

def write_file(fileName,output,content):
#write unicode string out to file
    filePath = os.path.join(output,fileName)
    codecs.open(filePath,'w','utf8').write(content)

def copy_file(fileName,input,output):
#copy production-ready files to output
    shutil.copy2(os.path.join(input,fileName),
                 os.path.join(output,fileName))

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
  parser = argparse.ArgumentParser()
  parser.add_argument('output', nargs='?', default=os.getcwd(), 
                      help='the output folder where the blog ends up')
  parser.add_argument('input', nargs='?', default=os.getcwd(), 
                      help='the input folder with markdown and mustache files')
  parameters = vars(parser.parse_args())
  parameters['pages'] = [('index.html',6),('archive.html',1024),('feed.xml',12)]
  build_site(parameters)