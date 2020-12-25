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

CREATE TABLE fiveGrams (
    fivegram_id UUID DEFAULT uuid_generate_v1(),
    key VARCHAR(145) NOT NULL,
    prediction VARCHAR(45) NOT NULL,
    url_id UUID NOT NULL,
    PRIMARY KEY(fivegram_id),
    CONSTRAINT fk_url
        FOREIGN KEY(url_id)
            REFERENCES urls(url_id)
);

CREATE TABLE fourGrams (
    fourgram_id UUID DEFAULT uuid_generate_v1(),
    key VARCHAR(145) NOT NULL,
    prediction VARCHAR(45) NOT NULL,
    url_id UUID NOT NULL,
    PRIMARY KEY(fourgram_id),
    CONSTRAINT fk_url
        FOREIGN KEY(url_id)
            REFERENCES urls(url_id)
);

CREATE TABLE threeGrams (
    threegram_id UUID DEFAULT uuid_generate_v1(),
    key VARCHAR(145) NOT NULL,
    prediction VARCHAR(45) NOT NULL,
    url_id UUID NOT NULL,
    PRIMARY KEY(threegram_id),
    CONSTRAINT fk_url
        FOREIGN KEY(url_id)
            REFERENCES urls(url_id)
);

CREATE TABLE twoGrams (
    twogram_id UUID DEFAULT uuid_generate_v1(),
    key VARCHAR(145) NOT NULL,
    prediction VARCHAR(45) NOT NULL,
    url_id UUID NOT NULL,
    PRIMARY KEY(twogram_id),
    CONSTRAINT fk_url
        FOREIGN KEY(url_id)
            REFERENCES urls(url_id)
);
EOSQL
