#!/usr/bin/env python

#      Lyratic Resolution: Belacqua Edition
#       A blog engine by Duncan McNicholl
#                   CC-BY-NC

import markdown
import string
import datetime
import time
import os
import codecs

class Article(object):
  def __init__(self, file):
    md = markdown.Markdown(extensions = ['meta'])
    with codecs.open(os.path.join(dir,file),'r','utf8')as f:
      post = unicode(f.read())
    self.body = md.convert(post)
    self.title = (md.Meta['title'])[0]
    self.date = (md.Meta['date'])[0]
    self.abstract = (md.Meta['abstract'])[0]
    self.tags = (md.Meta['tags'])
    self.slug = '-'.join(str(self.title).lower().translate(None,string.punctuation).split())+'.html'
    self.datestamp = datetime.datetime.fromtimestamp(time.mktime(time.strptime(str(self.date), '%Y-%m-%d'))).date()
    self.nicedate = self.datestamp.strftime('%A, %d %B \'%y')
    self.filename = os.path.join(output_dir,self.slug)
    
#read in files

dir = '/path/to/markdown/files'
template_dir = '/path/to/template/files'
output_dir = '/path/to/html/files'

articlelist = os.listdir(dir)
templatelist = os.listdir(template_dir)
templates = {}
articles = []

for template in templatelist:
  if not template.startswith('.'):
    with open(os.path.join(template_dir,template)) as t:
      templates[template[:-4]] = string.Template(t.read())

for a in articlelist:
  if not a.startswith('.'):
    article = Article(a)
    articles.append(article)

articles.sort(key=lambda k: k.datestamp, reverse=True)

#generate archive, feed, home, and pages

content = {'archive':'','feed':'','home':''}
n = 0

for article in articles:
  pieces = dict(body = article.body, title = article.title, date = article.nicedate, abstract = article.abstract, tags = article.tags, slug = article.slug, datestamp = article.date + 'T15:00:00Z')
  content['archive'] = content['archive'] + templates['snippet'].substitute(pieces)
  if n < 1:
    content['updated'] = pieces['datestamp']
  if n < 6:
    content['home'] = content['home'] + templates['post'].substitute(pieces)
  if n < 12:
    content['feed'] = content['feed'] + templates['atom'].substitute(pieces)
  with codecs.open(os.path.join(output_dir,article.filename),'w','utf8') as o:
    o.write(templates['page'].substitute(pieces))
  n = n+1
  
#write out pages

with codecs.open(os.path.join(output_dir,'index.html'),'w','utf8') as o:
  o.write(templates['home'].substitute(content))
with codecs.open(os.path.join(output_dir,'archive.html'),'w','utf8') as o:
  o.write(templates['archive'].substitute(content))
with codecs.open(os.path.join(output_dir,'index.xml'),'w','utf8') as o:
  o.write(templates['feed'].substitute(content))
