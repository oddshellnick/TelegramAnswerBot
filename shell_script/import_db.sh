#!/bin/bash

# username for MySQL server on your local machine.
LOCAL_USERNAME=...

# password for MySQL server on your local machine.
LOCAL_PASSWORD=...

# name of database which will be used to import to your local MySQL.
DB_NAME=...

# Create database.
mysql -u "$LOCAL_USERNAME" --password="$LOCAL_PASSWORD" -e "CREATE DATABASE IF NOT EXISTS $DB_NAME;" || exit 1

# Import data.
mysql -u "$LOCAL_USERNAME" --password="$LOCAL_PASSWORD" "$DB_NAME" < telegram_answer_bot.sql || exit 1

echo "Done."
exit 0