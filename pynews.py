#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# filename: pynews.py
# author: Albert Lukaszewski
# version: 0.01
# 
# Released under the GPLv2:
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301 USA.

import feedparser
import MySQLdb
import re

from datetime import datetime

# Read in list of feeds
rssFile = 'rssfeeds.tsv'
RSSfile = open(rssFile, 'r')
feedFile = RSSfile.readlines()
RSSfile.close()

# Read in list of common words that will be removed from the title to
# determine what the keywords of an item are.
wordFile = 'commonwords.txt'
WORDSfile = open(wordFile, 'r')
weedFile = WORDSfile.readlines()
WORDSfile.close()

# Define what whitespace is in the context of a title element
whitespacers = re.compile('([:,;.!?\s\)\(])')

# Define the database access credentials
dbhost = "localhost"
dbuser = "root"
dbpass = "r00tp4ss"
dbdb = "pynews"


def getKeywords(title):
    """
    Receives title of item, sorts out of it the most common English
    words, and returns a string of keywords found in the title.
    """
    keywords = list()
    # Substitute ' - ' separately as the re module tends to botch a
    # match of ' - ' when used with the other regex.
    title = title.replace(' - ', ' ')
    title = re.sub(whitespacers, ' ', title)
    titlewords = title.split(' ')
    for word in titlewords:
        match = 0
        for weed in weedFile:
            weed = weed.strip()
            if word == weed:
                match = 1
            elif word == weed.upper():
                match = 1
            elif word == weed.capitalize():
                match = 1
        if match == 0:
            keywords.append(word)
        
    keywords.sort()
    keywords = ' '.join(keywords)
    keywords = keywords.replace('  ', ' ')
    keywords = keywords.strip()
    return keywords


def main():
    for line in feedFile:
        lines = line.split('\t')
        feedname = lines[0].strip()
        feed = feedparser.parse(lines[1])
        feedretrieved = datetime.now()
        feeddeleted = 0

        for item in feed['items']:
            title = item.title
            link = item.link
            try:
                pubdate = item.published
            except:
                pubdate = "none specified"
            itemposted = str(datetime.now())
            feedname = feedname.encode("utf-8")
            title = title.encode("utf-8")
            link = link.encode("utf-8")
            pubdate = pubdate.encode("utf-8")
            keywords = getKeywords(title)

            print("Feed Name: " + feedname)
            print("Title: " + title)
            print("URL: " + link)
            print("Publication Date: " + pubdate)
            print("Keywords: " + keywords)
            print("\n")

            db = MySQLdb.connect(dbhost, dbuser, dbpass, dbdb)
            cursor = db.cursor()
            if feeddeleted == 0:
                try:
                    cursor.execute("""DELETE FROM feeditems WHERE feedname = "%s" """, (feedname))
                    feeddeleted = 1
                except:
                    pass

            cursor.execute("""INSERT INTO feeditems(feedname,title,url,pubdate,keywords,itemposted, feedretrieved) values("%s", "%s", "%s", "%s", "%s", "%s", "%s")""", (feedname, title, link, pubdate, keywords, itemposted, feedretrieved))

            db.commit()
            db.close()

    return 1

if __name__ == "__main__":
    main()
