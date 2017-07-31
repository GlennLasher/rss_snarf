#!/usr/bin/python

import snarf_rss_lib
import sqlite3

dbconn = sqlite3.connect("snarfer.db")
snarf = snarf_rss_lib.Snarf(dbconn)
snarf.updatedb()
