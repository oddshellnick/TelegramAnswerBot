# TelegramAnswerBot

TelegramAnswerBot is a Telegram bot designed to manage Frequently Asked Questions (FAQ), handle user inquiries, and manage users with different roles.

## Key Features:

* **FAQ Management:**
    * Add new questions and answers to the FAQ.
    * Delete existing questions from the FAQ.
    * Edit questions and answers in the FAQ.
    * Clear the entire FAQ list.
    * Browse the FAQ with convenient page navigation.

* **User Question Management:**
    * Clear the history of all questions.
    * View question statistics (total count, processed/unprocessed count, average response time).
    * View a list of recent questions.

* **User and Role Management:**
    * Add roles to users.
    * Change user roles.
    * Delete user roles.
    * View statistics on users with roles (username, number of processed questions).

* **Question Interaction:**
    * Ask questions (available to users without a role).
    * Answer questions (available to users with roles).

* **Multilingual Support:** The bot supports 8 languages: Russian, English, German, French, Spanish, Italian, Portuguese, Chinese.

## Installation:

### MySQL Server:

You need a running MySQL server. You can download and install the MySQL Community Server from the [official MySQL website](https://dev.mysql.com/downloads/mysql/). Follow the instructions provided for your operating system. After installation, start the MySQL server.

### Python dependencies:

1. **Clone the repository:**

    ```bash
    git clone https://github.com/oddshellnick/TelegramAnswerBot
    ```

2. **Install the required Python packages using pip:**

    ```bash
    pip install -r requirements.txt
    ```

### Database Setup:

* **Manual:** Import the database schema from `shell_script/telegram_answer_bot.sql` into your MySQL database. You can do this using a MySQL client like MySQL Workbench or by running the SQL script directly from your MySQL server’s command line.
* **Automated (Windows):** Use the provided batch script `shell_script/import_db.bat`. **Before running the script, edit it and set the values for the variables at the beginning of the file.** This script automates the import process but requires proper configuration.
* **Automated (Linux):** Use the provided bash script `shell_script/import_db.sh`. **Before running the script, edit it and set the values for the variables at the beginning of the file.** This script automates the import process but requires proper configuration.

### Run the Program:

To run the bot, simply execute the main script. On the first run, the bot will automatically create the necessary files in the `bin` directory. After the initial run, you will need to populate them with your parameters. The bot will then inform you about which files need to be populated. Also, you have to create `.env` file in core project folder with "TELEGRAM_BOT_TOKEN" and "MySQL_PASSWORD" variables.

## Command Descriptions:

| Command                      | Description                                                                                                                                                                                 |
|------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Add FAQ Question**         | Adds a new question and answer to the FAQ. Follow the bot's instructions.                                                                                                                   |
| **Delete FAQ Question**      | Deletes a question from the FAQ by its ID (number in the list). Follow the bot's instructions.                                                                                              |
| **Edit FAQ Question**        | Modifies a question or answer in the FAQ by its ID. Choose what to change and follow the bot's instructions.                                                                                |
| **Clear FAQ**                | Clears the entire FAQ list. Requires confirmation.                                                                                                                                          |
| **View FAQ**                 | Displays the FAQ list. Navigate through pages using the « and » buttons. Click on a question to view the answer.                                                                            |
| **Clear Questions**          | Clears the entire history of user questions.                                                                                                                                                |
| **View Question Statistics** | Displays question statistics: total count, processed/unprocessed/in progress count, average response time.                                                                                  |
| **View Question List**       | Displays a specified number of recent questions.                                                                                                                                            |
| **Add Role**                 | Adds a role to a Telegram user. Only available to users with a higher role level.                                                                                                           |
| **Change Role**              | Changes the role of a Telegram user. Only available to users with a higher role level.                                                                                                      |
| **Delete Role**              | Deletes a role from a Telegram user. Only available to users with a higher role level.                                                                                                      |
| **View User Statistics**     | Displays statistics on users with roles: username and the number of processed questions.                                                                                                    |
| **Ask Question**             | Allows users without a role to ask a question. The question is saved anonymously. The answer will arrive as a reply or a new message if the original message with the question was deleted. |
| **Answer Question**          | Allows users with a role to answer a question from a user without a role. The answer is sent anonymously.                                                                                   |

## Roles and Access Levels:

| Role              | Description                                                                            | Level |
|-------------------|----------------------------------------------------------------------------------------|-------|
| **Developer**     | Full access to all bot functions. (Add Telegram @username on MySQL server).            | 3     |
| **Administrator** | Access to all functions except "Ask Question".                                         | 2     |
| **Moderator**     | Access to most functions, except "Ask Question", "Manage FAQ", and "Manage Questions". | 1     |
| **User**          | Access only to "Ask Question" and "View FAQ".                                          | 0     |

## Translation Feedback

The translations in this bot were generated using AI. If you are a native speaker of the supported languages (Russian, English, German, French, Spanish, Italian, Portuguese, Chinese), please provide feedback on the accuracy and naturalness of the translations. Your input will help improve the bot's multilingual capabilities.