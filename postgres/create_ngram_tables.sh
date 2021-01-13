#!/bin/bash



psql -v ON_ERROR_STOP=1 --username "ngrams" --dbname "ngrams" <<-EOSQL
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE urls (
    url_id UUID DEFAULT uuid_generate_v1(),
    url TEXT UNIQUE NOT NULL,
    kafka_offset INT NOT NULL,
    kafka_produce_time TIMESTAMPTZ NOT NULL,
    PRIMARY KEY(url_id)
);

CREATE TABLE ngrams (
    fivegram_id UUID DEFAULT uuid_generate_v1(),
    key VARCHAR(145) NOT NULL,
    prediction VARCHAR(45) NOT NULL,
    n INT NOT NULL,
    url_id UUID NOT NULL,
    PRIMARY KEY(fivegram_id),
    CONSTRAINT fk_url
        FOREIGN KEY(url_id)
            REFERENCES urls(url_id)
);
EOSQL
