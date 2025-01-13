import json
import pandas
from telegram.ext import ContextTypes
from TelegramAnswerBot import (
	functions,
	objects_types
)
from TelegramAnswerBot.data_handlers.base import DataHandler


class UsersDataHandler(DataHandler):
	"""
    Manages user data stored in a database table named 'users'. Provides methods for adding, updating, and retrieving user information, including their roles and abilities.
    """
	
	def add_user_chat_id(self, username: str, chat_id: int):
		"""
        Updates a user's chat ID.

        Args:
            username (str): The username of the user to update.
            chat_id (int): The new chat ID for the user.
        """
		connection, cursor = self.get_attributes()
		
		cursor.execute(
				"""
                UPDATE
                    users
                SET
                    chat_id = %s
                WHERE
                    username = %s
                LIMIT 1
                """,
				(chat_id, username)
		)
		connection.commit()
		
		cursor.close()
		connection.close()
	
	def add_user(self, username: str, role: str):
		"""
        Adds a new user to the database.

        Args:
            username (str): The username of the new user.
            role (str): The role assigned to the user.
        """
		connection, cursor = self.get_attributes()
		
		cursor.execute(
				"""
                INSERT INTO
                    users (
                        username,
                        role,
                        user_context_data
                    )
                VALUES
                    (%s, %s, %s)
                """,
				(username, role, "{}")
		)
		connection.commit()
		
		cursor.close()
		connection.close()
	
	def change_user_role(self, username: str, role: str):
		"""
        Adds a new user to the database.

        Args:
            username (str): The username of the new user.
            role (str): The role assigned to the user.
        """
		connection, cursor = self.get_attributes()
		
		cursor.execute(
				"""
                SELECT
                    *
                FROM
                    users
                WHERE
                    username = %s
                """,
				(username,)
		)
		
		user = cursor.fetchone()
		
		if user[0]:
			cursor.execute(
					"""
                    UPDATE
                        users
                    SET
                        role = %s
                    WHERE
                        username = %s
                    LIMIT 1
                    """,
					(username, role)
			)
			connection.commit()
		else:
			self.add_user(username, role)
		
		cursor.close()
		connection.close()
	
	def create_table(self):
		"""
        Creates the 'faq' table if it doesn't exist.
        """
		connection, cursor = self.get_attributes()
		
		cursor.execute(
				"""
				CREATE TABLE IF NOT EXISTS roles (
					role_name VARCHAR(32) NOT NULL,
					role_level INTEGER NOT NULL,
					receives_messages TINYINT(1) NOT NULL,
					able_to_users_handle TINYINT(1) NOT NULL,
					able_to_users_view TINYINT(1) NOT NULL,
					able_to_faqs_handle TINYINT(1) NOT NULL,
					able_to_faqs_view TINYINT(1) NOT NULL,
					able_to_questions_handle TINYINT(1) NOT NULL,
					able_to_questions_view TINYINT(1) NOT NULL,
					able_to_ask TINYINT(1) NOT NULL,
					able_to_answer TINYINT(1) NOT NULL,
					PRIMARY KEY (`role_name`)
				)
				"""
		)
		connection.commit()
		
		cursor.execute(
				"""
				CREATE TABLE IF NOT EXISTS users (
					username VARCHAR(64) NOT NULL,
					role VARCHAR(32) NOT NULL,
					chat_id BIGINT DEFAULT NULL,
					user_context_data JSON NOT NULL,
					PRIMARY KEY (`username`),
					KEY `users_role` (`role`),
					CONSTRAINT `users_role` FOREIGN KEY (`role`) REFERENCES `roles` (`role_name`) ON DELETE CASCADE ON UPDATE CASCADE
				)
				"""
		)
		
		cursor.close()
		connection.close()
	
	def get_role_abilities(self, role_name: str) -> objects_types.RoleAbilitiesDict:
		"""
        Retrieves the abilities associated with a specific role.

        Args:
            role_name (str): The name of the role.

        Returns:
            objects_types.RoleAbilitiesDict: A dictionary where keys are ability names (e.g., "receives_messages", "able_to_users_handle") and values are booleans indicating whether the role has that ability.
        """
		connection, cursor = self.get_attributes()
		
		cursor.execute(
				f"""
                SELECT
                    receives_messages,
                    able_to_users_handle,
                    able_to_users_view,
                    able_to_faqs_handle,
                    able_to_faqs_view,
                    able_to_questions_handle,
                    able_to_questions_view,
                    able_to_ask,
                    able_to_answer
                FROM
                    roles
                WHERE
                    role_name = %s
                LIMIT 1
                """,
				(role_name,)
		)
		
		role_abilities = functions.get_db_line_dict([header[0] for header in cursor.description], [value == 1 for value in cursor.fetchone()])
		
		cursor.close()
		connection.close()
		
		return role_abilities
	
	def get_roles_by_priority(self, start_role: str, sign: str) -> list[str]:
		"""
        Retrieves roles based on their priority relative to a given `start_role`.

        Args:
            start_role (str): The reference role.
            sign (str):A comparison operator ("<" or ">") to determine the priority relative to `start_role`.

        Returns:
            list[str]: A list of role names that meet the specified priority criteria. Excludes the "user" role.
        """
		connection, cursor = self.get_attributes()
		
		cursor.execute(
				f"""
                SELECT
                    role_name
                FROM
                    roles
                WHERE
                    role_level {sign} (
                        SELECT role_level
                        FROM roles
                        WHERE role_name = %s
                    )
                    AND role_name != "user"
                """,
				(start_role,)
		)
		
		roles_by_priority = [row[0] for row in cursor.fetchall()]
		
		cursor.close()
		connection.close()
		
		return roles_by_priority
	
	def get_user_chat_id(self, username: str) -> int | None:
		"""
        Retrieves the chat ID associated with a specific username.

        Args:
            username (str): The username of the user.

        Returns:
            int | None: The user's chat ID, or None if no chat ID is found for the user.
        """
		connection, cursor = self.get_attributes()
		
		cursor.execute(
				"""
                SELECT
                    chat_id
                FROM
                    users
                WHERE
                    username = %s
                LIMIT 1
                """,
				(username,)
		)
		chat_id = cursor.fetchone()
		
		cursor.close()
		connection.close()
		
		return chat_id[0] if chat_id else None
	
	def get_user_data(self, username: str) -> objects_types.UserDataDict:
		"""
        Retrieves all data for a specific user.

        Args:
            username (str): The username of the user.

        Returns:
            objects_types.UserDataDict: A dictionary containing the user's data. The `user_context_data` field is parsed as a JSON object. Returns an empty dictionary if the user is not found.
        """
		connection, cursor = self.get_attributes()
		
		cursor.execute(
				"""
                SELECT
                    *
                FROM
                    users
                WHERE
                    username = %s
                LIMIT 1
                """,
				(username,)
		)
		
		user_data = functions.get_db_line_dict([header[0] for header in cursor.description], cursor.fetchone())
		user_data["user_context_data"] = json.loads(user_data["user_context_data"])
		
		cursor.close()
		connection.close()
		
		return user_data
	
	def get_user_language(self, username: str) -> str | None:
		"""
        Retrieves the language of a specific user.

        Args:
            username (str): The username of the user.

        Returns:
            str | None: The user's language. Returns None if the user is not found or doesn't have a language assigned.
        """
		connection, cursor = self.get_attributes()
		
		cursor.execute(
				"""
                SELECT
                    language
                FROM
                    users
                WHERE
                    username = %s
                LIMIT 1
                """,
				(username,)
		)
		language = cursor.fetchone()
		
		cursor.close()
		connection.close()
		
		return language[0] if language else None
	
	def get_user_role(self, username: str) -> tuple[str, bool]:
		"""
        Retrieves the role of a specific user.

        Args:
            username (str): The username of the user.

        Returns:
            tuple[str, bool]: The user's role. Returns "user" if the user is not found or doesn't have a role assigned.
        """
		connection, cursor = self.get_attributes()
		
		cursor.execute(
				"""
                SELECT
                    role
                FROM
                    users
                WHERE
                    username = %s
                LIMIT 1
                """,
				(username,)
		)
		role = cursor.fetchone()
		
		cursor.close()
		connection.close()
		
		return (role[0], True) if role else ("user", False)
	
	def get_users_chats_receiving_messages(self) -> list[int]:
		"""
        Retrieves a list of chat IDs for users who have a chat ID set (presumably indicating they should receive messages) and resets their `user_context_data`.

        Returns:
            list[int]: A list of chat IDs.
        """
		connection, cursor = self.get_attributes()
		
		cursor.execute(
				"""
                SELECT
                    chat_id
                FROM
                    users
                WHERE
                    chat_id IS NOT NULL
                FOR UPDATE
                """
		)
		
		users_chats_receiving_messages = [row[0] for row in cursor.fetchall()]
		
		cursor.execute(
				"""
                UPDATE
                    users
                SET
                    user_context_data = "{}"
                WHERE
                    chat_id IS NOT NULL
                """
		)
		connection.commit()
		
		cursor.close()
		connection.close()
		
		return users_chats_receiving_messages
	
	def get_users_data(self) -> pandas.DataFrame:
		"""
        Retrieves data for all users, including their roles and role levels.

        Returns:
           pandas.DataFrame: A Pandas DataFrame containing user data.
        """
		connection, cursor = self.get_attributes()
		
		cursor.execute(
				"""
                SELECT
                    *
                FROM
                    users
                JOIN
                    roles
                ON
                    users.role = roles.role_name
                ORDER BY
                    roles.role_level DESC,
                    users.username ASC
                """
		)
		
		users_data = functions.get_db_data_frame([header[0] for header in cursor.description], cursor.fetchall())
		
		cursor.close()
		connection.close()
		
		return users_data
	
	def remove_user(self, username: str):
		"""
        Removes a user from the database.

        Args:
            username (str): The username of the user to remove.
        """
		connection, cursor = self.get_attributes()
		
		cursor.execute(
				"""
                DELETE FROM users
                WHERE
                    username = %s
                LIMIT 1
                """,
				(username,)
		)
		connection.commit()
		
		cursor.close()
		connection.close()
	
	def update_language(self, username: str, language: str, context: ContextTypes.DEFAULT_TYPE):
		"""
        Updates a user's last recorded state, message ID, and context data in the database.

        Args:
            username (str): The username of the user to update.
            language (str): The user's last state.
            context (ContextTypes.DEFAULT_TYPE): The Telegram bot context.
        """
		connection, cursor = self.get_attributes()
		
		context.user_data["language"] = language
		
		cursor.execute(
				"""
                UPDATE
                    users
                SET
                    language = %s
                WHERE
                    username = %s
                LIMIT 1
                """,
				(language, username)
		)
		connection.commit()
		
		cursor.close()
		connection.close()
	
	def update_last_state(
			self,
			username: str,
			last_state: str,
			last_message_id: int | None,
			context: ContextTypes.DEFAULT_TYPE
	):
		"""
        Updates a user's last recorded state, message ID, and context data in the database.

        Args:
            username (str): The username of the user to update.
            last_state (str): The user's last state.
            last_message_id (int | None): The ID of the last message.
            context (ContextTypes.DEFAULT_TYPE): The Telegram bot context.
        """
		connection, cursor = self.get_attributes()
		
		context.user_data["current_state"] = (last_state, last_message_id)
		
		cursor.execute(
				"""
                UPDATE
                    users
                SET
                    user_context_data = %s
                WHERE
                    username = %s
                LIMIT 1
                """,
				(
						json.dumps(
								{
									"current_state": context.user_data["current_state"],
									"temp": context.user_data.get("temp", {}),
									"processing": context.user_data.get("processing", False)
								}
						),
						username
				)
		)
		connection.commit()
		
		cursor.close()
		connection.close()
