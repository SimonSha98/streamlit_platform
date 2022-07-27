CREATE TABLE stock (
    id SERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    name TEXT NOT NULL,
    exchange TEXT NOT NULL
);

CREATE TABLE stock_price (
    stock_id SERIAL NOT NULL,
    dt TIMESTAMP NOT NULL,
    open NUMERIC NOT NULL, 
    high NUMERIC NOT NULL,
    low NUMERIC NOT NULL,
    close NUMERIC NOT NULL, 
    volume NUMERIC NOT NULL,
    PRIMARY KEY (stock_id, dt),
    CONSTRAINT fk_stock FOREIGN KEY (stock_id) REFERENCES stock (id)
);

CREATE INDEX indx ON stock_price (stock_id, dt DESC);