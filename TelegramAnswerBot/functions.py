import os
import json
import typing
import pandas
import pathlib
from dotenv import load_dotenv
from telegram.ext import ContextTypes
from telegram.error import BadRequest
from TelegramAnswerBot import objects_types
from TelegramAnswerBot.errors import LocalizationError
from TelegramAnswerBot.system_paths import SystemPaths
from TelegramAnswerBot.utilities import accepted_languages
from telegram import (
	InlineKeyboardMarkup,
	Message,
	Update
)


async def warning_rights_error(
		warning: str,
		start_panel: objects_types.start_panel_type,
		update: Update,
		context: ContextTypes.DEFAULT_TYPE
):
	"""
	Displays a warning message to the user and returns them to the start panel.

	Args:
		warning (str): The warning message to display.
		start_panel (objects_types.start_panel_type): The function to call to display the start panel.
		update (Update): The Telegram update object.
		context (ContextTypes.DEFAULT_TYPE): The Telegram bot context.
	"""
	await update.effective_message.edit_text(text=warning)
	context.user_data["current_state"] = ("warning", None)
	await start_panel(update, context)


def read_json_file(path: pathlib.Path) -> typing.Any:
	"""
	Reads and parses a JSON file.

	Args:
		path (pathlib.Path): The path to the JSON file.

	Returns:
		typing.Any: The parsed JSON data.
	"""
	with open(path, "r", encoding="utf-8") as file:
		return json.loads(file.read())


def read_mysql_writeable_config() -> objects_types.Writeable_MySQL_ConfigDict:
	"""
	Reads the writable MySQL configuration from a JSON file.

	Returns:
		objects_types.Writeable_MySQL_ConfigDict: A dictionary containing the MySQL configuration.
	"""
	data = read_json_file(SystemPaths.mysql_config)
	
	return objects_types.Writeable_MySQL_ConfigDict(
			database=data["database"],
			host=data["host"],
			port=data["port"],
			user=data["user"],
			pool_name=data["pool_name"],
			pool_size=data["pool_size"]
	)


def read_settings() -> objects_types.SettingsDict:
	"""
	Reads settings data from a JSON file.

	Returns:
		objects_types.SettingsDict: A dictionary containing settings.
	"""
	data = read_mysql_writeable_config()
	load_dotenv(SystemPaths.env)
	
	return objects_types.SettingsDict(
			telegram_token=os.getenv("TELEGRAM_BOT_TOKEN"),
			MySQL_config=objects_types.MySQL_ConfigDict(
					database=data["database"],
					host=data["host"],
					port=data["port"],
					user=data["user"],
					password=os.getenv("MySQL_PASSWORD"),
					pool_name=data["pool_name"],
					pool_size=data["pool_size"]
			)
	)


def read_users_locals(file: dict) -> objects_types.UsersLocalDict:
	"""
	Reads and constructs a UsersLocalDict from a dictionary containing localized strings.

	This function processes localized strings for the user section, creating a `UsersLocalDict` object.
	It handles nested dictionaries for messages, handling, and viewing aspects.

	Args:
		file (dict): Dictionary containing nested dictionaries of localized user-related strings.

	Returns:
		objects_types.UsersLocalDict: A `UsersLocalDict` object with the localized strings.

	Raises:
		LocalizationError: If a language is missing from the input data.
	"""
	for language in accepted_languages:
		if language not in file["message"].keys():
			raise LocalizationError(language, "bin/localizations.json -> users -> message")
	
	for language in accepted_languages:
		if language not in file["handle"].keys():
			raise LocalizationError(language, "bin/localizations.json -> users -> handle")
	
	for language in accepted_languages:
		if language not in file["view"].keys():
			raise LocalizationError(language, "bin/localizations.json -> users -> view")
	
	return objects_types.UsersLocalDict(
			message=objects_types.UsersMessageLocalDict(
					**{
						lang: objects_types.UsersMessageLocalSingleDict(**file["message"][lang])
						for lang in accepted_languages
					}
			),
			handle=objects_types.UsersHandleLocalDict(
					**{
						lang: objects_types.UsersHandleLocalSingleDict(**file["handle"][lang])
						for lang in accepted_languages
					}
			),
			view=objects_types.UsersViewLocalDict(
					**{
						lang: objects_types.UsersViewLocalSingleDict(**file["view"][lang])
						for lang in accepted_languages
					}
			)
	)


