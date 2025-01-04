import mysql.connector
from objects_types import MySQL_PoolConfigDict
from data_handlers.FAQs import FAQs_DataHandler
from data_handlers.users import UsersDataHandler
from mysql.connector.pooling import MySQLConnectionPool
from data_handlers.questions import QuestionsDataHandler


class MySQLDataHandler:
    """
    Manages database interactions using a MySQL connection pool. Serves as a central point of access for different data handlers (Users, FAQs, Questions).

    Attributes:
        connection_pool (MySQLConnectionPool): The MySQL connection pool.
        users_data (UsersDataHandler): The handler for user-related data.
        faqs_data (FAQs_DataHandler): The handler for FAQ-related data.
        questions_data (QuestionsDataHandler): The handler for question-related data.

    :Usage:
         # Example usage (replace with your actual database credentials):
        pool_config = {
            "user": "your_user",
            "password": "your_password",
            "host": "your_host",
            "database": "your_database",
            "pool_size": 5 # Adjust pool size as needed
        }

        mysql_handler = MySQLDataHandler(pool_config)

        # Access data handlers:
        user_data = mysql_handler.users_data.get_user_data("some_username")
        faqs = mysql_handler.faqs_data.get_faq(1)
        # ... etc. ...
    """

    def __init__(self, users_data_pool_config: MySQL_PoolConfigDict):
        """
        Initializes the MySQLDataHandler with a connection pool and creates instances of the individual data handlers.

        Args:
            users_data_pool_config (MySQL_PoolConfigDict): Configuration parameters for the MySQL connection pool.
        """
        self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(**users_data_pool_config)
        self.users_data = UsersDataHandler(self.connection_pool)
        self.faqs_data = FAQs_DataHandler(self.connection_pool)
        self.questions_data = QuestionsDataHandler(self.connection_pool)
