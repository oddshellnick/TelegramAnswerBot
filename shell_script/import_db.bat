@echo off
:: username for MySQL server on your local machine.
set LOCAL_USERNAME=...

:: password for MySQL server on your local machine.
set LOCAL_PASSWORD=...

:: name of database which will be used to import to your local MySQL.
set DB_NAME=...

:: Create database.
mysql -u %LOCAL_USERNAME% --password="%LOCAL_PASSWORD%" -e "CREATE DATABASE IF NOT EXISTS %DB_NAME%;" || goto error

:: Import data.
mysql -u %LOCAL_USERNAME% --password="%LOCAL_PASSWORD%" %DB_NAME% < telegram_answer_bot.sql || goto error

echo Done.
goto end

:error
echo An error occurred.
goto end

:end
echo Script completed. Press Enter to exit.
pause > nul