def read_questions_locals(file: dict) -> objects_types.QuestionsLocalDict:
	"""
	Reads and constructs a QuestionsLocalDict from a dictionary containing localized strings.

	This function processes a dictionary containing localized strings for the questions section
	of the application and constructs a `QuestionsLocalDict` object.
	It handles nested dictionaries to build the complete localized structure.

	Args:
		file (dict): A dictionary containing nested dictionaries of localized strings for messages, handling, and viewing.

	Returns:
		objects_types.QuestionsLocalDict: A `QuestionsLocalDict` object containing the localized strings.

	Raises:
		LocalizationError: If a language is missing from the input data.
	"""
	for language in accepted_languages:
		if language not in file["message"].keys():
			raise LocalizationError(language, "bin/localizations.json -> questions -> message")
	
	for language in accepted_languages:
		if language not in file["handle"].keys():
			raise LocalizationError(language, "bin/localizations.json -> questions -> handle")
	
	for language in accepted_languages:
		if language not in file["view"].keys():
			raise LocalizationError(language, "bin/localizations.json -> questions -> view")
	
	return objects_types.QuestionsLocalDict(
			message=objects_types.QuestionsMessageLocalDict(
					**{
						lang: objects_types.QuestionsMessageLocalSingleDict(**file["message"][lang])
						for lang in accepted_languages
					}
			),
			handle=objects_types.QuestionsHandleLocalDict(
					**{
						lang: objects_types.QuestionsHandleLocalSingleDict(**file["handle"][lang])
						for lang in accepted_languages
					}
			),
			view=objects_types.QuestionsViewLocalDict(
					**{
						lang: objects_types.QuestionsViewLocalSingleDict(**file["view"][lang])
						for lang in accepted_languages
					}
			)
	)


def read_faq_locals(file: dict) -> objects_types.FaqLocalDict:
	"""
	Reads and constructs a FaqLocalDict from a dictionary containing localized strings.

	This function works similarly to `read_questions_locals`, but processes the localized strings
	for the FAQ section of the application.

	Args:
		file (dict): A dictionary containing nested dictionaries of localized strings.

	Returns:
		objects_types.FaqLocalDict: A `FaqLocalDict` object with the localized strings.

	Raises:
		LocalizationError: If a language is missing from the input data.
	"""
	for language in accepted_languages:
		if language not in file["message"].keys():
			raise LocalizationError(language, "bin/localizations.json -> faq -> message")
	
	for language in accepted_languages:
		if language not in file["handle"].keys():
			raise LocalizationError(language, "bin/localizations.json -> faq -> handle")
	
	for language in accepted_languages:
		if language not in file["view"].keys():
			raise LocalizationError(language, "bin/localizations.json -> faq -> view")
	
	return objects_types.FaqLocalDict(
			message=objects_types.FaqMessageLocalDict(
					**{
						lang: objects_types.FaqMessageLocalSingleDict(**file["message"][lang])
						for lang in accepted_languages
					}
			),
			handle=objects_types.FaqHandleLocalDict(
					**{
						lang: objects_types.FaqHandleLocalSingleDict(**file["handle"][lang])
						for lang in accepted_languages
					}
			),
			view=objects_types.FaqViewLocalDict(
					**{
						lang: objects_types.FaqViewLocalSingleDict(**file["view"][lang])
						for lang in accepted_languages
					}
			)
	)


