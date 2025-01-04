import typing
import datetime
from telegram import Update
from telegram.ext import ContextTypes


class UserDataDict(typing.TypedDict):
    """
    Represents the data structure for a user.

    Attributes:
        username (str): The username of the user.
        role (str): The role assigned to the user.
        chat_id (int): The user's chat ID.
        user_context_data (dict):A dictionary containing user-specific context data.
    """
    username: str
    role: str
    chat_id: int
    user_context_data: dict


class RoleAbilitiesDict(typing.TypedDict):
    """
    Represents the abilities associated with a role.

    Attributes:
        receives_messages (bool): Whether the role can receive messages.
        able_to_users_handle (bool): Whether the role can manage users.
        able_to_users_view (bool): Whether the role can view users.
        able_to_faqs_handle (bool): Whether the role can manage FAQs.
        able_to_faqs_view (bool): Whether the role can view FAQs.
        able_to_questions_handle (bool): Whether the role can manage questions.
        able_to_questions_view (bool): Whether the role can view questions.
        able_to_ask (bool): Whether the role can ask questions.
        able_to_answer (bool): Whether the role can answer questions.
    """
    receives_messages: bool
    able_to_users_handle: bool
    able_to_users_view: bool
    able_to_faqs_handle: bool
    able_to_faqs_view: bool
    able_to_questions_handle: bool
    able_to_questions_view: bool
    able_to_ask: bool
    able_to_answer: bool


class QuestionStatsDict(typing.TypedDict):
    """
    Represents statistics about questions.

    Attributes:
        total_questions (int): The total number of questions.
        unanswered_questions (int): The number of unanswered questions.
        processing_questions (int): The number of questions currently being processed.
        answered_questions (int): The number of answered questions.
    """
    total_questions: int
    unanswered_questions: int
    processing_questions: int
    answered_questions: int


class QuestionDict(typing.TypedDict):
    """
    Represents a single question.

    Attributes:
        question_id (int): The unique ID of the question.
        user_id (int): The ID of the user who asked the question.
        chat_id (int): The ID of the chat where the question was asked.
        message_id (int): The ID of the message containing the question.
        username (str): The username of the user who asked the question.
        first_name (str): The first name of the user.
        last_name (str): The last name of the user.
        question (str): The text of the question.
        asked_date (datetime.datetime): The date and time when the question was asked.
        answered_date (typing.Union[datetime.datetime, None]): The date and time when the question was answered (if applicable).
        status (str): The current status of the question (e.g., "Не обработан", "Обрабатывается", "Обработан").
        moderator_username (typing.Union[str,  None]): The username of the moderator handling the question (if applicable).
    """
    question_id: int
    user_id: int
    chat_id: int
    message_id: int
    username: str
    first_name: str
    last_name: str
    question: str
    asked_date: datetime.datetime
    answered_date: typing.Union[datetime.datetime, None]
    status: str
    moderator_username: typing.Union[str,  None]


class FAQ_Dict(typing.TypedDict):
    """
    Represents a Frequently Asked Question (FAQ).

    Attributes:
        faq_id (int): The unique ID of the FAQ.
        question (str): The question text.
        answer (str): The answer text.
        views_count (int): The number of times the FAQ has been viewed.
    """
    faq_id: int
    question: str
    answer: str
    views_count: int


class MySQL_PoolConfigDict(typing.TypedDict):
    """
    Configuration parameters for a MySQL connection pool.

    Attributes:
        database (str): The name of the database.
        host (str): The hostname or IP address of the MySQL server.
        port (int): The port number of the MySQL server.
        user (str): The database username.
        password (str): The database password.
        pool_name (str): The name of the connection pool.
        pool_size (int): The maximum number of connections in the pool.
    """
    database: str
    host: str
    port: int
    user: str
    password: str
    pool_name: str
    pool_size: int


class AuthDataDict(typing.TypedDict):
    """
    Authentication data for the application.

    Attributes:
        telegram_token (str): The Telegram Bot API token.
        MySQL_pool_config (MySQL_PoolConfigDict): Configuration for the MySQL connection pool.
    """
    telegram_token: str
    MySQL_pool_config: MySQL_PoolConfigDict


start_panel_type = typing.Callable[[Update, ContextTypes.DEFAULT_TYPE], typing.Coroutine[typing.Any, typing.Any, None]]
get_user_context_type = typing.Callable[[Update, ContextTypes.DEFAULT_TYPE], None]
