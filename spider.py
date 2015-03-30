#!/usr/bin/env python
# -*- coding:utf-8 -*-

from HTMLParser import HTMLParser 
from Queue import Queue

import requests as req

from multithreads.multithreads import MT
from multithreads.lockedset import LockedSet

class Parser(HTMLParser):
    movie_link = u'http://movie.douban.com/subject/'
        
    def __init__(self):
        self.restore()
        HTMLParser.__init__(self)

    def restore(self):
        self.title = False
        self.movie = {}
        self.movie['adj_movies'] = set()

    def handle_starttag(self, tag, attrs):
        if tag == u'a':
            for attr in attrs:
                if self.__is_movie_link(attr):
                    movie_id = self.__get_id(attr[1])
                    if movie_id is not None:
                        self.movie['adj_movies'].add(movie_id)
        if tag == u'title':
            self.title = True

    def handle_data(self, data):
        if self.title:
            self.movie['title'] = data[ : data.find(u'(') ].strip()

    def handle_endtag(self, tag):
        self.title = False

    def parse(self, page):
        self.restore()
        self.feed(page)
        self.close()
        return self.movie

    def __is_movie_link(self, attr):
        return attr[0] == u'href' and attr[1].startswith(self.movie_link) 

    def __get_id(self, link):
        link = link[len(self.movie_link) : ]
        movie_id = link[ : link.find(u'/') ]
        return int(movie_id) if movie_id.isnumeric() else None

    
init_page = u'http://movie.douban.com/subject/4876722/'
movie_link = u'http://movie.douban.com/subject/'

def spider(id_q, seen):
    while True:
        movie_id = id_q.get(block=1)
        seen.add(movie_id)
        http_req = req.get(movie_link + str(movie_id))
        if http_req.status_code == 200:
            parser = Parser()
            movie_info = parser.parse(http_req.text)
            print movie_info['title']
            for each_id in movie_info['adj_movies']:
                if each_id not in seen:
                    id_q.put(each_id, block=1)
        else:
            id_q.put(movie_id, 1)
            seen.remove(movie_id)
            print 'err'

def q_maintainer(id_q, seen):
    while True:
        if id_q.full():
            id_q.get()
        elif id_q.empty():
            pass
            

funcs = [spider, spider, spider, spider, q_maintainer]
nfuncs = range(len(funcs))

def main():
    id_q = Queue(90)
    seen = LockedSet()

    id_q.put(4876722) #init page
    print len(funcs)

    threads = []
    for i in nfuncs:
        t = MT(funcs[i], (id_q, seen), funcs[i].__name__)
        threads.append(t)

    for i in nfuncs:
        threads[i].start()

    for i in nfuncs:
        threads[i].join()

    print 'DONE'
    
if __name__=='__main__':
    main()