def read_main_locals(file: dict) -> objects_types.MainLocalDict:
	"""
	Reads and constructs a MainLocalDict from a dictionary containing localized strings.

	This function is similar to `read_questions_locals` and `read_faq_locals`, but specifically
	handles the localization data for the main section of the application.
	Note the different handling of the "view" section, which might indicate a difference in structure compared to
	the other sections.

	Args:
		file (dict): A dictionary containing nested dictionaries of localized strings.

	Returns:
		objects_types.MainLocalDict: A `MainLocalDict` object with the localized strings.

	Raises:
		LocalizationError: If a language is missing from the input data.
	"""
	for language in accepted_languages:
		if language not in file["message"].keys():
			raise LocalizationError(language, "bin/localizations.json -> main -> message")
	
	for language in accepted_languages:
		if language not in file["handle"].keys():
			raise LocalizationError(language, "bin/localizations.json -> main -> handle")
	
	return objects_types.MainLocalDict(
			message=objects_types.MainMessageLocalDict(
					**{
						lang: objects_types.MainMessageLocalSingleDict(**file["message"][lang])
						for lang in accepted_languages
					}
			),
			handle=objects_types.MainHandleLocalDict(
					**{
						lang: objects_types.MainHandleLocalSingleDict(**file["handle"][lang])
						for lang in accepted_languages
					}
			),
			view=file["view"]
	)


def read_start_locals(file: dict) -> objects_types.StartLocalDict:
	"""
	Reads and constructs a StartLocalDict from a dictionary containing localized strings.

	This function takes a dictionary containing localized strings for the start menu and constructs
	a `StartLocalDict` object.
	It iterates through the specified languages to create the appropriate nested structure.

	Args:
		file (dict): A dictionary where keys are language codes and values are dictionaries of localized strings.

	Returns:
		objects_types.StartLocalDict: A `StartLocalDict` object containing the localized strings.

	Raises:
		LocalizationError: If a language is missing from the input data.
	"""
	for language in accepted_languages:
		if language not in file.keys():
			raise LocalizationError(language, "bin/localizations.json -> start")
	
	return objects_types.StartLocalDict(
			**{
				lang: objects_types.StartLocalSingleDict(**file[lang])
				for lang in accepted_languages
			}
	)


def read_others_locals(file: dict) -> objects_types.OthersLocalDict:
	"""
	Reads and constructs an OthersLocalDict from a dictionary containing localized strings.

	This function is similar to `read_start_locals`, but processes the localized strings
	for the "others" section of the application.

	Args:
		file (dict): A dictionary containing localized strings for different languages.

	Returns:
		objects_types.OthersLocalDict: An `OthersLocalDict` object with the localized strings.

	Raises:
		LocalizationError: If a language is missing from the input data.
	"""
	for language in accepted_languages:
		if language not in file.keys():
			raise LocalizationError(language, "bin/localizations.json -> others")
	
	return objects_types.OthersLocalDict(
			**{
				lang: objects_types.OthersLocalSingleDict(**file[lang])
				for lang in accepted_languages
			}
	)


def read_roles_locals(file: dict) -> objects_types.RolesLocalDict:
	"""
	Reads and constructs a RolesLocalDict from a dictionary containing localized strings.

	This function processes localized strings for role names, creating a `RolesLocalDict` object.
	The structure is similar to `read_start_locals` and `read_others_locals`.

	Args:
		file (dict): Dictionary containing localized role names.

	Returns:
		objects_types.RolesLocalDict: A `RolesLocalDict` object with localized role names.

	Raises:
		LocalizationError: If a language is missing from the input data.
	"""
	for language in accepted_languages:
		if language not in file.keys():
			raise LocalizationError(language, "bin/localizations.json -> roles")
	
	return objects_types.RolesLocalDict(
			**{
				lang: objects_types.RolesLocalSingleDict(**file[lang])
				for lang in accepted_languages
			}
	)


def read_languages_locals(file: dict) -> objects_types.LanguagesDict:
	"""
	Reads and constructs a LanguagesDict from a dictionary.

	This function simply calls the `objects_types.LanguagesDict` constructor with the input
	dictionary to create a `LanguagesDict` object.
	This is a straightforward mapping operation.

	Args:
		file (dict): A dictionary containing language names indexed by language codes.

	Returns:
		objects_types.LanguagesDict: A `LanguagesDict` object.

	Raises:
		LocalizationError: If a language is missing from the input data.
	"""
	for language in accepted_languages:
		if language not in file.keys():
			raise LocalizationError(language, "bin/localizations.json -> languages")
	
	return objects_types.LanguagesDict(**file)


