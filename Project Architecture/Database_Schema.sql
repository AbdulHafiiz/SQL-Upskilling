.eqp ON
.echo ON
.bail ON
.timer ON
.mode box --wrap 25
.log "database_creation_20231217.log"

PRAGMA foreign_keys = ON;

BEGIN;

-- STATUS TABLE

CREATE TABLE status_reference IF NOT EXISTS (
    status_id INTEGER(1) PRIMARY KEY AUTOINCREMENT UNIQUE,
    name TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL DEFAULT 'general',
    description TEXT
) STRICT;

-- IMAGE TABLE

CREATE TABLE images_table IF NOT EXISTS (
    image_id INTEGER(6) PRIMARY KEY AUTOINCREMENT,
    source_url TEXT NOT NULL,
    blob_storage_uuid TEXT NOT NULL UNIQUE,
    shape TEXT NOT NULL,
    upload_timestamp INTEGER(6) NOT NULL DEFAULT strftime('%s', CURRENT_TIMESTAMP),
    upload_date INTEGER(6) NOT NULL DEFAULT strftime('%s', CURRENT_DATE),
    status_id INTEGER(1) NOT NULL DEFAULT 0,
    description_text TEXT,
    uploader_id INTEGER(6) NOT NULL,
    likes INTEGER(2) NOT NULL DEFAULT 0,
    dislikes INTEGER(2) NOT NULL DEFAULT 0,
    FOREIGN KEY (image_status_id)
        REFERENCES status_reference (status_id)
            ON UPDATE CASCADE
            ON DELETE SET NULL,
    FOREIGN KEY (uploader_id)
        REFERENCES users_table (user_id)
            ON UPDATE CASCADE
            ON DELETE NO ACTION,

) STRICT;

CREATE INDEX indexed_image_datetime
    ON images_table (upload_timestamp, upload_date);

-- TAG TABLE

CREATE TABLE tags_table IF NOT EXISTS (
    tag_id INTEGER(4) PRIMARY KEY AUTOINCREMENT UNIQUE,
    type_category TEXT DEFAULT 'None',
    "name" TEXT NOT NULL,
    description TEXT,
    status_id INTEGER(1),
    creation_timestamp INTEGER(6) NOT NULL DEFAULT strftime('%s', CURRENT_TIMESTAMP),
    FOREIGN KEY (status_id)
        REFERENCES status_reference (status_id)
            ON UPDATE CASCADE
            ON DELETE NO ACTION
) STRICT;

-- IMAGE TAG JUNCTION TABLE

CREATE TABLE image_tag_junction IF NOT EXISTS (
    tag_id INTEGER(4),
    image_id INTEGER(6),
    PRIMARY KEY (tag_id, image_id)
    FOREIGN KEY (tag_id)
        REFERENCES tags_table (tag_id)
            ON UPDATE CASCADE
            ON DELETE NO ACTION,
    FOREIGN KEY (image_id)
        REFERENCES images_table (image_id)
            ON UPDATE CASCADE
            ON DELETE NO ACTION
) STRICT;

-- USER TABLE

CREATE TABLE users_table IF NOT EXISTS (
    user_id INTEGER(6) PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    creation_timestamp INTEGER(6) NOT NULL DEFAULT strftime('%s', CURRENT_TIMESTAMP),
    status_id INTEGER(1) NOT NULL DEFAULT 0,
    permission_level INTEGER(1) NOT NULL DEFAULT 0
) STRICT;

-- COMMENT TABLE

CREATE TABLE comments_table IF NOT EXISTS (
    comment_id INTEGER(8) PRIMARY KEY AUTOINCREMENT,
    status_id INTEGER(1) NOT NULL DEFAULT 0,
    user_id INTEGER(6) NOT NULL,
    content TEXT NOT NULL,
    creation_date INTEGER(6) NOT NULL DEFAULT strftime('%s', CURRENT_TIMESTAMP),
    edited BOOLEAN NOT NULL DEFAULT 0,
    likes INTEGER(2) NOT NULL DEFAULT 0,
    dislikes INTEGER(2) NOT NULL DEFAULT 0,
    FOREIGN KEY (user_id)
        REFERENCES users_table
            ON UPDATE CASCADE
            ON DELETE NO ACTION,
    FOREIGN KEY (status_id)
        REFERENCES status_table (status_id)
            ON UPDATE CASCADE
            ON DELETE NO ACTION
) STRICT;

-- USER COMMENT JUNCTION TABLE

CREATE TABLE user_comment_junction IF NOT EXISTS (
    user_id INTEGER(6) NOT NULL,
    comment_id INTEGER(8) NOT NULL,
    PRIMARY KEY (user_id, comment_id)
    FOREIGN KEY user_id
        REFERENCES users_table (user_id)
            ON UPDATE CASCADE
            ON DELETE NO ACTION,
    FOREIGN KEY comment_id (comment_id)
        REFERENCES comments_table (comment_id)
            ON UPDATE CASCADE
            ON DELETE NO ACTION,
);

COMMIT;