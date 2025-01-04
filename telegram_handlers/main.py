import typing
import functions
import data_handlers
from telegram.error import BadRequest
from telegram.constants import ParseMode
from telegram.ext import CallbackQueryHandler, ContextTypes
from objects_types import get_user_context_type, start_panel_type
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update


class StateFlags:
    """
    Defines string constants representing different states within the bot's conversation flow, primarily focused on question and answer interactions.

    These flags track the user's current interaction state, enabling the bot to handle different inputs and
    callbacks related to asking questions, providing answers, viewing documentation, and managing questions.

    Attributes:
        input_question (str): State for handling user input of a new question.
        input_answer (str): State for handling user input of an answer to a question.

        view_doc (str): State for viewing documentation.

        ask_question (str): State for initiating the process of asking a question.

        decline_question (str): State for declining a question.
        reply_to_question (str): State for replying to a question.
        answer_question (str): State for answering a question.
    """
    input_question = "input_question"
    input_answer = "input_answer"

    view_doc = "view_doc"

    ask_question = "ask_question"

    decline_question = "decline_question"
    reply_to_question = "reply_to_question"
    answer_question = "answer_question"


class Main_message:
    """
    Handles message-based interactions for asking and answering questions.

    This class processes user input for both asking new questions and providing answers to existing questions.
    It interacts with the database to store new questions, update question status, and retrieve necessary information.
    Error handling is included to manage potential issues such as sending messages to unavailable users.

    Attributes:
        db_handler (MySQLDataHandler): An instance of the MySQLDataHandler for database interaction.

    :Usage:
        main_message = Main_message(db_handler_instance)
        main_message.input_answer(update, context) # Process user input for an answer.
        main_message.input_question(update, context) # Process user input for a question.
    """
    def __init__(self, db_handler: data_handlers.MySQLDataHandler):
        """
        Initializes the Main_message class.

        Args:
            db_handler (MySQLDataHandler): The data handler for database operations.
        """
        self.db_handler = db_handler

    async def input_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Processes a user's answer to a question.

        Sends the answer to the user who asked the question and updates the question's status in the database. Handles potential errors like failed message delivery.

        Args:
            update (Update): The Telegram update object.
            context (ContextTypes.DEFAULT_TYPE): The Telegram context object.
        """
        reserved_question = self.db_handler.questions_data.check_question_reservation(context.user_data["temp"]["question_id"], update.effective_user.username)

        if reserved_question:
            try:
                await context.bot.send_message(
                        chat_id=int(reserved_question["chat_id"]),
                        reply_to_message_id=int(reserved_question["message_id"]),
                        text=update.message.text
                )
            except BadRequest:
                try:
                    await context.bot.send_message(
                            chat_id=int(reserved_question["chat_id"]),
                            text=f"Ваш вопрос: {reserved_question['question']}\n\nОтвет: {update.message.text}"
                    )
                except BadRequest:
                    pass

            self.db_handler.questions_data.mark_question_as_answered(context.user_data["temp"]["question_id"])

            await context.bot.send_message(chat_id=update.effective_chat.id, text="Ваш ответ отправлен!")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="На этот вопрос уже ответили :(")

        context.user_data["temp"] = {}
        context.user_data.pop("processing")
        self.db_handler.users_data.update_last_state(update.effective_user.username, StateFlags.input_answer, None, context)

    async def input_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Processes a user's question.

        Saves the question to the database and notifies all relevant users.

        Args:
            update (Update): The Telegram update object.
            context (ContextTypes.DEFAULT_TYPE): The Telegram context object.
        """
        question = update.message.text

        self.db_handler.questions_data.add_question(
                context.user_data["temp"]["user_id"],
                context.user_data["temp"]["chat_id"],
                update.message.message_id,
                context.user_data["temp"]["username"],
                context.user_data["temp"]["first_name"],
                context.user_data["temp"]["last_name"],
                question
        )

        for user_chat_receiving_messages in self.db_handler.users_data.get_users_chats_receiving_messages():
            try:
                await context.bot.send_message(chat_id=user_chat_receiving_messages, text="Появился новый вопрос!")
            except BadRequest:
                pass

        await context.bot.send_message(chat_id=update.effective_chat.id, text="Спасибо, ваш вопрос получен!")

        context.user_data["temp"] = {}
        context.user_data.pop("processing")
        self.db_handler.users_data.update_last_state(update.effective_user.username, StateFlags.input_question, None, context)


