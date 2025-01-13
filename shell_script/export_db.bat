@echo off
:: username for MySQL server on your local machine.
set LOCAL_USERNAME=...

:: password for MySQL server on your local machine.
set LOCAL_PASSWORD=...

:: schema name on MySQL server on your local machine.
set LOCAL_DB_NAME=...

:: Export tables with data.
mysqldump -u %LOCAL_USERNAME% --password=%LOCAL_PASSWORD% %LOCAL_DB_NAME% roles > tables_with_data.sql || goto error

:: Export tables without data.
mysqldump -u %LOCAL_USERNAME% --password=%LOCAL_PASSWORD% %LOCAL_DB_NAME% --no-data questions users faq > tables_without_data.sql || goto error

:: Export tables without data.
type tables_with_data.sql tables_without_data.sql > telegram_answer_bot.sql || goto error

:: Cut mysqldump warning from telegram_answer_bot.sql
sed "s/mysqldump: \[Warning] Using a password on the command line interface can be insecure.//g" telegram_answer_bot.sql > temp.sql
move /y temp.sql telegram_answer_bot.sql

:: Replace source schema name in telegram_answer_bot.sql
sed "s/%LOCAL_DB_NAME%/telegram_answer_bot/g" telegram_answer_bot.sql > temp.sql
move /y temp.sql telegram_answer_bot.sql

:: Cut AUTO_INCREMENT from telegram_answer_bot.sql
sed "s/AUTO_INCREMENT=[0-9]\+ *//g" telegram_answer_bot.sql > temp.sql
move /y temp.sql telegram_answer_bot.sql

del /f /q tables_with_data.sql
del /f /q tables_without_data.sql

echo Done.
goto end

:error
echo An error occurred.
goto end

:end
echo Script completed. Press Enter to exit.
pause > nul