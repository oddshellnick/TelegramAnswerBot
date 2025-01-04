import json
import pandas
import pathlib
import objects_types
from system_paths import SystemPaths
from telegram.ext import ContextTypes
from telegram import InlineKeyboardMarkup, Message, Update


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


def read_doc() -> list[str]:
    """
    Reads the documentation file and splits it into sections.

    Returns:
        list[str]: A list of strings, where each string represents a section of the documentation. Sections are delimited by "__SPLIT__".
    """
    return open(SystemPaths.doc, "r", encoding="utf-8").read().split("\n__SPLIT__\n")


def read_auth_data() -> objects_types.AuthDataDict:
    """
    Reads authentication data from a JSON file.

    Returns:
        objects_types.AuthDataDict: A dictionary containing authentication information.
    """
    data = json.load(open(SystemPaths.auth_data, "r", encoding="utf-8"))

    return objects_types.AuthDataDict(
            telegram_token=data["telegram_token"],
            MySQL_pool_config=objects_types.MySQL_PoolConfigDict(
                    database=data["MySQL_pool_config"]["database"],
                    host=data["MySQL_pool_config"]["host"],
                    port=data["MySQL_pool_config"]["port"],
                    user=data["MySQL_pool_config"]["user"],
                    password=data["MySQL_pool_config"]["password"],
                    pool_name=data["MySQL_pool_config"]["pool_name"],
                    pool_size=data["MySQL_pool_config"]["pool_size"]
            )
    )


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


def get_db_line_dict(headers: list[str], row: list | tuple | None) -> dict:
    """
    Creates a dictionary from a database row and its corresponding headers.

    Args:
        headers (list[str]): A list of column headers.
        row (list | tuple | None): A tuple or list representing a database row, or None if no row is found.

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


def get_current_state(context: ContextTypes.DEFAULT_TYPE) -> tuple[str, int | None]:
    """
    Retrieves the current state from the user's context data.

    Args:
        context (ContextTypes.DEFAULT_TYPE): The Telegram bot context.

    Returns:
        tuple[str, int | None]: A tuple containing the current state (a string) and the message ID (an integer or None). Defaults to ("", None) if no state is found.
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
        reply_markup: InlineKeyboardMarkup | None = None
) -> Message:
    """
    Edits a message or sends a new one if the original message can't be edited. Clears "temp" data in the context if a new message is sent.

    Args:
        message_to_edit (int): The ID of the message to edit.
        text (str): The new text for the message.
        update (Update): The Telegram update object.
        context (ContextTypes.DEFAULT_TYPE): The Telegram bot context.
        reply_markup (InlineKeyboardMarkup | None):The reply markup for the message. Defaults to None.

    Returns:
        Message: The sent message object.
    """
    if message_to_edit == update.effective_message.message_id:
        return await update.effective_message.edit_text(text=text, reply_markup=reply_markup)

    context.user_data["temp"] = {}
    return await context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=reply_markup)


def build_hidden_files() -> list[pathlib.Path]:
    """
    Builds the hidden `auth_data.json` file if it doesn't exist.

    Creates a new `auth_data.json` file with default empty values if the file is not found.

    Returns:
        list[pathlib.Path]: list of all created hidden files.
    """
    hidden_files_built = []

    if not SystemPaths.auth_data.is_file():
        open(SystemPaths.auth_data, "w+", encoding="utf-8").write(
                json.dumps(
                        objects_types.AuthDataDict(
                                telegram_token="",
                                MySQL_pool_config=objects_types.MySQL_PoolConfigDict(database="", host="", port=0, user="", password="", pool_name="", pool_size=0)
                        ),
                        ensure_ascii=False,
                        indent=4
                )
        )
        hidden_files_built.append(SystemPaths.auth_data)

    if not SystemPaths.doc.is_file():
        open(SystemPaths.doc, "w+", encoding="utf-8").write("")
        hidden_files_built.append(SystemPaths.doc)

    return hidden_files_built
