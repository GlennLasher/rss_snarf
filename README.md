# RSS Snarfer

Archiver for podcasts and RSS news feeds

#What's that, then?

This Python library and its accompanying bits and bobs serve to read
content from RSS feeds (as many as you can practically fit into the
database) and archive the contents of those feeds.  I wrote it
initially to give me a way to search back through articles I might
have read and podcasts I might have listened to.

There are two scripts that provide entry points to the library.

One, called updatedb.py, will read the RSS feeds, parse them, and
store the parsed outcome in the database.

The other, fetchall.py, will scan the database table that holds the
enclosures, and attempt to fetch any files from there that have not
yet been successfully fetched.  It's pretty error-tolerant, so if it
fails, it just decrements a counter, and stops trying when that
counter runs out.

#Vision

Because the content carried on RSS feeds tends to be somewhat
ephemeral, the idea here was to create an archive of the feeds I read
and the podcasts I listen to.  It's not complete as of yet, so here
are the things to be done yet:

 * Create methods to convert database contents into RSS objects, and
   RSS objects back into a valid RSS feed.

 * Create the means to move data into a PostgreSQL database

 * Combining the above two, create import/export/transport scripts to
   enable moving data from one instance to another and/or convert from
   one type of data store to another (e.g. SQLite to PostgreSQL).

 * Add tables to contain a word index of key fields: channel title,
   channel description, item title, item comments, item description
   and item content.

 * Create methods to update those tables

 * Create methods to use those tables to search for channels and items
   based on those tables

 * Create a more complete command-line interface

 * Create a WebUI, maybe using Flask.
