@echo off
echo Removing cached files from Git...

git rm --cached bin/mysql_config.json || (
  echo Error removing bin/mysql_config.json
  exit /b 1
)

echo Files removed successfully.