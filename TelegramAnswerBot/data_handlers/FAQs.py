from TelegramAnswerBot import (
	functions,
	objects_types
)
from TelegramAnswerBot.data_handlers.base import DataHandler


class FAQs_DataHandler(DataHandler):
	"""
    Manages Frequently Asked Questions (FAQs) stored in a database table named 'faq'. Provides methods for adding, modifying, retrieving, and deleting FAQs.
    """
	
	def add_faq(self, question: str, answer: str) -> int:
		"""
        Adds a new FAQ to the database.

        Args:
            question (str): The question text.
            answer (str): The answer text.

        Returns:
            int: The ID of the newly added FAQ.
        """
		connection, cursor = self.get_attributes()
		
		cursor.execute(
				"""
                INSERT INTO
                    faq (
                        question,
                        answer
                    )
                VALUES
                    (%s, %s)
                """,
				(question, answer)
		)
		connection.commit()
		
		last_id = cursor.lastrowid
		
		cursor.close()
		connection.close()
		
		return last_id
	
	def change_fag_answer(self, faq_id: int, answer_text: str):
		"""
        Updates a specific attribute (instance) of an FAQ.

        Args:
            faq_id (int): The ID of the FAQ to update.
            answer_text (str): The new value for the answer.
        """
		connection, cursor = self.get_attributes()
		
		cursor.execute(
				"""
                UPDATE
                    faq
                SET
                    answer = %s
                WHERE
                    faq_id = %s
                LIMIT 1
                """,
				(answer_text, faq_id)
		)
		connection.commit()
		
		cursor.close()
		connection.close()
	
	def change_fag_question(self, faq_id: int, question_text: str):
		"""
        Updates a specific attribute (instance) of an FAQ.

        Args:
            faq_id (int): The ID of the FAQ to update.
            question_text (str): The new value for the question.
        """
		connection, cursor = self.get_attributes()
		
		cursor.execute(
				"""
                UPDATE
                    faq
                SET
                    question = %s
                WHERE
                    faq_id = %s
                LIMIT 1
                """,
				(question_text, faq_id)
		)
		connection.commit()
		
		cursor.close()
		connection.close()
	
	def check_faq_exists(self, faq_id: int) -> bool:
		"""
        Checks if an FAQ with the given ID exists.

        Args:
            faq_id (int): The ID of the FAQ to check.

        Returns:
            bool: True if the FAQ exists, False otherwise.
        """
		connection, cursor = self.get_attributes()
		
		cursor.execute(
				"""
                SELECT
                    COUNT(*)
                FROM
                    faq
                WHERE
                    faq_id = %s
                LIMIT 1
                """,
				(faq_id,)
		)
		
		faq_exists = cursor.fetchone()[0] != 0
		
		cursor.close()
		connection.close()
		
		return faq_exists
	
	def clear_faqs(self):
		"""
        Deletes all FAQs from the database and resets the auto-increment counter. Use with caution!
        """
		connection, cursor = self.get_attributes()
		
		cursor.execute("DELETE FROM faq")
		cursor.execute("ALTER TABLE faq AUTO_INCREMENT = 1")
		connection.commit()
		
		cursor.close()
		connection.close()
	
	def create_table(self):
		"""
        Creates the 'faq' table if it doesn't exist.
        """
		connection, cursor = self.get_attributes()
		
		cursor.execute(
				"""
            CREATE TABLE IF NOT EXISTS faq (
                faq_id INTEGER AUTO_INCREMENT,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                views_count INTEGER DEFAULT 0,
                PRIMARY KEY (`faq_id`)
            )
            """
		)
		connection.commit()
		
		cursor.close()
		connection.close()
	
	def delete_faq(self, faq_id: int):
		"""
        Deletes a specific FAQ from the database. Also attempts to re-sequence faq_id values – This logic is flawed and prone to race conditions. It's generally not advisable to manually manipulate auto-incrementing IDs like this.
        Args:
            faq_id (int): The ID of the FAQ to delete.
        """
		connection, cursor = self.get_attributes()
		
		cursor.execute(
				"""
                DELETE FROM faq
                WHERE
                    faq_id = %s
                LIMIT 1
                """,
				(faq_id,)
		)
		cursor.execute(
				"""
                UPDATE
                    faq
                SET
                    faq_id = faq_id - 1
                WHERE
                    faq_id > %s
                LIMIT 1
                """,
				(faq_id,)
		)
		connection.commit()
		
		cursor.close()
		connection.close()
	
	def get_faq(self, faq_id: int) -> objects_types.FAQ_Dict:
		"""
        Retrieves a specific FAQ from the database and increments its view count.

        Args:
            faq_id (int): The ID of the FAQ to retrieve.

        Returns:
            objects_types.FAQ_Dict: A dictionary representing the FAQ data. Returns an empty dictionary if no FAQ with the given ID is found.
        """
		connection, cursor = self.get_attributes()
		
		cursor.execute(
				"""
                SELECT
                    *
                FROM
                    faq
                WHERE
                    faq_id = %s
                LIMIT 1
                FOR UPDATE
                """,
				(faq_id,)
		)
		
		faq = functions.get_db_line_dict([header[0] for header in cursor.description], cursor.fetchone())
		
		if faq:
			cursor.execute(
					"""
                    UPDATE
                        faq
                    SET
                        views_count = views_count + 1
                    WHERE
                        faq_id = %s
                    LIMIT 1
                    """,
					(faq_id,)
			)
			connection.commit()
		
			faq["views_count"] += 1
		
		cursor.close()
		connection.close()
		
		return faq
	
	def get_faq_group(self, faq_group_size: int, faq_group: int):
		"""
        Retrieves a group of FAQs. The logic for calculating the offset appears incorrect (multiplies by 9, unclear why).

        Args:
            faq_group_size (int): The number of FAQs to retrieve in each group.
            faq_group (int): The group number (starting from 0). The offset is calculated by multiplying this by 9. This calculation needs review.

        Returns:
           pandas.DataFrame: A Pandas DataFrame containing the FAQs in the specified group.
        """
		connection, cursor = self.get_attributes()
		
		cursor.execute(
				"""
                SELECT
                    faq_id,
                    question
                FROM
                    faq
                LIMIT %s
                OFFSET %s
                """,
				(faq_group_size, faq_group * 9,)
		)
		
		faq_group = functions.get_db_data_frame([header[0] for header in cursor.description], cursor.fetchall())
		
		cursor.close()
		connection.close()
		
		return faq_group
	
	def get_total_faqs_count(self) -> int:
		"""
        Retrieves the total number of FAQs in the database.

        Returns:
            int: The total count of FAQs.
        """
		connection, cursor = self.get_attributes()
		
		cursor.execute(
				"""
                SELECT
                    COUNT(*)
                FROM
                    faq
                """
		)
		total_faqs_count = cursor.fetchone()[0]
		
		cursor.close()
		connection.close()
		
		return total_faqs_count
