#!/usr/bin/python

import xml.etree.ElementTree as ET
import time
import urllib2
import dateutil.parser
import sqlite3
import os
import urlparse

###EXCEPTION CLASSES

class WTF (Exception):
    pass

###UTILITY FUNCTIONS

def now():
    return time.time()
    
def parsedate (date = None):
    if (date is None):
        return None
    else:
        return dateutil.parser.parse(date).isoformat()

def coalesce (element):
    if (element is None):
        return None
    else:
        return element.text

def download(url, directory, filename):
    blocksize = 1048576
    if (not os.path.isdir(directory)):
        os.makedirs(directory)
    infile = urllib2.urlopen(url)
    outfile = open(os.path.join(directory, filename), "w")
    #outfile.write(infile.read())
    block = infile.read(blocksize)
    while (block != ""):
        outfile.write (block)
        block = infile.read(blocksize)
    infile.close()
    outfile.close()

###MAIN CLASSES

class Enclosure:
    def __init__(self, enc_url = None, enc_localpath = None,
                 enc_length = None, enc_type = None, item = None):
        self.url = enc_url
        self.localpath = enc_localpath
        self.length = enc_length
        self.type = enc_type
        self.item = item

    def populate(self, tree):
        try:
            self.url = tree.attrib['url']
        except KeyError :
            self.url = None

        try:
            self.length = tree.attrib['length']
        except KeyError:
            self.length = None

        try:
            self.type = tree.attrib['type']
        except KeyError:
            self.type = None

    def updatedb (self):
        cursor = self.item.channel.rss.snarf.dbconn.cursor()
        cursor.execute("select enc_id from enclosure where item_id = ? and enc_url = ?",
                       [self.item.item_id, self.url])
        result = cursor.fetchone()
        if (result is None):
            cursor.execute("insert into enclosure (item_id, enc_url, " +
                           "enc_length, enc_type) values (?, ?, ?, ?)",
                           [self.item.item_id, self.url, self.length, self.type])
            self.enc_id = cursor.lastrowid
        else:
            self.enc_id = result[0]

class Item:
    def __init__(self, item_title = None, item_link = None,
                 item_comments = None, item_pubdate = None,
                 item_guid = None, item_description = None,
                 channel = None, item_id = None, content = None):
        self.title = item_title
        self.link = item_link
        self.comments = item_comments
        self.pubdate = item_pubdate
        self.datetime = parsedate(item_pubdate)
        self.guid = item_guid
        self.description = item_description
        self.content = content
        self.enclosures = []
        self.channel = channel
        self.item_id = item_id
        
    def populate(self, tree):
        self.title = coalesce(tree.find('title'))
        self.link = coalesce(tree.find('link'))
        self.comments = coalesce(tree.find('comments'))
        self.pubdate = coalesce(tree.find('pubDate'))
        self.datetime = parsedate(self.pubdate)
        self.guid = coalesce(tree.find('guid'))
        self.description = coalesce(tree.find('description'))
        self.content = coalesce(tree.find('{http://purl.org/rss/1.0/modules/content/}encoded'))
        
        for subtree in tree.findall('enclosure'):
            newenclosure = Enclosure(item = self)
            newenclosure.populate(subtree)
            self.enclosures = self.enclosures + [newenclosure]

    def updatedb(self):
        cursor = self.channel.rss.snarf.dbconn.cursor()
        cursor.execute("select item_id from item where item_guid = ? and ch_id = ?",
                       [self.guid, self.channel.ch_id])
        result = cursor.fetchone()
        if (result is None):
            cursor.execute ("insert into item (ch_id, item_title, item_link, " +
                            "item_comments, item_pubdate, item_guid, " +
                            "item_description, item_content, item_datetime) values " +
                            "(?, ?, ?, ?, ?, ?, ?, ?, ?)",
                            [self.channel.ch_id, self.title, self.link,
                             self.comments, self.pubdate, self.guid,
                             self.description, self.content, self.datetime])
            self.item_id = cursor.lastrowid
        else:
            self.item_id = result[0]

            cursor.execute("update item set ch_id = ?, item_title = ?, " +
                           "item_link = ?, item_comments = ?, item_pubdate = ?, " +
                           "item_guid = ?, item_description = ?, item_content = ?, " +
                           "item_datetime = ? where item_id = ?",
                           [self.channel.ch_id, self.title, self.link,
                            self.comments, self.pubdate, self.guid,
                            self.description, self.content, self.datetime,
                            self.item_id])

        for enclosure in self.enclosures:
            enclosure.updatedb()