def read_localizations() -> objects_types.LocalizationsDict:
	"""
	Reads and parses localization data from a JSON file.

	This function reads localization data from a JSON file specified by `SystemPaths.localizations`,
	parses it, and constructs a `LocalizationsDict` object.
	It uses helper functions to parse individual sections of the localization data (users, roles, etc.).

	Returns:
		objects_types.LocalizationsDict: A `LocalizationsDict` object containing all localized strings.  Returns None if file reading fails.

	Raises:
		LocalizationError: If a language is missing from the input data.
	"""
	data = read_json_file(SystemPaths.localizations)
	
	return objects_types.LocalizationsDict(
			languages=read_languages_locals(data["languages"]),
			roles=read_roles_locals(data["roles"]),
			others=read_others_locals(data["others"]),
			start=read_start_locals(data["start"]),
			main=read_main_locals(data["main"]),
			faq=read_faq_locals(data["faq"]),
			questions=read_questions_locals(data["questions"]),
			users=read_users_locals(data["users"])
	)


def read_text_file(path: pathlib.Path) -> str:
	"""
	Reads the content of a text file.

	Args:
		path (pathlib.Path): The path to the text file.

	Returns:
		str: The content of the text file as a string.
	"""
	with open(path, "r", encoding="utf-8") as file:
		return file.read()


def read_doc() -> dict[str, list[str]]:
	"""
	Reads and parses documentation files for multiple languages.

	Reads documentation text files from the specified path, splitting each file into a list of strings
	based on a special delimiter ("\\n__SPLIT__\\n").  Files are expected to be encoded in UTF-8.

	Returns:
		dict[str, list[str]]: A dictionary where keys are language codes (strings) and values are lists of strings, each representing a section of the documentation for that language.
	"""
	doc_files = os.listdir(SystemPaths.doc_folder)
	
	for language in accepted_languages:
		if f"{language}.txt" not in doc_files:
			raise LocalizationError(language, f"bin/doc/{language}.txt")
	
	return {
		language: read_text_file(SystemPaths.doc_folder / f"{language}.txt").split("\n__SPLIT__\n")
		for language in accepted_languages
	}


def preprocess_username(username: str) -> str:
	"""
	Removes the "@" symbol from the beginning of a username if present.

	Args:
		username (str): The username to preprocess.

	Returns:
		str: The preprocessed username.
	"""
	if username.startswith("@"):
		username = username[1:]
	
	return username


def get_language(context: ContextTypes.DEFAULT_TYPE) -> typing.Optional[objects_types.language_type]:
	"""
	Retrieves the user's preferred language from the context.

	This function checks the user's context for a stored language preference.
	It returns the language code if a valid language is found; otherwise, it returns None.

	Args:
		context (ContextTypes.DEFAULT_TYPE): The Telegram context object containing user data.

	Returns:
		typing.Optional[objects_types.language_type]: The two-letter language code (e.g., "en" for English, "ru" for Russian) or None if no valid language is found.
	"""
	language = context.user_data.get("language", None)
	
	if language in accepted_languages:
		return language
	
	return None


def get_db_line_dict(headers: list[str], row: typing.Optional[typing.Union[list, tuple]]) -> dict:
	"""
	Creates a dictionary from a database row and its corresponding headers.

	Args:
		headers (list[str]): A list of column headers.
		row (typing.Optional[typing.Union[list, tuple]]): A tuple or list representing a database row, or None if no row is found.

	Returns:
		dict: A dictionary where keys are headers and values are the corresponding row values. Returns an empty dictionary if the input is invalid or if the row is None.
	"""
	if isinstance(headers, list) and isinstance(row, (list, tuple)):
		return {header: value for header, value in zip(headers, row)}
	
	return {}


def get_db_data_frame(headers: list[str], rows: list[tuple]) -> pandas.DataFrame:
	"""
	Creates a Pandas DataFrame from a list of database rows and headers.

	Args:
		headers (list[str]): A list of column headers.
		rows (list[tuple]): A list of tuples, where each tuple represents a row in the database.

	Returns:
		pandas.DataFrame: A DataFrame created from the provided data. Returns an empty DataFrame if the input is invalid.
	"""
	if isinstance(headers, list) and isinstance(rows, (list, tuple)):
		return pandas.DataFrame(rows, columns=headers)
	
	return pandas.DataFrame()


