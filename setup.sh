#!/bin/bash

# https://stackoverflow.com/questions/20095351/shebang-use-interpreter-relative-to-the-script-path
# https://unix.stackexchange.com/questions/17499/get-path-of-current-script-when-executed-through-a-symlink


# sqlite3 ./database/website_database.db < ./database/setup/setup_database.sql
# sqlite3 ./database/website_database.db < ./database/setup/import_data_p1.sql
./database/setup/import_data_p2.py
# sqlite3 ./database/website_database.db < ./database/setup/import_data_p3.sql
