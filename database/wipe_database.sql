.bail ON
.log "./logs/database_wipe.log"

BEGIN;

DROP TABLE IF EXISTS status_reference;
DROP TABLE IF EXISTS permission_reference;
DROP TABLE IF EXISTS users_table;
DROP TABLE IF EXISTS images_table;
DROP TABLE IF EXISTS tags_table;
DROP TABLE IF EXISTS image_tag_junction;
DROP TABLE IF EXISTS user_favourites_junction;
DROP TABLE IF EXISTS comments_table;
DROP TABLE IF EXISTS user_comment_junction;
DROP INDEX IF EXISTS indexed_image_datetime;

COMMIT;

VACUUM;
PRAGMA INTEGRITY_CHECK;