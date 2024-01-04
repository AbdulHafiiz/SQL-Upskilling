.eqp ON
.echo ON
.bail ON
.timer ON
.log "./logs/data_import_p3.log"

BEGIN;

.import --csv ./database/csv/image_tag_junction.csv image_tag_junction
.import --csv ./database/csv/user_comment_junction.csv user_comment_junction
.import --csv ./database/csv/user_favourites_junction.csv user_favourites_junction

COMMIT;