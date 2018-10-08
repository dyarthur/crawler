#!/usr/bin/env python
# coding: utf-8

import os
import sys
import traceback
import logging

import json
import requests

cwd = os.getcwd()

CONFIG_FILE = cwd + "/crawler.conf"

# This file save downloaded books
BOOKS_JSON = cwd + '/books.json'


def getConf():
    try:
        with open(CONFIG_FILE) as cfg_data:
            return json.load(cfg_data)
    except:
        logging.error(traceback.format_exc())
        return {}


def get(num):
    ids = []
    if num is None:
        try:
            cfg = getConf()
            ids = cfg["sgwaa"]["download_list"]
        except:
            logging.error(traceback.format_exc())
            logging.error("can not get download list")
            return
    else:
        ids.append(num)

    for id in ids:
        url = 'http://www.sgwaa.com/read/%s/index.html' % id
        preurl = 'http://www.sgwaa.com/read/%s/' % id

        os.system('cp -fp %s %s.bak' % (BOOKS_JSON, BOOKS_JSON))
        try:
            with open(BOOKS_JSON) as json_data:
                books = json.load(json_data)
        except:
            logging.error(traceback.format_exc())
            logging.error("can not get downloaded book list")
            books = {}

        r = requests.get(url)
        if r.status_code == 200:
            content = r.text.encode('latin1').decode('gbk', 'ignore')

            # find book name
            index = 0
            key = '<a href="/read/%s/index.html">' % id
            index = content.find(key, index)
            if index >= 0:
                name_content = content[index: index + 100]
                book_name = name_content.split(">")[1][:-3]
                logging.info("book name: %s" % book_name)
            else:
                logging.error("can not get the book name")
                return

            # find book author
            index = content.find("作者：".decode('utf-8'), index)
            if index >= 0:
                author_content = content[index: index + 100]
                author = author_content.split("<")[0][len("作者：".decode('utf-8')):]
                logging.info("book author: %s" % author)
            else:
                logging.error("can not get the book author")
                return

            key = "<dd><a href="
            file_name = cwd + "/books/《".decode('utf-8') + book_name + "》作者：".decode('utf-8') + author + ".txt"
            book = open(file_name, "a")
            while True:
                index = content.find(key, index)
                if index < 0:
                    break
                try:
                    chapter = content[index: index + 100]
                    # get chapter link and name
                    chapter_link = preurl + chapter.split('"')[1]
                    chapter_name = chapter.split(">")[2][:-3]
                    book.write(
                        "\r\n                   ".encode('utf8') + chapter_name.encode('utf8') + "\r\n".encode('utf8'))
                    # get chapter content
                    logging.info(chapter_name)
                    ret = requests.get(chapter_link)
                    if ret.status_code == 200:
                        chapter_content = ret.text.encode('latin1').decode('gbk', 'ignore')
                        # print chapter_content
                        chapter_key = "&nbsp;&nbsp;&nbsp;&nbsp;"
                        i = 0
                        while True:
                            i = chapter_content.find(chapter_key, i)
                            if i < 0:
                                break
                            sub_content = chapter_content[i:]
                            string = "    " + sub_content.split(chapter_key)[1].split("<br")[0].split("</div")[0] + "\r\n"
                            book.write(string.encode('utf8'))
                            i += len(chapter_key)
                    else:
                        chapter_content = "IT CANNOT BE DOWNLOADED FROM WEB, CHECK " + chapter_link + " FOR DETAIL\r\n"
                        book.write(chapter_content.encode('utf8'))
                except:
                    logging.error(chapter_name)
                    logging.error(traceback.format_exc())
                    chapter_content = "IT CANNOT BE DOWNLOADED FROM WEB, CHECK " + chapter_link + " FOR DETAIL\r\n"
                    book.write(chapter_content.encode('utf8'))
                # for next chapter search
                index += 20

            book.close()
            if "sgwaa" not in books:
                books["sgwaa"] = {}
            books["sgwaa"][id] = {"name": book_name, "author": author}
            with open(BOOKS_JSON, 'w') as outfile:
                outfile.write(json.dumps(books, ensure_ascii=False, sort_keys=True, indent=4).encode('utf8'))

            logging.info("Book %s has been downloaded." % book_name)
        else:
            logging.error("can not get the url")


def init():
    pass


def usage():
    print "python crawler.py init\n" \
          "python crawler.py get xxx(id)"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if len(sys.argv) > 1:
        if sys.argv[1] == "init":
            init()
        elif sys.argv[1] == "get":
            if len(sys.argv) > 2:
                get(sys.argv[2])
            else:
                get(None)
        else:
            usage()
    else:
        usage()
