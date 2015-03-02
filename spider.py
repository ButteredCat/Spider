#!/usr/bin/env python
# -*- coding:utf-8 -*-

from HTMLParser import HTMLParser 
import Queue

import requests as req

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

def add_ids(queue, ids):
    for each_id in ids:
        queue.put(each_id)

def main():
    queue = Queue.Queue()
    seen = set()
    r = req.get(init_page)
    parser = Parser()
    movie = parser.parse(r.text)
    add_ids(queue, movie['adj_movies'])
    while(True):
        if queue.qsize() > 0:
            each_id = queue.get()
            if each_id not in seen:
                r = req.get(movie_link + str(each_id))
                if r.status_code == 200:
                    movie = parser.parse(r.text)
                    add_ids(queue, movie['adj_movies'])
                    print movie[u'title']
                    seen.add(each_id)
                else:
                    print 'error'
        else:
            break


if __name__=='__main__':
    main()
