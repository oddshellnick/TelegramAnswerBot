import pandas
import mysql.connector
from TelegramAnswerBot import (
	functions,
	objects_types
)
from TelegramAnswerBot.data_handlers.base import DataHandler


class QuestionsDataHandler(DataHandler):
	"""
    Manages the 'questions' table in the database, inheriting basic functionality from `DataHandler`. This class provides methods for creating the table and adding new questions.

    Attributes:
        connection_pool (mysql.connector.pooling.MySQLConnectionPool): Inherited from DataHandler.
        time_for_answer (int):Time allowed for answering a question (in seconds, presumably). Currently unused.

    :Usage:
        # Assuming 'pool' is a pre-existing MySQLConnectionPool instance
        questions_handler = QuestionsDataHandler(pool)

        # Add a question:
        questions_handler.add_question(123, 456, 789, "some_username", "First", "Last", "What's the meaning of life?")
    """
	
	def __init__(self, connection_pool: mysql.connector.pooling.MySQLConnectionPool):
		"""
        Initializes the QuestionsDataHandler, calling the parent class initializer and setting the `time_for_answer`.

        Args:
            connection_pool (mysql.connector.pooling.MySQLConnectionPool):The connection pool for database access.
        """
		super().__init__(connection_pool)
		
		self.time_for_answer = 120
	
	def add_question(
			self,
			user_id: int,
			chat_id: int,
			message_id: int,
			username: str,
			first_name: str,
			last_name: str,
			question: str
	):
		"""
        Adds a new question to the 'questions' table.

        Args:
            user_id (int): The ID of the user who asked the question.
            chat_id (int): The ID of the chat where the question was asked.
            message_id (int): The ID of the message containing the question.
            username (str): The username of the user.
            first_name (str): The first name of the user.
            last_name (str): The last name of the user.
            question (str): The text of the question.
        """
		connection, cursor = self.get_attributes()
		
		cursor.execute(
				"""
            INSERT INTO
                questions (
                    user_id,
                    chat_id,
                    message_id,
                    username,
                    first_name,
                    last_name,
                    question
                )
            VALUES
                (%s, %s, %s, %s, %s, %s, %s)
            """,
				(
						user_id,
						chat_id,
						message_id,
						username,
						first_name,
						last_name,
						question
				)
		)
		connection.commit()
		
		cursor.close()
		connection.close()
	
	def check_question_reservation(self, question_id: int, moderator_username: str) -> objects_types.QuestionDict:
		"""
        Checks if a specific question is reserved by a particular moderator.

        Args:
            question_id (int): The ID of the question to check.
            moderator_username (str): The username of the moderator to check against.

        Returns:
            objects_types.QuestionDict: A dictionary representing the question data if the question is reserved by the specified moderator and its status is "processing". Returns an empty dictionary if no such reservation exists.
        """
		connection, cursor = self.get_attributes()
		
		cursor.execute(
				"""
            SELECT
                *
            FROM
                questions
            WHERE
                question_id = %s
                AND status = "processing"
                AND moderator_username = %s
            LIMIT 1
            """,
				(question_id, moderator_username)
		)
		
		question_reservation = objects_types.QuestionDict(
				**functions.get_db_line_dict([header[0] for header in cursor.description], cursor.fetchone())
		)
		
		cursor.close()
		connection.close()
		
		return question_reservation
	
	def clear_questions_data(self):
		"""
        Clears all data from the 'questions' table and resets the auto-increment counter. Use with caution!
        """
		connection, cursor = self.get_attributes()
		
		cursor.execute("DELETE FROM questions")
		cursor.execute("ALTER TABLE questions AUTO_INCREMENT = 1")
		connection.commit()
		
		cursor.close()
		connection.close()
	
	def create_table(self):
		"""
        Creates the 'questions' table if it doesn't exist. Also resets the status of any questions marked as 'processing' to 'unprocessed'.
        """
		connection, cursor = self.get_attributes()
		
		cursor.execute(
				"""
            CREATE TABLE IF NOT EXISTS questions (
                question_id INTEGER AUTO_INCREMENT,
                user_id BIGINT NOT NULL,
                chat_id BIGINT NOT NULL,
                message_id BIGINT NOT NULL,
                username VARCHAR(64),
                first_name VARCHAR(64),
                last_name VARCHAR(64),
                question TEXT NOT NULL,
                asked_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                answered_date TIMESTAMP DEFAULT NULL,
                status VARCHAR(32) NOT NULL DEFAULT "unprocessed",
                moderator_username VARCHAR(64),
                PRIMARY KEY (`question_id`)
            )
            """
		)
		cursor.execute(
				"""
            UPDATE
                questions
            SET
                status = "unprocessed",
                answered_date = NULL,
                moderator_username = NULL
            WHERE
                status = 'processing'
            """
		)
		connection.commit()
		
		cursor.close()
		connection.close()
	
	def free_question_from_moderator(self, question_id: int):
		"""
        Releases a question from a moderator's reservation. Sets the `answered_date` to NULL, the `status` to "unprocessed", and clears the `moderator_username`.

        Args:
            question_id (int): The ID of the question to release.
        """
		connection, cursor = self.get_attributes()
		
		cursor.execute(
				"""
            UPDATE
                questions
            SET
                answered_date = NULL,
                status = "unprocessed",
                moderator_username = NULL
            WHERE
                question_id = %s
            LIMIT 1
            """,
				(question_id,)
		)
		connection.commit()
		
		cursor.close()
		connection.close()
	
	def get_average_answer_time(self) -> float:
		"""
        Calculates and returns the average time taken to answer questions (in seconds).

        Returns:
            float: The average answer time in seconds. Returns NaN (Not a Number) if no answered questions are found.
        """
		connection, cursor = self.get_attributes()
		
		cursor.execute(
				"""
                SELECT
                    TIMESTAMPDIFF(SECOND, asked_date, answered_date) AS time_difference
                FROM
                    questions
                WHERE
                    answered_date IS NOT NULL
                    AND asked_date IS NOT NULL
                    AND status = "processed"
                """
		)
		
		average_answer_time = functions.get_db_data_frame([header[0] for header in cursor.description], cursor.fetchall())["time_difference"].mean()
		
		cursor.close()
		connection.close()
		
		return average_answer_time
	
	def get_first_unanswered_question(self, declined_questions: list[int]) -> objects_types.QuestionDict:
		"""
        Retrieves the first unanswered question from the database, excluding questions specified in `declined_questions`.

        Args:
            declined_questions (list[int], optional): A list of question IDs to exclude from the search. Defaults to None.

        Returns:
            objects_types.QuestionDict: A dictionary representing the first unanswered question found. Returns an empty dictionary if no unanswered questions are found. A question is considered unanswered if its status is "unprocessed" or if it's marked as "processing" but the `answered_date` is older than `self.time_for_answer` seconds.
        """
		connection = self.connection_pool.get_connection()
		cursor = connection.cursor()
		
		if declined_questions:
			cursor.execute(
					f"""
                    SELECT
                        *
                    FROM
                        questions
                    WHERE
                        (
                            status = "unprocessed"
                            OR (
                                status = "processing"
                                AND answered_date IS NOT NULL
                                AND TIMESTAMPDIFF(SECOND, answered_date, CURRENT_TIMESTAMP) >= {self.time_for_answer}
                            )
                        )
                        AND question_id NOT IN ({", ".join(["%s" for _ in declined_questions])})
                    LIMIT 1
                    """,
					(*declined_questions,)
			)
		else:
			cursor.execute(
					f"""
                    SELECT
                        *
                    FROM
                        questions
                    WHERE
                        status = "unprocessed"
                        OR (
                            status = "processing"
                            AND answered_date IS NOT NULL
                            AND TIMESTAMPDIFF(SECOND, answered_date, CURRENT_TIMESTAMP) >= {self.time_for_answer}
                        )
                    LIMIT 1
                    """
			)
		
		first_unanswered_question = objects_types.QuestionDict(
				**functions.get_db_line_dict([header[0] for header in cursor.description], cursor.fetchone())
		)
		
		cursor.close()
		connection.close()
		
		return first_unanswered_question
	
	def get_questions_stats(self) -> objects_types.QuestionStatsDict:
		"""
        Retrieves statistics about the questions in the database.

        Returns:
            objects_types.QuestionStatsDict: A dictionary containing the questions statistics.
        """
		connection, cursor = self.get_attributes()
		
		cursor.execute(
				f"""
                SELECT
                    (
                        SELECT
                            COUNT(*)
                        FROM
                            questions
                    ) AS total_questions,
                    (
                        SELECT
                            COUNT(*)
                        FROM
                            questions
                        WHERE
                            status = "unprocessed"
                            OR (
                                status = "processing"
                                AND answered_date IS NOT NULL
                                AND TIMESTAMPDIFF(SECOND, answered_date, CURRENT_TIMESTAMP) >= {self.time_for_answer}
                            )
                    ) AS unanswered_questions,
                    (
                        SELECT
                            COUNT(*)
                        FROM
                            questions
                        WHERE
                            status = "processing"
                            AND answered_date IS NOT NULL
                            AND TIMESTAMPDIFF(SECOND, answered_date, CURRENT_TIMESTAMP) < {self.time_for_answer}
                    ) AS processing_questions,
                    (
                        SELECT
                            COUNT(*)
                        FROM
                            questions
                        WHERE
                            status = "processed"
                    ) AS answered_questions;
                """
		)
		
		questions_stats = objects_types.QuestionStatsDict(
				**functions.get_db_line_dict([header[0] for header in cursor.description], cursor.fetchone())
		)
		
		cursor.close()
		connection.close()
		
		return questions_stats
	
	def get_questions_text_list(self, number_of_questions: int = None) -> list[str]:
		"""
        Retrieves a list of question texts from the database.

        Args:
            number_of_questions (int, optional): The maximum number of questions to retrieve. If None, retrieves all questions. Defaults to None.

        Returns:
            list[str]: A list of strings, where each string is the text of a question.
        """
		connection, cursor = self.get_attributes()
		
		if number_of_questions is None:
			cursor.execute(
					"""
                    SELECT
                        question
                    FROM
                        questions
                    ORDER BY
                        question_id DESC
                    """
			)
		else:
			cursor.execute(
					"""
                    SELECT
                        question
                    FROM
                        questions
                    ORDER BY
                        question_id DESC
                    LIMIT %s
                    """,
					(number_of_questions,)
			)
		
		questions_text_list = [row[0] for row in cursor.fetchall()]
		
		cursor.close()
		connection.close()
		
		return questions_text_list
	
	def get_total_questions_count(self) -> int:
		"""
        Retrieves the total number of questions in the database.

        Returns:
            int: The total count of questions.
        """
		connection, cursor = self.get_attributes()
		
		cursor.execute(
				"""
                SELECT
                    COUNT(*)
                FROM
                    questions
                """
		)
		total_questions_count = cursor.fetchone()[0]
		
		cursor.close()
		connection.close()
		
		return total_questions_count
	
	def get_users_statistics(self) -> pandas.DataFrame:
		"""
        Retrieves statistics about moderators and the number of questions they have answered.

        Returns:
            pandas.DataFrame: A DataFrame with "moderator_usernames" and "count_questions" they've answered columns.
        """
		connection, cursor = self.get_attributes()
		
		cursor.execute(
				"""
                SELECT
                    moderator_username,
                    COUNT(*) AS count_questions
                FROM
                    questions
                WHERE
                    moderator_username IS NOT NULL
                    AND status = "processed"
                GROUP BY
                    moderator_username
                ORDER BY
                    count_questions DESC
                """
		)
		
		users_statistics = functions.get_db_data_frame([header[0] for header in cursor.description], cursor.fetchall())
		
		cursor.close()
		connection.close()
		
		return users_statistics
	
	def mark_question_as_answered(self, question_id: int):
		"""
        Marks a question as answered by updating its status to "processed" (processed) and setting the `answered_date` to the current timestamp.

        Args:
            question_id (int): The ID of the question to mark as answered.
        """
		connection, cursor = self.get_attributes()
		
		cursor.execute(
				"""
                UPDATE
                    questions
                SET
                    status = "processed",
                    answered_date = CURRENT_TIMESTAMP
                WHERE
                    question_id = %s
                LIMIT 1
                """,
				(question_id,)
		)
		connection.commit()
		
		cursor.close()
		connection.close()
	
	def reserve_question_for_moderator(self, moderator_username: str, question_id: int):
		"""
        Reserves a question for a specific moderator. Sets the `answered_date` to the current timestamp (which seems unusual for a reservation), the `status` to "processing", and the `moderator_username`.

        Args:
            moderator_username (str): The username of the moderator reserving the question.
            question_id (int): The ID of the question to reserve.
        """
		connection, cursor = self.get_attributes()
		
		cursor.execute(
				"""
                UPDATE
                    questions
                SET
                    answered_date = CURRENT_TIMESTAMP,
                    status = "processing",
                    moderator_username = %s
                WHERE
                    question_id = %s
                LIMIT 1
                """,
				(moderator_username, question_id)
		)
		connection.commit()
		
		cursor.close()
		connection.close()
