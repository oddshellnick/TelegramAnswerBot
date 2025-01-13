#!/bin/bash

echo "Removing cached files from Git..."

git rm --cached bin/settings.json || {
  echo "Error removing bin/settings.json"
  exit 1
}

echo "Files removed successfully."