.eqp ON
.echo ON
.bail ON
.timer ON
.log "./logs/data_import_p3.log"

BEGIN;

.import --csv --skip 1 ./database/csv/image_tag_junction.csv image_tag_junction
.import --csv --skip 1 ./database/csv/user_comment_junction.csv user_comment_junction
.import --csv --skip 1 ./database/csv/user_favourites_junction.csv user_favourites_junction

COMMIT;