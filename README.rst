TelegramAnswerBot
=================

TelegramAnswerBot is a Telegram bot designed to manage Frequently Asked Questions (FAQ), handle user inquiries, and manage users with different roles.

Key Features:
-------------

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


Command Descriptions:
---------------------

.. list-table::
   :widths: 20 80
   :header-rows: 1

   * - Command
     - Description
   * - **Add FAQ Question**
     - Adds a new question and answer to the FAQ. Follow the bot's instructions.
   * - **Delete FAQ Question**
     - Deletes a question from the FAQ by its ID (number in the list). Follow the bot's instructions.
   * - **Edit FAQ Question**
     - Modifies a question or answer in the FAQ by its ID. Choose what to change and follow the bot's instructions.
   * - **Clear FAQ**
     - Clears the entire FAQ list. Requires confirmation.
   * - **View FAQ**
     - Displays the FAQ list. Navigate through pages using the « and » buttons. Click on a question to view the answer.
   * - **Clear Questions**
     - Clears the entire history of user questions.
   * - **View Question Statistics**
     - Displays question statistics: total count, processed/unprocessed/in progress count, average response time.
   * - **View Question List**
     - Displays a specified number of recent questions.
   * - **Add Role**
     - Adds a role to a Telegram user. Only available to users with a higher role level.
   * - **Change Role**
     - Changes the role of a Telegram user. Only available to users with a higher role level.
   * - **Delete Role**
     - Deletes a role from a Telegram user. Only available to users with a higher role level.
   * - **View User Statistics**
     - Displays statistics on users with roles: username and the number of processed questions.
   * - **Ask Question**
     - Allows users without a role to ask a question. The question is saved anonymously. The answer will arrive as a reply or a new message if the original message with the question was deleted.
   * - **Answer Question**
     - Allows users with a role to answer a question from a user without a role. The answer is sent anonymously.


Roles and Access Levels:
------------------------

.. list-table::
   :widths: 20 60 20
   :header-rows: 1

   * - Role
     - Description
     - Level
   * - **Developer**
     - Full access to all bot functions. (Add Telegram @username on MySQL server).
     - 3
   * - **Administrator**
     - Access to all functions except "Ask Question".
     - 2
   * - **Moderator**
     - Access to most functions, except "Ask Question", "Manage FAQ", and "Manage Questions".
     - 1
   * - **User**
     - Access only to "Ask Question" and "View FAQ".
     - 0

Installation and Setup:
-----------------------

* **Install Dependencies:** Install the required Python packages using pip:

.. code-block:: bash

   pip install -r requirements.txt

* **Run the Program:** Execute the program. This will create necessary files for storing configuration information, including ``bin/auth_data.json`` and ``bin/doc.txt``. The list of created files will be printed to the console. You will then need to populate these files with your configuration details as needed.