class Main_handle:
    """
    Handles callback query interactions for the main functionality of the bot: asking and answering questions.

    This class manages the flow of asking new questions and answering existing unanswered questions. It uses
    the database to track question status and user permissions. Error handling ensures that only authorized
    users can perform actions and provides feedback to users in case of issues.

    Attributes:
        start (function): The function to display the bot's start panel.
        get_user_context (function): A function to retrieve user-specific context data.
        db_handler (MySQLDataHandler): The data handler for database operations.

    :Usage:
      main_handle = Main_handle(start_panel_function, get_user_role_function, db_handler_instance)
      main_handle.ask_question(update, context) # Initiate asking a question.
      main_handle.answer_question(update, context) # Initiate answering questions.
      main_handle.decline_question(update, context) # Decline a question.
      main_handle.reply_to_question(update, context) # Reply to a question.
    """
    def __init__(
            self,
            start_panel: start_panel_type,
            get_user_role: typing.Callable[[Update, ContextTypes.DEFAULT_TYPE], None],
            db_handler: data_handlers.MySQLDataHandler
    ):
        """
        Initializes the Main_handle class.

        Args:
            start_panel (function): The function to display the start panel.
            get_user_role (function): The function to retrieve user role information.
            db_handler (MySQLDataHandler): The database handler instance.
        """
        self.start = start_panel
        self.get_user_context = get_user_role
        self.db_handler = db_handler

    async def ask_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Initiates the process of asking a question.

        Args:
            update (Update): The Telegram update object.
            context (ContextTypes.DEFAULT_TYPE): The Telegram context object.
        """
        self.get_user_context(update, context)
        current_state = functions.get_current_state(context)

        if current_state[0] in ["start"] and current_state[1] == update.effective_message.message_id:
            if context.user_data["abilities"]["able_to_ask"]:
                user_id = update.effective_user.id
                chat_id = update.effective_chat.id
                username = update.effective_user.username
                first_name = update.effective_user.first_name
                last_name = update.effective_user.last_name

                reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Отмена", callback_data="start")]])

                message = await functions.edit_message(
                        message_to_edit=current_state[1],
                        text="Пожалуйста, напишите ваш вопрос:",
                        update=update,
                        context=context,
                        reply_markup=reply_markup
                )

                context.user_data["temp"] = {
                    "user_id": user_id,
                    "chat_id": chat_id,
                    "username": username,
                    "first_name": first_name,
                    "last_name": last_name
                }
                self.db_handler.users_data.update_last_state(update.effective_user.username, StateFlags.ask_question, message.message_id, context)
                context.user_data["processing"] = True
            else:
                await functions.warning_rights_error("Задавать вопросы могут только пользователи.", self.start, update, context)
        else:
            await self.start(update, context)

    async def answer_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Presents the next unanswered question to a moderator.

        Args:
            update (Update): The Telegram update object.
            context (ContextTypes.DEFAULT_TYPE): The Telegram context object.
        """
        self.get_user_context(update, context)
        current_state = functions.get_current_state(context)

        if current_state[0] in ["start", StateFlags.decline_question] and current_state[1] == update.effective_message.message_id:
            if context.user_data["abilities"]["able_to_answer"]:
                if context.user_data["temp"].get("declined_questions", None) is None:
                    context.user_data["temp"]["declined_questions"] = []

                unanswered_question = self.db_handler.questions_data.get_first_unanswered_question(context.user_data["temp"]["declined_questions"])

                if unanswered_question:
                    question_id = unanswered_question["question_id"]
                    question_text = unanswered_question["question"]

                    self.db_handler.questions_data.reserve_question_for_moderator(update.effective_user.username, question_id)

                    keyboard = [
                        [InlineKeyboardButton("Ответить на вопрос", callback_data=StateFlags.reply_to_question)],
                        [InlineKeyboardButton("Следующий вопрос", callback_data=StateFlags.decline_question)],
                        [InlineKeyboardButton("Назад", callback_data="start")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)

                    message = await functions.edit_message(
                            message_to_edit=current_state[1],
                            text=f"Вопрос от пользователя (ID: {question_id}):\n\n{question_text}",
                            update=update,
                            context=context,
                            reply_markup=reply_markup
                    )

                    context.user_data["temp"]["question_id"] = unanswered_question["question_id"]
                    self.db_handler.users_data.update_last_state(update.effective_user.username, StateFlags.answer_question, message.message_id, context)
                    context.user_data["processing"] = True
                else:
                    await update.effective_message.edit_text(text="Вопросов больше нет.")

                    self.db_handler.users_data.update_last_state(update.effective_user.username, StateFlags.answer_question, None, context)

                    await self.start(update, context)
            else:
                await functions.warning_rights_error("У вас нет прав для ответов на вопросы.", self.start, update, context)
        else:
            await self.start(update, context)

    async def decline_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handles declining to answer a question.

        Args:
            update (Update): The Telegram update object.
            context (ContextTypes.DEFAULT_TYPE): The Telegram context object.
        """
        self.get_user_context(update, context)
        current_state = functions.get_current_state(context)

        if current_state[0] == StateFlags.answer_question and current_state[1] == update.effective_message.message_id:
            if context.user_data["abilities"]["able_to_answer"]:
                if context.user_data["temp"].get("declined_questions", None) is None:
                    context.user_data["temp"]["declined_questions"] = [context.user_data["temp"]["question_id"]]
                else:
                    context.user_data["temp"]["declined_questions"].append(context.user_data["temp"]["question_id"])

                self.db_handler.questions_data.free_question_from_moderator(context.user_data["temp"]["question_id"])

                context.user_data["processing"] = True
                self.db_handler.users_data.update_last_state(
                        update.effective_user.username,
                        StateFlags.decline_question,
                        update.effective_message.message_id,
                        context
                )

                await self.answer_question(update, context)
            else:
                await functions.warning_rights_error("У вас нет прав для ответов на вопросы.", self.start, update, context)
        else:
            await self.start(update, context)

    async def reply_to_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handles replying to a question; prompts the moderator for the answer text.

        Args:
            update (Update): The Telegram update object.
            context (ContextTypes.DEFAULT_TYPE): The Telegram context object.
        """
        self.get_user_context(update, context)
        current_state = functions.get_current_state(context)

        if current_state[0] == StateFlags.answer_question and current_state[1] == update.effective_message.message_id:
            if context.user_data["abilities"]["able_to_answer"]:
                await update.effective_message.edit_text(text="Введите текст ответа:")

                self.db_handler.users_data.update_last_state(update.effective_user.username, StateFlags.reply_to_question, None, context)
                context.user_data["processing"] = True
            else:
                await functions.warning_rights_error("У вас нет прав для ответов на вопросы.", self.start, update, context)
        else:
            await self.start(update, context)

    def get_callback_query_handlers(self) -> list[CallbackQueryHandler]:
        """
        Returns a list of CallbackQueryHandlers for main bot interactions.

        Returns:
            list[CallbackQueryHandler]: A list of CallbackQueryHandler objects.
        """
        return list(
                sorted(
                        [
                            CallbackQueryHandler(callback=self.answer_question, pattern=StateFlags.answer_question),
                            CallbackQueryHandler(callback=self.reply_to_question, pattern=StateFlags.reply_to_question),
                            CallbackQueryHandler(callback=self.decline_question, pattern=StateFlags.decline_question),
                            CallbackQueryHandler(callback=self.ask_question, pattern=StateFlags.ask_question)
                        ],
                        key=lambda x: len(x.pattern.pattern),
                        reverse=True
                )
        )


class Main_view:
    """
    Handles the display of documentation to the user.

    This class manages the presentation of documentation content retrieved from a provided list. It updates
    the user's last state in the database after displaying the documentation.

    Attributes:
        start_panel (function): A function to display the start panel of the bot.
        db_handler (MySQLDataHandler): An instance of the MySQLDataHandler for database operations.
        doc (list[str]): A list of strings representing the documentation content to be displayed. Each string can contain HTML formatting.

    :Usage:
        main_view = Main_view(start_panel_function, db_handler_instance, documentation_list)
        main_view.view_doc(update, context) # Display the documentation.
    """
    def __init__(self, start_panel: start_panel_type, db_handler: data_handlers.MySQLDataHandler, doc: list[str]):
        """
        Initializes the Main_view class.

        Args:
            start_panel (function): The function to display the bot's start panel.
            db_handler (MySQLDataHandler): The database handler instance.
            doc (list[str]): A list of strings representing the documentation content.
        """
        self.start_panel = start_panel
        self.db_handler = db_handler
        self.doc = doc

    async def view_doc(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Displays the documentation content to the user.

        Sends each item in the `doc` list as a separate message, using HTML formatting if present.
        Updates the database with the current state after displaying the documentation.

        Args:
            update (Update): The Telegram update object.
            context (ContextTypes.DEFAULT_TYPE): The Telegram context object.
        """
        for doc_item in self.doc:
            try:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=doc_item, parse_mode=ParseMode.HTML)
            except BadRequest:
                pass

        self.db_handler.users_data.update_last_state(update.effective_user.username, StateFlags.view_doc, None, context)

        await self.start_panel(update, context)

    def get_callback_query_handlers(self) -> list[CallbackQueryHandler]:
        """
        Returns a list of CallbackQueryHandlers for documentation viewing.

        Returns:
            list[CallbackQueryHandler]: A list of CallbackQueryHandler objects.
        """
        return list(
                sorted(
                        [CallbackQueryHandler(callback=self.view_doc, pattern=StateFlags.view_doc)],
                        key=lambda x: len(x.pattern.pattern),
                        reverse=True
                )
        )


class Main_controls:
    """
    Centralizes control and interaction for the main functionalities of the bot.

    This class combines the functionalities of Main_view, Main_handle, and Main_message, providing a
    single point of access for handling user interactions related to viewing documentation, asking
    questions, and answering questions. It manages the overall flow by combining the callback query
    handlers from the constituent classes.

    Attributes:
        view (Main_view): Instance for handling documentation display.
        handle (Main_handle): Instance for handling question asking and answering.
        message (Main_message): Instance for handling message-based question and answer processing.

    :Usage:
        main_controls = Main_controls(start_panel_function, get_user_context_function, db_handler_instance, documentation_list)
        handlers = main_controls.get_callback_query_handlers() # Get all combined handlers.
    """
    def __init__(
            self,
            start_panel: start_panel_type,
            get_user_context: get_user_context_type,
            db_handler: data_handlers.MySQLDataHandler,
            doc: list[str]
    ):
        """
        Initializes the Main_controls class.

        Args:
            start_panel (function): Function to display the start panel.
            get_user_context (function): Function to get user context.
            db_handler (MySQLDataHandler): Database handler instance.
            doc (list[str]): List of documentation strings.
        """
        self.view = Main_view(start_panel, db_handler, doc)
        self.handle = Main_handle(start_panel, get_user_context, db_handler)
        self.message = Main_message(db_handler)

    def get_callback_query_handlers(self) -> list[CallbackQueryHandler]:
        """
        Returns a combined list of callback query handlers.

        Merges handlers from the view and handle components, sorting them by pattern length to
        ensure correct precedence.

        Returns:
            list[CallbackQueryHandler]: A sorted list of CallbackQueryHandler instances.
        """
        return list(
                sorted(
                        self.view.get_callback_query_handlers() + self.handle.get_callback_query_handlers(),
                        key=lambda x: len(x.pattern.pattern),
                        reverse=True
                )
        )
