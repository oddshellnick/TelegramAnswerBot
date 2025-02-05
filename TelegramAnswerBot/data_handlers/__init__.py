import mysql.connector
from mysql.connector.pooling import MySQLConnectionPool
from TelegramAnswerBot.objects_types import MySQL_ConfigDict
from TelegramAnswerBot.data_handlers.FAQs import FAQs_DataHandler
from TelegramAnswerBot.data_handlers.users import UsersDataHandler
from TelegramAnswerBot.data_handlers.questions import QuestionsDataHandler


class MySQLDataHandler:
	"""
    Manages database interactions using a MySQL connection pool. Serves as a central point of access for different data handlers (Users, FAQs, Questions).

    Attributes:
        connection_pool (MySQLConnectionPool): The MySQL connection pool.
        users_data (UsersDataHandler): The handler for user-related data.
        faqs_data (FAQs_DataHandler): The handler for FAQ-related data.
        questions_data (QuestionsDataHandler): The handler for question-related data.
    """
	
	def __init__(self, users_data_pool_config: MySQL_ConfigDict):
		"""
        Initializes the MySQLDataHandler with a connection pool and creates instances of the individual data handlers.

        Args:
            users_data_pool_config (MySQL_ConfigDict): Configuration parameters for the MySQL connection pool.
        """
		self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(**users_data_pool_config)
		self.users_data = UsersDataHandler(self.connection_pool)
		self.faqs_data = FAQs_DataHandler(self.connection_pool)
		self.questions_data = QuestionsDataHandler(self.connection_pool)
