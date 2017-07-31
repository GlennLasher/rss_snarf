
CREATE TABLE feed (
    feed_id INTEGER PRIMARY KEY AUTOINCREMENT,
    feed_url TEXT,
    active BOOLEAN default 't'
);

CREATE TABLE channel (
    ch_id INTEGER PRIMARY KEY AUTOINCREMENT,
    feed_id INTEGER REFERENCES feed(feed_id),
    ch_title TEXT,
    ch_link TEXT,
    ch_language TEXT,
    ch_copyright TEXT,
    ch_description TEXT,
    ch_lastbuild TEXT, --unaltered string from feed
    ch_generator TEXT,
    ch_datetime TIMESTAMP
);

CREATE TABLE item (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ch_id INTEGER REFERENCES channel(ch_id),
    item_title TEXT,
    item_link TEXT,
    item_comments TEXT,
    item_pubdate TEXT, --unaltered string from feed
    item_guid TEXT,
    item_description TEXT,
    item_content TEXT,
    item_datetime TIMESTAMP
);

CREATE TABLE enclosure (
    enc_id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER REFERENCES item(item_id),
    enc_url TEXT,
    enc_length INTEGER,
    enc_type TEXT,
    enc_localpath TEXT,
    enc_retries INTEGER DEFAULT 5
);

