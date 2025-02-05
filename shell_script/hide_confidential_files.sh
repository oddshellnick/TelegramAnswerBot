#!/bin/bash

echo "Removing cached files from Git..."

git rm --cached bin/mysql_config.json || {
  echo "Error removing bin/mysql_config.json"
  exit 1
}

echo "Files removed successfully."