class Channel:
    def __init__(self, ch_title = None, ch_link = None,
                 ch_language = None, ch_copyright = None,
                 ch_description = None, ch_lastbuild = None,
                 ch_generator = None, rss = None, ch_id = None):
        self.title = ch_title
        self.link = ch_link
        self.language = ch_language
        self.copyright = ch_copyright
        self.description = ch_description
        self.lastbuild = parsedate(ch_lastbuild)
        self.generator = ch_generator
        self.items = []
        self.rss = rss
        self.ch_id = ch_id
        
    def populate(self, tree):
        self.title = coalesce(tree.find('title'))
        self.link = coalesce(tree.find('link'))
        self.language = coalesce(tree.find('language'))
        self.copyright = coalesce(tree.find('copyright'))
        self.description = coalesce(tree.find('description'))
        self.lastbuild = coalesce(tree.find('lastBuildDate'))
        self.datetime = parsedate(self.lastbuild)
        self.generator = coalesce(tree.find('generator'))

        for subtree in tree.findall('item'):
            newitem = Item(channel = self)
            newitem.populate(subtree)
            self.items = self.items + [newitem]

    def updatedb(self):
        cursor = self.rss.snarf.dbconn.cursor()
        cursor.execute("select ch_id from channel where ch_link = ? and feed_id = ?",
                       [self.link, self.rss.feed_id])
        result = cursor.fetchone()
        if (result is None):
            cursor.execute ("insert into channel (feed_id, ch_title, ch_link, " +
                            "ch_language, ch_copyright, ch_description, " +
                            "ch_lastbuild, ch_generator, ch_datetime) values " +
                            "(?, ?, ?, ?, ?, ?, ?, ?, ?)",
                            [self.rss.feed_id, self.title, self.link,
                             self.language, self.copyright, self.description,
                             self.lastbuild, self.generator, self.datetime])
            self.ch_id = cursor.lastrowid
        else:
            self.ch_id = result[0]

            cursor.execute("update channel set ch_title = ?, ch_language = ?, " +
                           "ch_copyright = ?, ch_description = ?, ch_lastbuild = ?, " +
                           "ch_generator = ?, ch_datetime = ? where ch_id = ?",
                           [self.title, self.language, self.copyright,
                            self.description, self.lastbuild, self.generator,
                            self.datetime, self.ch_id])

        for item in self.items:
            item.updatedb()
        
class Rss:
    def __init__(self, url = None, title = None, feed_id = None, snarf = None):
        self.url = url
        self.title = title
        self.feed_id = feed_id
        self.channels = []
        self.snarf = snarf

    def retrieve(self):
        f=urllib2.urlopen(self.url)
        result = f.read()
        f.close()
        return result
        
    def tree_from_xml (self, xml):
        return ET.fromstring(xml)
        
    def populate (self, tree):
        for subtree in tree.findall('channel'):
            newchannel = Channel(rss = self)
            newchannel.populate(subtree)
            self.channels = self.channels + [newchannel]

    def populate_from_url(self, url=None):
        if (url is not None):
            self.url = url

        self.populate(self.tree_from_xml(self.retrieve()))

    def updatedb (self):
        cursor = self.snarf.dbconn.cursor()
        cursor.execute("select feed_id from feed where feed_url = ? and active='t'",
                       [self.url,])
        result = cursor.fetchone()
        if (result is None):
            cursor.execute ("insert into feed (feed_url, active) values (?, 't')",
                            [self.url,])
            self.feed_id = cursor.lastrowid
        else:
            self.feed_id = result[0]

        for channel in self.channels:
            channel.updatedb()

        self.snarf.dbconn.commit()

class Snarf:
    def __init__(self, dbconn = None, base = None):
        self.dbconn = dbconn
        self.feedlist = []
        self.dbtype = None

        if (type(dbconn) is sqlite3.Connection):
            self.dbtype = 'SQLite3'

        if (base is None):
            self.base = os.getcwd()
        else:
            self.base = base

    def connectdb(self, dbpath, dbtype):
        if (dbtype != 'SQLite3'):
            raise WTF

        self.dbconn = sqlite3.connect(dbpath)

    def updatedb(self):
        if (self.dbtype == 'SQLite3'):
            cursor = self.dbconn.cursor()
            cursor.execute ("select feed_id, feed_url from feed where active='t'", [])
            for result in cursor:
                newrss = Rss(url=result[1], feed_id=result[0],
                             snarf = self)
                newrss.populate_from_url()
                newrss.updatedb()
                self.feedlist = self.feedlist + [newrss]

    def retrieve_all_encs(self):
        
        if (self.dbtype == 'SQLite3'):
            readcur = self.dbconn.cursor()
            writecur = self.dbconn.cursor()
            readcur.execute("select e.enc_id, i.item_datetime, c.ch_title, " +
                            "e.enc_url from enclosure e, item i, channel c " +
                            "where e.enc_localpath is null and " +
                            "e.enc_retries > 0 and " +
                            "e.item_id = i.item_id and i.ch_id = c.ch_id " +
                            "order by i.item_datetime desc", [])
            for result in readcur:
                print result
                url = result[3]
                local = os.path.join(result[1][:4], result[1][5:7],
                                     result[1][8:10], result[2])
                filename = os.path.basename(urlparse.urlparse(result[3]).path)

                success = True

                try:
                    download(url = url, directory = os.path.join(self.base, local),
                             filename = filename)
                except:
                    success = False

                if (success):
                    writecur.execute("update enclosure set enc_localpath = ?, " +
                                     "enc_retries = enc_retries - 1 where enc_id = ?",
                                     [os.path.join(local, filename),
                                      result[0]])
                else:
                    writecur.execute("update enclosure set " +
                                     "enc_retries = enc_retries - 1 where enc_id = ?",
                                     [result[0]])
                self.dbconn.commit()
                    
        else:
            raise WTF
        
###THROW AN EXCEPTION IF NOT CALLED AS A LIB.

if (__name__ == "__main__"):
    raise WTF
