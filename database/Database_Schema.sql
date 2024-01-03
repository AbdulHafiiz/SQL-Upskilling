.eqp ON
.echo ON
.bail ON
.timer ON
.mode box --wrap 25
.log "./logs/database_creation.log"

PRAGMA foreign_keys = ON;

BEGIN;

-- STATUS TABLE

CREATE TABLE IF NOT EXISTS status_reference (
    status_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
    "name" TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL DEFAULT 'general',
    "description" TEXT
) STRICT;

-- PERMISSIONS TABLE

CREATE TABLE IF NOT EXISTS permission_reference (
    permission_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
    "name" TEXT NOT NULL UNIQUE,
    "description" TEXT
) STRICT;

-- USER TABLE

CREATE TABLE IF NOT EXISTS users_table (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    creation_timestamp INTEGER NOT NULL DEFAULT (strftime('%s', CURRENT_TIMESTAMP)),
    status_id INTEGER NOT NULL DEFAULT 7,
    permission_id INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (permission_id)
        REFERENCES permission_reference (permission_id)
            ON UPDATE CASCADE
            ON DELETE NO ACTION
) STRICT;

-- IMAGE TABLE

CREATE TABLE IF NOT EXISTS images_table (
    image_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_url TEXT NOT NULL,
    blob_storage_uuid BLOB NOT NULL,
    shape TEXT NOT NULL,
    upload_timestamp INTEGER NOT NULL DEFAULT (strftime('%s', CURRENT_TIMESTAMP)),
    upload_date INTEGER NOT NULL DEFAULT (strftime('%s', CURRENT_DATE)),
    status_id INTEGER NOT NULL DEFAULT 0,
    "description" TEXT,
    uploader_id INTEGER NOT NULL,
    likes INTEGER NOT NULL DEFAULT 0,
    dislikes INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (status_id)
        REFERENCES status_reference (status_id)
            ON UPDATE CASCADE
            ON DELETE SET NULL,
    FOREIGN KEY (uploader_id)
        REFERENCES users_table (user_id)
            ON UPDATE CASCADE
            ON DELETE NO ACTION

) STRICT;

CREATE INDEX IF NOT EXISTS indexed_image_datetime
    ON images_table (upload_timestamp, upload_date);

-- TAG TABLE

CREATE TABLE IF NOT EXISTS tags_table (
    tag_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
    type_category TEXT DEFAULT 'None',
    "name" TEXT NOT NULL,
    "description" TEXT,
    status_id INTEGER,
    creation_timestamp INTEGER NOT NULL DEFAULT (strftime('%s', CURRENT_TIMESTAMP)),
    FOREIGN KEY (status_id)
        REFERENCES status_reference (status_id)
            ON UPDATE CASCADE
            ON DELETE NO ACTION
) STRICT;

-- IMAGE TAG JUNCTION TABLE

CREATE TABLE IF NOT EXISTS image_tag_junction (
    tag_id INTEGER,
    image_id INTEGER,
    PRIMARY KEY (tag_id, image_id),
    FOREIGN KEY (tag_id)
        REFERENCES tags_table (tag_id)
            ON UPDATE CASCADE
            ON DELETE NO ACTION,
    FOREIGN KEY (image_id)
        REFERENCES images_table (image_id)
            ON UPDATE CASCADE
            ON DELETE NO ACTION
) STRICT;

-- IMAGE SAVED BY USER JUNCTION TABLE

CREATE TABLE IF NOT EXISTS user_favourites_junction (
    user_id INTEGER NOT NULL,
    image_id INTEGER NOT NULL,
    PRIMARY KEY (user_id, image_id),
    FOREIGN KEY (user_id)
        REFERENCES users_table (user_id)
            ON UPDATE CASCADE
            ON DELETE NO ACTION,
    FOREIGN KEY (image_id)
        REFERENCES images_table (image_id)
            ON UPDATE CASCADE
            ON DELETE NO ACTION
) STRICT;

-- COMMENT TABLE

CREATE TABLE IF NOT EXISTS comments_table (
    comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    status_id INTEGER NOT NULL DEFAULT 12,
    content TEXT NOT NULL,
    creation_date INTEGER NOT NULL DEFAULT (strftime('%s', CURRENT_TIMESTAMP)),
    edited INTEGER NOT NULL DEFAULT 0,
    likes INTEGER NOT NULL DEFAULT 0,
    dislikes INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (status_id)
        REFERENCES status_reference (status_id)
            ON UPDATE CASCADE
            ON DELETE NO ACTION
) STRICT;

-- USER COMMENT JUNCTION TABLE

CREATE TABLE IF NOT EXISTS user_comment_junction (
    user_id INTEGER NOT NULL,
    comment_id INTEGER NOT NULL,
    PRIMARY KEY (user_id, comment_id),
    FOREIGN KEY (user_id)
        REFERENCES users_table (user_id)
            ON UPDATE CASCADE
            ON DELETE NO ACTION,
    FOREIGN KEY (comment_id)
        REFERENCES comments_table (comment_id)
            ON UPDATE CASCADE
            ON DELETE NO ACTION
);

COMMIT;

BEGIN;

INSERT INTO status_reference (status_id, "name", category)
VALUES (-1, 'missing', 'error_handling');

INSERT INTO permission_id (permission_id, "name")
VALUES (-1, 'missing');

INSERT INTO users_table (user_id, username, creation_timestamp, status_id, permission_id)
VALUES (-1, 'missing', 0, -1, -1);

.import --csv --skip 1 ./database/csv/comments_table.csv comments_table
.import --csv --skip 1 ./database/images_table.csv images_table
.import --csv --skip 1 ./database/permission_reference.csv permission_reference
.import --csv --skip 1 ./database/status_reference.csv status_reference
.import --csv --skip 1 ./database/tags_table.csv tags_table
.import --csv --skip 1 ./database/users_table.csv users_table

COMMIT;