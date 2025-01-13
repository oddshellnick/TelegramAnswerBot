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
        language (str): language the user speaks.
        chat_id (int): The user's chat ID.
        user_context_data (dict):A dictionary containing user-specific context data.
    """
	username: str
	role: str
	language: str
	chat_id: int
	user_context_data: dict


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


class SettingsDict(typing.TypedDict):
	"""
    Authentication data for the application.

    Attributes:
        telegram_token (str): The Telegram Bot API token.
        MySQL_pool_config (MySQL_PoolConfigDict): Configuration for the MySQL connection pool.
    """
	telegram_token: str
	MySQL_pool_config: MySQL_PoolConfigDict


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
        status (str): The current status of the question (e.g., "unprocessed", "processing", "processed").
        moderator_username (typing.Union[str, None]): The username of the moderator handling the question (if applicable).
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
	moderator_username: typing.Union[str, None]


class UsersViewLocalSingleDict(typing.TypedDict):
	"""
    Defines localized strings for user view functionalities in a single language.

    This TypedDict holds the localized text used in the user view section of the application for a single language.
    It ensures type safety and maintainability when working with these strings.

    Attributes:
        users_view_suggestion (str): A suggestion or introductory message for the user view section.
        cant_view_users (str): Warning message displayed when a user lacks permission to access the user view.
        view_users_statistics_button (str): Text displayed on the button to view user statistics.
        view_users_list_button (str): Text displayed on the button to view the list of users.
        user_statistics_output (str): Format string for displaying user statistics.
        cant_view_users_statistics_warning (str): Warning message when a user lacks permission to view user statistics.
        user_output (str): Format string for displaying user information.
        cant_view_users_list_warning (str): Warning message when a user lacks permission to view the user list.
    """
	users_view_suggestion: str
	cant_view_users: str
	view_users_statistics_button: str
	user_statistics_output: str
	cant_view_users_statistics_warning: str
	view_users_list_button: str
	user_output: str
	cant_view_users_list_warning: str


class UsersViewLocalDict(typing.TypedDict):
	"""
    Defines localized strings for user view functionalities across multiple languages.

    This TypedDict maps language codes to `UsersViewLocalSingleDict` instances, enabling easy access
    to localized text based on the user's chosen language.

    Attributes:
        ru (UsersViewLocalSingleDict): Localized strings for Russian.
        en (UsersViewLocalSingleDict): Localized strings for English.
        de (UsersViewLocalSingleDict): Localized strings for German.
        fr (UsersViewLocalSingleDict): Localized strings for French.
        es (UsersViewLocalSingleDict): Localized strings for Spanish.
        it (UsersViewLocalSingleDict): Localized strings for Italian.
        pt (UsersViewLocalSingleDict): Localized strings for Portuguese.
        zh (UsersViewLocalSingleDict): Localized strings for Chinese.
    """
	ru: UsersViewLocalSingleDict
	en: UsersViewLocalSingleDict
	de: UsersViewLocalSingleDict
	fr: UsersViewLocalSingleDict
	es: UsersViewLocalSingleDict
	it: UsersViewLocalSingleDict
	pt: UsersViewLocalSingleDict
	zh: UsersViewLocalSingleDict


class UsersHandleLocalSingleDict(typing.TypedDict):
	"""
    Defines localized strings for user handling functionalities in a single language.

    This TypedDict stores localized text used in the user handling section of the application
    for a single language, ensuring type safety and easier maintenance.

    Attributes:
        handle_users_suggestion (str): Introductory message or suggestion for user handling actions.
        cant_handle_users_warning (str): Warning message shown when a user lacks permission to handle users.
        add_role_to_user_button (str): Text for the button to add a role to a user.
        role_choice_suggestion (str): Message prompting the user to choose a role.
        input_user_to_add_role_suggestion (str): Message prompting the user to input a username for role addition.
        cant_add_role_to_user_warning (str): Warning message shown when a user can't add a role to another user.
        remove_role_to_user_button (str): Text for the button to remove a role from a user.
        input_user_to_remove_role_suggestion (str): Message prompting the user to input a username for role removal.
        cant_remove_role_from_user_warning (str): Warning message shown when a user can't remove a role from another user.
    """
	handle_users_suggestion: str
	cant_handle_users_warning: str
	add_role_to_user_button: str
	role_choice_suggestion: str
	input_user_to_add_role_suggestion: str
	cant_add_role_to_user_warning: str
	remove_role_to_user_button: str
	input_user_to_remove_role_suggestion: str
	cant_remove_role_from_user_warning: str


class UsersHandleLocalDict(typing.TypedDict):
	"""
    Defines localized strings for user handling functionalities across multiple languages.

    This TypedDict maps language codes to `UsersHandleLocalSingleDict` instances, allowing easy
    retrieval of localized text based on the user's chosen language.

    Attributes:
        ru (UsersHandleLocalSingleDict): Localized strings for Russian.
        en (UsersHandleLocalSingleDict): Localized strings for English.
        de (UsersHandleLocalSingleDict): Localized strings for German.
        fr (UsersHandleLocalSingleDict): Localized strings for French.
        es (UsersHandleLocalSingleDict): Localized strings for Spanish.
        it (UsersHandleLocalSingleDict): Localized strings for Italian.
        pt (UsersHandleLocalSingleDict): Localized strings for Portuguese.
        zh (UsersHandleLocalSingleDict): Localized strings for Chinese.
    """
	ru: UsersHandleLocalSingleDict
	en: UsersHandleLocalSingleDict
	de: UsersHandleLocalSingleDict
	fr: UsersHandleLocalSingleDict
	es: UsersHandleLocalSingleDict
	it: UsersHandleLocalSingleDict
	pt: UsersHandleLocalSingleDict
	zh: UsersHandleLocalSingleDict


class UsersMessageLocalSingleDict(typing.TypedDict):
	"""
    Defines localized strings for messages related to user role management in a single language.

    This TypedDict provides localized text for various confirmation and warning messages
    related to adding or removing user roles, ensuring type safety and easier maintenance.

    Attributes:
        user_role_added_confirmation (str): Confirmation message when a user's role is successfully added.
        user_role_removed_confirmation (str): Confirmation message when a user's role is successfully removed.
        you_lose_role_notification (str): Notification message sent to a user whose role has been removed.
        user_dont_have_role_warning (str): Warning message indicating that a user doesn't have a role.
        cant_remove_role_from_user_warning (str): Warning message when the user lacks permissions to removed from a user.
    """
	user_role_added_confirmation: str
	user_role_removed_confirmation: str
	you_lose_role_notification: str
	user_dont_have_role_warning: str
	cant_remove_role_from_user_warning: str


class UsersMessageLocalDict(typing.TypedDict):
	"""
    Defines localized strings for messages related to user role management across multiple languages.

    This TypedDict maps language codes to `UsersMessageLocalSingleDict` instances, providing
    easy access to localized messages based on the user's language preference.

    Attributes:
        ru (UsersMessageLocalSingleDict): Localized messages for Russian.
        en (UsersMessageLocalSingleDict): Localized messages for English.
        de (UsersMessageLocalSingleDict): Localized messages for German.
        fr (UsersMessageLocalSingleDict): Localized messages for French.
        es (UsersMessageLocalSingleDict): Localized messages for Spanish.
        it (UsersMessageLocalSingleDict): Localized messages for Italian.
        pt (UsersMessageLocalSingleDict): Localized messages for Portuguese.
        zh (UsersMessageLocalSingleDict): Localized messages for Chinese.
    """
	ru: UsersMessageLocalSingleDict
	en: UsersMessageLocalSingleDict
	de: UsersMessageLocalSingleDict
	fr: UsersMessageLocalSingleDict
	es: UsersMessageLocalSingleDict
	it: UsersMessageLocalSingleDict
	pt: UsersMessageLocalSingleDict
	zh: UsersMessageLocalSingleDict


class UsersLocalDict(typing.TypedDict):
	"""
    Combines localized dictionaries for all user-related aspects.

    This TypedDict serves as a container to hold localized string resources for different
    components related to user management: messages, handling, and viewing.
    It simplifies access to these localized strings by grouping them together.

    Attributes:
        message (UsersMessageLocalDict): Localized strings for messages related to user role management.
        handle (UsersHandleLocalDict): Localized strings for handling user roles and permissions.
        view (UsersViewLocalDict): Localized strings for viewing user information and statistics.
    """
	message: UsersMessageLocalDict
	handle: UsersHandleLocalDict
	view: UsersViewLocalDict


class QuestionsViewLocalSingleDict(typing.TypedDict):
	"""
    Localized strings for viewing questions in a single language.

    This TypedDict holds localized strings specific to the question viewing section of the application for a single language.
    It ensures type safety and maintainability for these strings.

    Attributes:
        questions_view_suggestion (str): Introductory message or suggestion for the questions view.
        cant_view_questions_warning (str): Warning message when the user lacks permission to view questions.
        view_questions_statistics_button (str): Text for the button to view question statistics.
        total_questions_count_output (str): Format string for displaying the total number of questions.
        unprocessed_questions_count_output (str): Format string for displaying the number of unprocessed questions.
        processing_questions_count_output (str): Format string for displaying the number of questions being processed.
        processed_questions_count_output (str): Format string for displaying the number of processed questions.
        average_answer_time_output (str): Format string for displaying the average answer time.
        cant_view_questions_statistics_warning (str): Warning message when the user can't view question statistics.
        view_questions_button (str): Text for the button to view a list of questions.
        input_number_of_questions_to_view_suggestion (str): Prompt to input the number of questions to view.
        cant_view_questions_list_warning (str): Warning message when the user can't view the questions list.
    """
	questions_view_suggestion: str
	cant_view_questions_warning: str
	view_questions_statistics_button: str
	total_questions_count_output: str
	unprocessed_questions_count_output: str
	processing_questions_count_output: str
	processed_questions_count_output: str
	average_answer_time_output: str
	cant_view_questions_statistics_warning: str
	view_questions_button: str
	input_number_of_questions_to_view_suggestion: str
	cant_view_questions_list_warning: str


class QuestionsViewLocalDict(typing.TypedDict):
	"""
    Localized strings for viewing questions across multiple languages.

    This TypedDict maps language codes to `QuestionsViewLocalSingleDict` instances, providing
    easy access to localized text based on the user's language preference.

    Attributes:
        ru (QuestionsViewLocalSingleDict): Localized strings for Russian.
        en (QuestionsViewLocalSingleDict): Localized strings for English.
        de (QuestionsViewLocalSingleDict): Localized strings for German.
        fr (QuestionsViewLocalSingleDict): Localized strings for French.
        es (QuestionsViewLocalSingleDict): Localized strings for Spanish.
        it (QuestionsViewLocalSingleDict): Localized strings for Italian.
        pt (QuestionsViewLocalSingleDict): Localized strings for Portuguese.
        zh (QuestionsViewLocalSingleDict): Localized strings for Chinese.
    """
	ru: QuestionsViewLocalSingleDict
	en: QuestionsViewLocalSingleDict
	de: QuestionsViewLocalSingleDict
	fr: QuestionsViewLocalSingleDict
	es: QuestionsViewLocalSingleDict
	it: QuestionsViewLocalSingleDict
	pt: QuestionsViewLocalSingleDict
	zh: QuestionsViewLocalSingleDict


class QuestionsHandleLocalSingleDict(typing.TypedDict):
	"""
    Localized strings for handling questions in a single language.

    This TypedDict holds localized strings used in the question handling section of the application
    for a single language. It ensures type safety and makes maintenance easier.

    Attributes:
        questions_handle_suggestion (str): Introductory message or suggestion for handling questions.
        cant_handle_questions_warning (str): Warning message shown when the user lacks permission.
        clear_questions_button (str): Text for the button to clear questions.
        questions_clear_aware (str): Confirmation message before clearing questions.
        questions_cleared_notification (str): Notification message after successfully clearing questions.
        cant_clear_questions_warning (str): Warning message when the user can't clear questions.
    """
	questions_handle_suggestion: str
	cant_handle_questions_warning: str
	clear_questions_button: str
	questions_clear_aware: str
	questions_cleared_notification: str
	cant_clear_questions_warning: str


class QuestionsHandleLocalDict(typing.TypedDict):
	"""
    Localized strings for handling questions across multiple languages.

    This TypedDict maps language codes to `QuestionsHandleLocalSingleDict` instances, facilitating
    access to localized text based on the user's language setting.

    Attributes:
        ru (QuestionsHandleLocalSingleDict): Localized strings for Russian.
        en (QuestionsHandleLocalSingleDict): Localized strings for English.
        de (QuestionsHandleLocalSingleDict): Localized strings for German.
        fr (QuestionsHandleLocalSingleDict): Localized strings for French.
        es (QuestionsHandleLocalSingleDict): Localized strings for Spanish.
        it (QuestionsHandleLocalSingleDict): Localized strings for Italian.
        pt (QuestionsHandleLocalSingleDict): Localized strings for Portuguese.
        zh (QuestionsHandleLocalSingleDict): Localized strings for Chinese.
    """
	ru: QuestionsHandleLocalSingleDict
	en: QuestionsHandleLocalSingleDict
	de: QuestionsHandleLocalSingleDict
	fr: QuestionsHandleLocalSingleDict
	es: QuestionsHandleLocalSingleDict
	it: QuestionsHandleLocalSingleDict
	pt: QuestionsHandleLocalSingleDict
	zh: QuestionsHandleLocalSingleDict


class QuestionsMessageLocalSingleDict(typing.TypedDict):
	"""
    Localized strings for formatting question messages in a single language.

    This TypedDict holds the localized format strings used to display questions and related counts.
    It ensures type safety and simplifies the management of these strings.

    Attributes:
        question_output (str): Format string for displaying a single question.
        questions_count_output (str): Format string for displaying the total number of questions.
    """
	question_output: str
	questions_count_output: str


class QuestionsMessageLocalDict(typing.TypedDict):
	"""
    Localized strings for formatting question messages across multiple languages.

    This TypedDict maps language codes to `QuestionsMessageLocalSingleDict` instances, allowing
    easy access to localized format strings based on the user's selected language.

    Attributes:
        ru (QuestionsMessageLocalSingleDict): Localized format strings for Russian.
        en (QuestionsMessageLocalSingleDict): Localized format strings for English.
        de (QuestionsMessageLocalSingleDict): Localized format strings for German.
        fr (QuestionsMessageLocalSingleDict): Localized format strings for French.
        es (QuestionsMessageLocalSingleDict): Localized format strings for Spanish.
        it (QuestionsMessageLocalSingleDict): Localized format strings for Italian.
        pt (QuestionsMessageLocalSingleDict): Localized format strings for Portuguese.
        zh (QuestionsMessageLocalSingleDict): Localized format strings for Chinese.
    """
	ru: QuestionsMessageLocalSingleDict
	en: QuestionsMessageLocalSingleDict
	de: QuestionsMessageLocalSingleDict
	fr: QuestionsMessageLocalSingleDict
	es: QuestionsMessageLocalSingleDict
	it: QuestionsMessageLocalSingleDict
	pt: QuestionsMessageLocalSingleDict
	zh: QuestionsMessageLocalSingleDict


class QuestionsLocalDict(typing.TypedDict):
	"""
    Combines localized dictionaries for all question-related aspects.

    This TypedDict acts as a container for localized strings related to questions, grouping
    together message formatting, handling, and viewing aspects for easier access.

    Attributes:
        message (QuestionsMessageLocalDict): Localized format strings for question messages.
        handle (QuestionsHandleLocalDict): Localized strings for handling question-related actions.
        view (QuestionsViewLocalDict): Localized strings for viewing questions and statistics.
    """
	message: QuestionsMessageLocalDict
	handle: QuestionsHandleLocalDict
	view: QuestionsViewLocalDict


class FaqViewLocalSingleDict(typing.TypedDict):
	"""
    Localized strings for FAQ viewing in a single language.

    This TypedDict stores localized strings used in the FAQ viewing section of the application
    for a single language. It enhances code readability and maintainability.

    Attributes:
        faq_choice_suggestion (str): A message suggesting a choice of FAQ actions.
        faq_output (str): Text displayed when showing FAQs.
    """
	faq_choice_suggestion: str
	faq_output: str


class FaqViewLocalDict(typing.TypedDict):
	"""
    Localized strings for FAQ viewing across multiple languages.

    This TypedDict maps language codes to `FaqViewLocalSingleDict` instances, enabling easy
    access to localized strings based on the user's language preference.

    Attributes:
        ru (FaqViewLocalSingleDict): Localized strings for Russian.
        en (FaqViewLocalSingleDict): Localized strings for English.
        de (FaqViewLocalSingleDict): Localized strings for German.
        fr (FaqViewLocalSingleDict): Localized strings for French.
        es (FaqViewLocalSingleDict): Localized strings for Spanish.
        it (FaqViewLocalSingleDict): Localized strings for Italian.
        pt (FaqViewLocalSingleDict): Localized strings for Portuguese.
        zh (FaqViewLocalSingleDict): Localized strings for Chinese.
    """
	ru: FaqViewLocalSingleDict
	en: FaqViewLocalSingleDict
	de: FaqViewLocalSingleDict
	fr: FaqViewLocalSingleDict
	es: FaqViewLocalSingleDict
	it: FaqViewLocalSingleDict
	pt: FaqViewLocalSingleDict
	zh: FaqViewLocalSingleDict


class FaqHandleLocalSingleDict(typing.TypedDict):
	"""
    Localized strings for FAQ handling in a single language.

    This TypedDict contains localized strings for the FAQ handling section of the application,
    ensuring type safety and improved code organization.

    Attributes:
        faq_handle_choice (str): Message presenting options for FAQ handling.
        cant_handle_faq_warning (str): Warning message when the user lacks permissions to handle FAQ.
        faq_clear_button (str): Text for the button to clear FAQs.
        faq_clear_aware (str): Confirmation message before clearing FAQs.
        faq_cleared_notification (str): Notification message after clearing FAQs.
        cant_clear_faq_warning (str): Warning message when the user lacks permissions to clear FAQ.
        edit_faq_button (str): Text for the button to edit an FAQ.
        input_faq_id_to_edit_suggestion (str): Prompt to input the FAQ ID for editing.
        input_faq_new_question_suggestion (str): Prompt to input the new question for an FAQ.
        input_faq_new_answer_suggestion (str): Prompt to input the new answer for an FAQ.
        cant_faq_edit_warning (str): Warning message when the user lacks permissions to edit an FAQ.
        create_faq_button (str): Text for the button to create a new FAQ.
        input_faq_question_suggestion (str): Prompt to input the question for a new FAQ.
        cant_create_faq_warning (str): Warning message when failing to create a new FAQ.
        delete_faq_button (str): Text for the button to delete an FAQ.
        input_faq_id_to_delete_suggestion (str): Prompt to input the FAQ ID for deletion.
        cant_faq_delete_warning (str): Warning message when failing to delete an FAQ.
    """
	faq_handle_choice: str
	cant_handle_faq_warning: str
	faq_clear_button: str
	faq_clear_aware: str
	faq_cleared_notification: str
	cant_clear_faq_warning: str
	edit_faq_button: str
	input_faq_id_to_edit_suggestion: str
	input_faq_new_question_suggestion: str
	input_faq_new_answer_suggestion: str
	cant_faq_edit_warning: str
	create_faq_button: str
	input_faq_question_suggestion: str
	cant_create_faq_warning: str
	delete_faq_button: str
	input_faq_id_to_delete_suggestion: str
	cant_faq_delete_warning: str


class FaqHandleLocalDict(typing.TypedDict):
	"""
    Localized strings for FAQ handling across multiple languages.

    This TypedDict maps language codes to `FaqHandleLocalSingleDict` instances, simplifying
    access to localized strings based on the user's language setting.

    Attributes:
        ru (FaqHandleLocalSingleDict): Localized strings for Russian.
        en (FaqHandleLocalSingleDict): Localized strings for English.
        de (FaqHandleLocalSingleDict): Localized strings for German.
        fr (FaqHandleLocalSingleDict): Localized strings for French.
        es (FaqHandleLocalSingleDict): Localized strings for Spanish.
        it (FaqHandleLocalSingleDict): Localized strings for Italian.
        pt (FaqHandleLocalSingleDict): Localized strings for Portuguese.
        zh (FaqHandleLocalSingleDict): Localized strings for Chinese.
    """
	ru: FaqHandleLocalSingleDict
	en: FaqHandleLocalSingleDict
	de: FaqHandleLocalSingleDict
	fr: FaqHandleLocalSingleDict
	es: FaqHandleLocalSingleDict
	it: FaqHandleLocalSingleDict
	pt: FaqHandleLocalSingleDict
	zh: FaqHandleLocalSingleDict


class FaqMessageLocalSingleDict(typing.TypedDict):
	"""
    Localized strings for messages related to FAQ management in a single language.

    This TypedDict stores localized strings used for various messages within the FAQ management
    section of the application for a single language.
    It improves code organization and type safety.

    Attributes:
        input_faq_answer_suggestion (str): Prompt to input the answer for an FAQ.
        new_faq_saved_notification (str): Notification message when a new FAQ is successfully saved.
        faq_with_id_deleted_confirmation (str): Confirmation message after deleting an FAQ.
        no_faq_with_id_warning (str): Warning message when an FAQ with a given ID is not found.
        faq_instance_choice (str): Message indicating a choice of FAQ instances (e.g., for editing).
        faq_instance_changed_notification (str): Notification message after changing an FAQ instance.
    """
	input_faq_answer_suggestion: str
	new_faq_saved_notification: str
	faq_with_id_deleted_confirmation: str
	no_faq_with_id_warning: str
	faq_instance_choice: str
	faq_instance_changed_notification: str


class FaqMessageLocalDict(typing.TypedDict):
	"""
    Localized strings for messages related to FAQ management across multiple languages.

    This TypedDict maps language codes to `FaqMessageLocalSingleDict` instances, providing
    easy access to localized messages based on the user's language preference.

    Attributes:
        ru (FaqMessageLocalSingleDict): Localized messages for Russian.
        en (FaqMessageLocalSingleDict): Localized messages for English.
        de (FaqMessageLocalSingleDict): Localized messages for German.
        fr (FaqMessageLocalSingleDict): Localized messages for French.
        es (FaqMessageLocalSingleDict): Localized messages for Spanish.
        it (FaqMessageLocalSingleDict): Localized messages for Italian.
        pt (FaqMessageLocalSingleDict): Localized messages for Portuguese.
        zh (FaqMessageLocalSingleDict): Localized messages for Chinese.
    """
	ru: FaqMessageLocalSingleDict
	en: FaqMessageLocalSingleDict
	de: FaqMessageLocalSingleDict
	fr: FaqMessageLocalSingleDict
	es: FaqMessageLocalSingleDict
	it: FaqMessageLocalSingleDict
	pt: FaqMessageLocalSingleDict
	zh: FaqMessageLocalSingleDict


class FaqLocalDict(typing.TypedDict):
	"""
    Combines localized dictionaries for all FAQ-related aspects.

    This TypedDict groups together localized string resources for FAQ management, including
    message formatting, handling, and viewing.
    It simplifies access to these resources.

    Attributes:
        message (FaqMessageLocalDict): Localized strings for messages related to FAQ management.
        handle (FaqHandleLocalDict): Localized strings for handling FAQ-related actions.
        view (FaqViewLocalDict): Localized strings for viewing FAQs.
    """
	message: FaqMessageLocalDict
	handle: FaqHandleLocalDict
	view: FaqViewLocalDict


class MainHandleLocalSingleDict(typing.TypedDict):
	"""
    Localized strings for main handling functionalities in a single language.

    This TypedDict stores localized strings used in the main handling section of the application, for a single language.
    It improves code readability and maintainability.

    Attributes:
        input_question_suggestion (str): Message prompting the user to ask a question.
        cant_ask_question_warning (str): Warning message when the user lacks permissions to ask a question.
        input_answer_suggestion (str): Message prompting the user to answer a question.
        cant_answer_question_warning (str): Warning message when the user lacks permissions to answer a question.
        question_preview (str): Format string for displaying a question preview.
        answer_question_button (str): Text displayed on the button to answer a question.
        next_question_button (str): Text displayed on the button to proceed to the next question.
        no_questions_warning (str): Message indicating that there are no questions to answer.
        language_choice_suggestion (str): Message prompting the user to choose a language.
    """
	input_question_suggestion: str
	cant_ask_question_warning: str
	input_answer_suggestion: str
	cant_answer_question_warning: str
	question_preview: str
	answer_question_button: str
	next_question_button: str
	no_questions_warning: str
	language_choice_suggestion: str


class MainHandleLocalDict(typing.TypedDict):
	"""
    Localized strings for main handling functionalities across multiple languages.

    This TypedDict maps language codes to `MainHandleLocalSingleDict` instances, enabling easy
    access to localized strings based on the user's selected language.

    Attributes:
        ru (MainHandleLocalSingleDict): Localized strings for Russian.
        en (MainHandleLocalSingleDict): Localized strings for English.
        de (MainHandleLocalSingleDict): Localized strings for German.
        fr (MainHandleLocalSingleDict): Localized strings for French.
        es (MainHandleLocalSingleDict): Localized strings for Spanish.
        it (MainHandleLocalSingleDict): Localized strings for Italian.
        pt (MainHandleLocalSingleDict): Localized strings for Portuguese.
        zh (MainHandleLocalSingleDict): Localized strings for Chinese.
    """
	ru: MainHandleLocalSingleDict
	en: MainHandleLocalSingleDict
	de: MainHandleLocalSingleDict
	fr: MainHandleLocalSingleDict
	es: MainHandleLocalSingleDict
	it: MainHandleLocalSingleDict
	pt: MainHandleLocalSingleDict
	zh: MainHandleLocalSingleDict


class MainMessageLocalSingleDict(typing.TypedDict):
	"""
    Localized strings for messages in the main section of the application (single language).

    This TypedDict holds localized strings used for various messages within the main section
    of the application for just one language, improving code organization and type safety.

    Attributes:
        answer_notification (str): Message notifying the user of a new answer.
        answer_accepted_confirmation (str): Confirmation message when an answer is accepted.
        question_answered_warning (str): Warning message when a question is already answered.
        new_question_notification (str): Message notifying the user of a new question.
        new_question_accepted_confirmation (str): Confirmation message when a new question is accepted.
    """
	answer_notification: str
	answer_accepted_confirmation: str
	question_answered_warning: str
	new_question_notification: str
	new_question_accepted_confirmation: str


class MainMessageLocalDict(typing.TypedDict):
	"""
    Localized strings for messages in the main section of the application (multiple languages).

    This TypedDict maps language codes to `MainMessageLocalSingleDict` instances, making it
    easier to access localized messages based on the user's selected language.

    Attributes:
        ru (MainMessageLocalSingleDict): Localized messages for Russian.
        en (MainMessageLocalSingleDict): Localized messages for English.
        de (MainMessageLocalSingleDict): Localized messages for German.
        fr (MainMessageLocalSingleDict): Localized messages for French.
        es (MainMessageLocalSingleDict): Localized messages for Spanish.
        it (MainMessageLocalSingleDict): Localized messages for Italian.
        pt (MainMessageLocalSingleDict): Localized messages for Portuguese.
        zh (MainMessageLocalSingleDict): Localized messages for Chinese.
    """
	ru: MainMessageLocalSingleDict
	en: MainMessageLocalSingleDict
	de: MainMessageLocalSingleDict
	fr: MainMessageLocalSingleDict
	es: MainMessageLocalSingleDict
	it: MainMessageLocalSingleDict
	pt: MainMessageLocalSingleDict
	zh: MainMessageLocalSingleDict


class MainLocalDict(typing.TypedDict):
	"""
    Combines localized dictionaries for all main application aspects.

    This TypedDict groups together localized string resources for the main application section,
    including message formatting, handling, and (presumably) viewing aspects.
    It simplifies access to these resources.

    Attributes:
        message (MainMessageLocalDict): Localized strings for messages in the main section.
        handle (MainHandleLocalDict): Localized strings for handling actions in the main section.
        view (dict):
    """
	message: MainMessageLocalDict
	handle: MainHandleLocalDict
	view: dict


class StartLocalSingleDict(typing.TypedDict):
	"""
    Localized strings for the start menu in a single language.

    This TypedDict holds the localized text used in the start menu of the application for
    a single language. This improves code readability and maintainability.

    Attributes:
        handle_faq (str): Text for the option to handle FAQs.
        view_faq (str): Text for the option to view FAQs.
        handle_questions (str): Text for the option to handle questions.
        view_questions (str): Text for the option to view questions.
        handle_users (str): Text for the option to handle users.
        view_users (str): Text for the option to view users.
        ask_question (str): Text for the option to ask a question.
        answer_question (str): Text for the option to answer a question.
        chose_language (str): Text for the option to choose a language.
    """
	handle_faq: str
	view_faq: str
	handle_questions: str
	view_questions: str
	handle_users: str
	view_users: str
	ask_question: str
	answer_question: str
	chose_language: str


class StartLocalDict(typing.TypedDict):
	"""
    Localized strings for the start menu across multiple languages.

    This TypedDict maps language codes to `StartLocalSingleDict` instances, making it easy
    to retrieve localized text based on the user's language preference.

    Attributes:
        ru (StartLocalSingleDict): Localized strings for Russian.
        en (StartLocalSingleDict): Localized strings for English.
        de (StartLocalSingleDict): Localized strings for German.
        fr (StartLocalSingleDict): Localized strings for French.
        es (StartLocalSingleDict): Localized strings for Spanish.
        it (StartLocalSingleDict): Localized strings for Italian.
        pt (StartLocalSingleDict): Localized strings for Portuguese.
        zh (StartLocalSingleDict): Localized strings for Chinese.
    """
	ru: StartLocalSingleDict
	en: StartLocalSingleDict
	de: StartLocalSingleDict
	fr: StartLocalSingleDict
	es: StartLocalSingleDict
	it: StartLocalSingleDict
	pt: StartLocalSingleDict
	zh: StartLocalSingleDict


class OthersLocalSingleDict(typing.TypedDict):
	"""
    Defines the structure for localized strings for a single language.

    This TypedDict specifies the keys and types for localized strings used in various parts
    of the application, such as warnings, button labels, etc., for a single language.

    Attributes:
        integer_needed_warning (str): Warning message indicating that an integer is required.
        above_zero_needed_warning (str): Warning message indicating that a number greater than zero is required.
        decline_button (str): Text for the decline button.
        back_button (str): Text for the back button.
    """
	integer_needed_warning: str
	above_zero_needed_warning: str
	decline_button: str
	back_button: str


class OthersLocalDict(typing.TypedDict):
	"""
    Defines the structure for localized strings across multiple languages.

    This TypedDict acts as a container for localized strings, mapping language codes to `OthersLocalSingleDict` instances.
    This allows easy access to localized text based on the user's selected language.

    Attributes:
        ru (OthersLocalSingleDict): Localized strings for Russian.
        en (OthersLocalSingleDict): Localized strings for English.
        de (OthersLocalSingleDict): Localized strings for German.
        fr (OthersLocalSingleDict): Localized strings for French.
        es (OthersLocalSingleDict): Localized strings for Spanish.
        it (OthersLocalSingleDict): Localized strings for Italian.
        pt (OthersLocalSingleDict): Localized strings for Portuguese.
        zh (OthersLocalSingleDict): Localized strings for Chinese.
    """
	ru: OthersLocalSingleDict
	en: OthersLocalSingleDict
	de: OthersLocalSingleDict
	fr: OthersLocalSingleDict
	es: OthersLocalSingleDict
	it: OthersLocalSingleDict
	pt: OthersLocalSingleDict
	zh: OthersLocalSingleDict


class RolesLocalSingleDict(typing.TypedDict):
	"""
    Defines localized role names for a single language.

    This TypedDict holds the localized names for different user roles within the application for a single language.
    It ensures type safety when accessing and using these role names.

    Attributes:
        developer (str): Localized name for the "developer" role.
        administrator (str): Localized name for the "administrator" role.
        moderator (str): Localized name for the "moderator" role.
        user (str): Localized name for the "user" role.
    """
	developer: str
	administrator: str
	moderator: str
	user: str


class RolesLocalDict(typing.TypedDict):
	"""
    Defines localized role names across multiple languages.

    This TypedDict maps language codes to `RolesLocalSingleDict` instances, providing a
    convenient way to access localized role names based on the user's selected language.

    Attributes:
        ru (RolesLocalSingleDict): Localized role names for Russian.
        en (RolesLocalSingleDict): Localized role names for English.
        de (RolesLocalSingleDict): Localized role names for German.
        fr (RolesLocalSingleDict): Localized role names for French.
        es (RolesLocalSingleDict): Localized role names for Spanish.
        it (RolesLocalSingleDict): Localized role names for Italian.
        pt (RolesLocalSingleDict): Localized role names for Portuguese.
        zh (RolesLocalSingleDict): Localized role names for Chinese.
    """
	ru: RolesLocalSingleDict
	en: RolesLocalSingleDict
	de: RolesLocalSingleDict
	fr: RolesLocalSingleDict
	es: RolesLocalSingleDict
	it: RolesLocalSingleDict
	pt: RolesLocalSingleDict
	zh: RolesLocalSingleDict


class LanguagesDict(typing.TypedDict):
	"""
    Dictionary containing language names. This allows for easy lookup of language names by code.

    Attributes:
        ru (str): Name of the Russian language.
        en (str): Name of the English language.
        de (str): Name of the German language.
        fr (str): Name of the French language.
        es (str): Name of the Spanish language.
        it (str): Name of the Italian language.
        pt (str): Name of the Portuguese language.
        zh (str): Name of the Chinese language.
    """
	ru: str
	en: str
	de: str
	fr: str
	es: str
	it: str
	pt: str
	zh: str


class LocalizationsDict(typing.TypedDict):
	"""
    Top-level dictionary containing all localized strings for the application.

    This TypedDict acts as the central repository for all localized strings, organized by section and language.
    It provides a structured way to access localized text throughout the application.

    Attributes:
        languages (LanguagesDict): Dictionary mapping language codes to language names.
        start (StartLocalDict): Localized strings for the start menu.
        main (MainLocalDict): Localized strings for the main application section.
        faq (FaqLocalDict): Localized strings for FAQ management.
        questions (QuestionsLocalDict): Localized strings for question management.
        users (UsersLocalDict): Localized strings for user management.
        roles (RolesLocalDict): Localized strings for role names.
        others (OthersLocalDict): Localized strings for miscellaneous elements.
    """
	languages: LanguagesDict
	roles: RolesLocalDict
	others: OthersLocalDict
	start: StartLocalDict
	main: MainLocalDict
	faq: FaqLocalDict
	questions: QuestionsLocalDict
	users: UsersLocalDict


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


start_panel_type = typing.Callable[[Update, ContextTypes.DEFAULT_TYPE], typing.Coroutine[typing.Any, typing.Any, None]]
get_user_context_type = typing.Callable[[Update, ContextTypes.DEFAULT_TYPE], None]
language_type = typing.Literal["ru", "en", "de", "fr", "es", "it", "pt", "zh"]
