
CREATE TABLE word (
    word_id INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT,
    word_isstopword BOOLEAN DEFAULT false
);

CREATE TABLE word_channel (
    wc_id INTEGER PRIMARY KEY AUTOINCREMENT,
    word_id INTEGER REFERENCES word(word_id),
    ch_id INTEGER REFERENCES channel(ch_id),
    wc_count INTEGER,
    wc_title INTEGER,
    wc_description INTEGER
);

CREATE TABLE word_item (
    wi_id INTEGER PRIMARY KEY AUTOINCREMENT,
    word_id INTEGER REFERENCES word(word_id),
    item_id INTEGER REFERENCES item(item_id),
    wi_count INTEGER,
    wi_title INTEGER,
    wi_comments INTEGER,
    wi_description INTEGER,
    wi_content INTEGER
);