def get_current_state(context: ContextTypes.DEFAULT_TYPE) -> tuple[str, typing.Optional[int]]:
	"""
	Retrieves the current state from the user's context data.

	Args:
		context (ContextTypes.DEFAULT_TYPE): The Telegram bot context.

	Returns:
		tuple[str, typing.Optional[int]]: A tuple containing the current state (a string) and the message ID (an integer or None). Defaults to ("", None) if no state is found.
	"""
	return context.user_data.get("current_state", ("", None))


def format_time(time_: float) -> str:
	"""
	Formats a time value (in seconds) into a human-readable string (HH:MM:SS format).

	Args:
		time_ (float): The time value in seconds.

	Returns:
		str: The formatted time string.
	"""
	hours_s = "%02d" % (time_ // 3600) if time_ > 3600 else ""
	minutes_s = "%02d" % (time_ % 3600 // 60) if time_ > 60 else ""
	seconds_s = "%02d" % (time_ % 60)
	
	return ":".join(list(filter(None, [hours_s, minutes_s, seconds_s])))


async def edit_message(
		message_to_edit: int,
		text: str,
		update: Update,
		context: ContextTypes.DEFAULT_TYPE,
		reply_markup: typing.Optional[InlineKeyboardMarkup] = None
) -> Message:
	"""
	Edits a message or sends a new one if the original message can't be edited. Clears "temp" data in the context if a new message is sent.

	Args:
		message_to_edit (int): The ID of the message to edit.
		text (str): The new text for the message.
		update (Update): The Telegram update object.
		context (ContextTypes.DEFAULT_TYPE): The Telegram bot context.
		reply_markup (typing.Optional[InlineKeyboardMarkup]):The reply markup for the message. Defaults to None.

	Returns:
		Message: The sent message object.
	"""
	if message_to_edit == update.effective_message.message_id:
		try:
			return await update.effective_message.edit_text(text=text, reply_markup=reply_markup)
		except BadRequest:
			return update.effective_message
	
	context.user_data["temp"] = {}
	return await context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=reply_markup)


def write_env_file(path: pathlib.Path, values: dict[str, typing.Any]):
	"""
	Writes a dictionary of key-value pairs to an environment file.

	Args:
		path (pathlib.Path): The path to the environment file.
		values (dict[str, typing.Any]): A dictionary containing the key-value pairs to write to the file.
	"""
	with open(path, "w+", encoding="utf-8") as file:
		file.write(
				"\n".join(
						f"{key}={'"' if isinstance(value, str) else ''}{value}{'"' if isinstance(value, str) else ''}"
						for key, value in values.items()
				)
		)


def write_json_file(path: pathlib.Path, data: typing.Any):
	"""
	Writes data to a JSON file.

	Args:
		path (pathlib.Path): The path to the JSON file.
		data (typing.Any): The data to be written to the file.
	"""
	with open(path, "w+", encoding="utf-8") as file:
		file.write(json.dumps(data, ensure_ascii=False, indent=4))


def build_hidden_files() -> list[pathlib.Path]:
	"""
	Builds and returns a list of hidden configuration files.

	This function creates the necessary hidden configuration files for the application if they don't already exist, initializing them with default values.

	Returns:
		list[pathlib.Path]: A list of pathlib.Path objects representing the created hidden files.
	"""
	hidden_files_built = []
	
	if not SystemPaths.mysql_config.is_file():
		write_json_file(
				SystemPaths.mysql_config,
				objects_types.Writeable_MySQL_ConfigDict(database="", host="", port=0, user="", pool_name="", pool_size=0)
		)
		hidden_files_built.append(SystemPaths.mysql_config)
	
	if not SystemPaths.env.is_file():
		write_env_file(SystemPaths.env, {"TELEGRAM_BOT_TOKEN": "", "MySQL_PASSWORD": ""})
		hidden_files_built.append(SystemPaths.env)
	
	return hidden_files_built
