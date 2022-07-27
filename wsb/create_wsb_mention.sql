CREATE TABLE mention (
    stock_id INTEGER,
    dt TIMESTAMP NOT NULL,
    message TEXT NOT NULL,
    source TEXT NOT NULL,
    url TEXT NOT NULL,
    PRIMARY KEY (stock_id, dt)
);
CREATE INDEX indx ON mention (stock_id, dt DESC);