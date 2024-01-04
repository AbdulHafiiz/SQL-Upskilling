.bail ON
.log "./logs/data_import_p1.log"

BEGIN;

INSERT INTO status_reference (status_id, "name", category)
VALUES (-1, 'missing', 'error_handling');

INSERT INTO permission_reference (permission_id, "name")
VALUES (-1, 'missing');

INSERT INTO users_table (user_id, username, creation_timestamp, status_id, permission_id)
VALUES (-1, 'missing', 0, -1, -1);

.import --csv --skip 1 ./database/csv/status_reference.csv status_reference
.import --csv --skip 1 ./database/csv/permission_reference.csv permission_reference
.import --csv --skip 1 ./database/csv/tags_table.csv tags_table
.import --csv --skip 1 ./database/csv/users_table.csv users_table
.import --csv --skip 1 ./database/csv/comments_table.csv comments_table

COMMIT;