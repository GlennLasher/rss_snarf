#!/usr/bin/python

import snarf_rss_lib
import sqlite3

dbconn = sqlite3.connect("snarfer.db")
snarf = snarf_rss_lib.Snarf(dbconn = dbconn,
                            base = "/extraspace/snarfer/repository")
snarf.retrieve_all_encs()
