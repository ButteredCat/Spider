#!/usr/bin/env python
# -*- coding:utf-8 -*-

from HTMLParser import HTMLParser 
import Queue

import requests as req

class MoviePageParser(HTMLParser):
    movie_link = u'http://movie.douban.com/subject/'

    def __init__(self):
        self.__movie_id = []
        self.__movie_info = {}
        HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        if tag == u'a':
            for attr in attrs:
                if self.__is_movie_link(attr):
                    movie_id = self.__get_id(attr[1])
                    if movie_id is not None and \
                        movie_id not in self.__movie_id:
                        self.__movie_id.append(movie_id)


    def get_adj_movie_ids(self, page):
        self.feed(page)
        self.close()
        return self.__movie_id

    def __is_movie_link(self, attr):
        return attr[0] == u'href' and attr[1].startswith(self.movie_link) 

    def __get_id(self, link):
        link = link[len(self.movie_link) : ]
        movie_id = link[ : link.find(u'/') ]
        return int(movie_id) if movie_id.isnumeric() else None


init_page = u'http://movie.douban.com/subject/4876722/'
api_url = u'http://api.douban.com/v2/movie/'
movie_link = u'http://movie.douban.com/subject/'

def add_ids(queue, ids):
    for each_id in ids:
        queue.put(each_id)

def main():
    queue = Queue.Queue()
    seen = set()
    r = req.get(init_page)
    parser = MoviePageParser()
    ids = parser.get_adj_movie_ids(r.text)
    add_ids(queue, ids)
    while(True):
        if queue.qsize() > 0:
            each_id = queue.get()
            if each_id not in seen:
                r = req.get(api_url + str(each_id))
                if r.status_code == 200:
                    print r.json()[u'title']
                    seen.add(each_id)
                r = req.get(movie_link + str(each_id))
                ids = parser.get_adj_movie_ids(r.text)
                add_ids(queue, ids)
        else:
            break


if __name__=='__main__':
    main()
