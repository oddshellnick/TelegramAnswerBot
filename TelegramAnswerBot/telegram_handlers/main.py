import re
from dataclasses import dataclass
from telegram.error import BadRequest
from telegram.constants import ParseMode
from TelegramAnswerBot import (
	data_handlers,
	functions
)
from telegram.ext import (
	CallbackQueryHandler,
	ContextTypes
)
from telegram import (
	InlineKeyboardButton,
	InlineKeyboardMarkup,
	Update
)
from TelegramAnswerBot.objects_types import (
	LanguagesDict,
	MainHandleLocalDict,
	MainLocalDict,
	MainMessageLocalDict,
	OthersLocalDict,
	get_user_context_type,
	start_panel_type
)


@dataclass(frozen=True)
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

        previous_languages_group (str): State for navigating to the previous language group.
        next_languages_group (str): State for navigating to the next language group.
        set_language (str): State for setting a new language.
        view_languages_group (str): State for viewing available languages.
    """
	input_question = "input_question"
	input_answer = "input_answer"
	
	view_doc = "view_doc"
	
	ask_question = "ask_question"
	
	decline_question = "decline_question"
	reply_to_question = "reply_to_question"
	answer_question = "answer_question"
	
	previous_languages_group = "previous_languages_group"
	next_languages_group = "next_languages_group"
	set_language = "set_language"
	view_languages_group = "view_languages_group"


class Main_message:
	"""
    Handles message-based interactions for asking and answering questions.

    This class processes user input for both asking new questions and providing answers to existing questions.
    It interacts with the database to store new questions, update question status, and retrieve necessary information.
    Error handling is included to manage potential issues such as sending messages to unavailable users.
    Uses localized strings for internationalization.

    Attributes:
        start_panel (start_panel_type): Function to display the start panel.
        get_user_context (get_user_context_type): Function to retrieve user context.
        db_handler (MySQLDataHandler): An instance of the MySQLDataHandler for database interaction.
        main_local (MainMessageLocalDict): Localized strings specific to main message operations.
    """
	
	def __init__(
			self,
			start_panel: start_panel_type,
			get_user_context: get_user_context_type,
			db_handler: data_handlers.MySQLDataHandler,
			main_local: MainMessageLocalDict
	):
		"""
        Initializes the Main_message class.

        Args:
            start_panel (start_panel_type): Function to display the start panel.
            get_user_context (get_user_context_type): Function to retrieve user context.
            db_handler (MySQLDataHandler): The data handler for database operations.
            main_local (MainMessageLocalDict): Localized strings for main message operations.
        """
		self.start_panel = start_panel
		self.get_user_context = get_user_context
		self.db_handler = db_handler
		self.main_local = main_local
	
	async def input_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
		"""
        Processes a user's answer to a question.

        Sends the answer to the user who asked the question and updates the question's status in the database. Handles potential errors like failed message delivery.

        Args:
            update (Update): The Telegram update object.
            context (ContextTypes.DEFAULT_TYPE): The Telegram context object.
        """
		self.get_user_context(update, context)
		language = functions.get_language(context)
		
		if language is None:
			await self.start_panel(update, context)
			return
		
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
							text=self.main_local[language]["answer_notification"].format(question=reserved_question['question'], answer=update.message.text)
					)
				except BadRequest:
					pass
		
			self.db_handler.questions_data.mark_question_as_answered(context.user_data["temp"]["question_id"])
		
			await context.bot.send_message(chat_id=update.effective_chat.id, text=self.main_local[language]["answer_accepted_confirmation"])
		else:
			await context.bot.send_message(chat_id=update.effective_chat.id, text=self.main_local[language]["question_answered_warning"])
		
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
		self.get_user_context(update, context)
		language = functions.get_language(context)
		
		if language is None:
			await self.start_panel(update, context)
			return
		
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
				await context.bot.send_message(chat_id=user_chat_receiving_messages, text=self.main_local[language]["new_question_notification"])
			except BadRequest:
				pass
		
		await context.bot.send_message(chat_id=update.effective_chat.id, text=self.main_local[language]["new_question_accepted_confirmation"])
		
		context.user_data["temp"] = {}
		context.user_data.pop("processing")
		self.db_handler.users_data.update_last_state(update.effective_user.username, StateFlags.input_question, None, context)


class Main_handle:
	"""
    Handles callback query interactions for the main bot functionality: asking and answering questions.

    This class manages the flow of asking new questions and answering existing unanswered questions.
    It uses the database to track question status and user permissions.
    Error handling ensures that only authorized users can perform actions and provides feedback to users in case of issues.
    Uses localized strings for internationalization.

    Attributes:
        start_panel (start_panel_type): The function to display the bot's start panel.
        get_user_context (get_user_context_type): A function to retrieve user-specific context data including user role.
        db_handler (MySQLDataHandler): The data handler for database operations.
        main_local (MainHandleLocalDict): Localized strings specific to main handle operations.
        others_local (OthersLocalDict): Localized strings for general application use.
        languages_dict (LanguagesDict): Dictionary containing available languages and their codes.
    """
	
	def __init__(
			self,
			start_panel: start_panel_type,
			get_user_context: get_user_context_type,
			db_handler: data_handlers.MySQLDataHandler,
			main_local: MainHandleLocalDict,
			others_local: OthersLocalDict,
			languages_dict: LanguagesDict
	):
		"""
        Initializes the Main_handle class.

        Args:
            start_panel (start_panel_type): The function to display the start panel.
            get_user_context (get_user_context_type): The function to retrieve user role information.
            db_handler (MySQLDataHandler): The database handler instance.
            main_local (MainHandleLocalDict): Localized strings for main handle operations.
            others_local (OthersLocalDict): Localized strings for general application use.
            languages_dict (LanguagesDict): Dictionary containing available languages and their codes.
        """
		self.start_panel = start_panel
		self.get_user_context = get_user_context
		self.db_handler = db_handler
		self.main_local = main_local
		self.others_local = others_local
		self.languages_dict = languages_dict
	
	async def ask_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
		"""
        Initiates the process of asking a question.

        Args:
            update (Update): The Telegram update object.
            context (ContextTypes.DEFAULT_TYPE): The Telegram context object.
        """
		self.get_user_context(update, context)
		language = functions.get_language(context)
		
		if language is None:
			await self.start_panel(update, context)
			return
		
		current_state = functions.get_current_state(context)
		if current_state[0] not in ["start"] or current_state[1] != update.effective_message.message_id:
			await self.start_panel(update, context)
			return
		
		if not context.user_data["abilities"]["able_to_ask"]:
			await functions.warning_rights_error(self.main_local[language]["cant_ask_question_warning"], self.start_panel, update, context)
			return
		
		user_id = update.effective_user.id
		chat_id = update.effective_chat.id
		username = update.effective_user.username
		first_name = update.effective_user.first_name
		last_name = update.effective_user.last_name
		
		reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(self.others_local[language]["decline_button"], callback_data="start")]])
		
		message = await functions.edit_message(
				message_to_edit=current_state[1],
				text=self.main_local[language]["input_question_suggestion"],
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
	
	async def answer_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
		"""
        Presents the next unanswered question to a moderator.

        Args:
            update (Update): The Telegram update object.
            context (ContextTypes.DEFAULT_TYPE): The Telegram context object.
        """
		self.get_user_context(update, context)
		language = functions.get_language(context)
		
		if language is None:
			await self.start_panel(update, context)
			return
		
		current_state = functions.get_current_state(context)
		if current_state[0] not in ["start", StateFlags.decline_question] or current_state[1] != update.effective_message.message_id:
			await self.start_panel(update, context)
			return
		
		if not context.user_data["abilities"]["able_to_answer"]:
			await functions.warning_rights_error(self.main_local[language]["cant_answer_question_warning"], self.start_panel, update, context)
			return
		
		if context.user_data["temp"].get("declined_questions", None) is None:
			context.user_data["temp"]["declined_questions"] = []
		
		unanswered_question = self.db_handler.questions_data.get_first_unanswered_question(context.user_data["temp"]["declined_questions"])
		
		if unanswered_question:
			question_id = unanswered_question["question_id"]
			question_text = unanswered_question["question"]
		
			self.db_handler.questions_data.reserve_question_for_moderator(update.effective_user.username, question_id)
		
			keyboard = [
				[
					InlineKeyboardButton(self.main_local[language]["answer_question_button"], callback_data=StateFlags.reply_to_question)
				],
				[
					InlineKeyboardButton(self.main_local[language]["next_question_button"], callback_data=StateFlags.decline_question)
				],
				[InlineKeyboardButton(self.others_local[language]["back_button"], callback_data="start")]
			]
			reply_markup = InlineKeyboardMarkup(keyboard)
		
			message = await functions.edit_message(
					message_to_edit=current_state[1],
					text=self.main_local[language]["question_preview"].format(id=question_id, text=question_text),
					update=update,
					context=context,
					reply_markup=reply_markup
			)
		
			context.user_data["temp"]["question_id"] = unanswered_question["question_id"]
			self.db_handler.users_data.update_last_state(update.effective_user.username, StateFlags.answer_question, message.message_id, context)
			context.user_data["processing"] = True
		else:
			await update.effective_message.edit_text(text=self.main_local[language]["no_questions_warning"])
		
			self.db_handler.users_data.update_last_state(update.effective_user.username, StateFlags.answer_question, None, context)
		
			await self.start_panel(update, context)
	
	async def decline_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
		"""
        Handles declining to answer a question.

        Args:
            update (Update): The Telegram update object.
            context (ContextTypes.DEFAULT_TYPE): The Telegram context object.
        """
		self.get_user_context(update, context)
		language = functions.get_language(context)
		
		if language is None:
			await self.start_panel(update, context)
			return
		
		current_state = functions.get_current_state(context)
		if current_state[0] not in [StateFlags.answer_question] or current_state[1] != update.effective_message.message_id:
			await self.start_panel(update, context)
			return
		
		if not context.user_data["abilities"]["able_to_answer"]:
			await functions.warning_rights_error(self.main_local[language]["cant_answer_question_warning"], self.start_panel, update, context)
			return
		
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
	
	async def reply_to_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
		"""
        Handles replying to a question; prompts the moderator for the answer text.

        Args:
            update (Update): The Telegram update object.
            context (ContextTypes.DEFAULT_TYPE): The Telegram context object.
        """
		self.get_user_context(update, context)
		language = functions.get_language(context)
		
		if language is None:
			await self.start_panel(update, context)
			return
		
		current_state = functions.get_current_state(context)
		if current_state[0] not in [StateFlags.answer_question] or current_state[1] != update.effective_message.message_id:
			await self.start_panel(update, context)
			return
		
		if not context.user_data["abilities"]["able_to_answer"]:
			await functions.warning_rights_error(self.main_local[language]["cant_answer_question_warning"], self.start_panel, update, context)
			return
		
		reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(self.others_local[language]["decline_button"], callback_data="start")]])
		await update.effective_message.edit_text(text=self.main_local[language]["input_answer_suggestion"], reply_markup=reply_markup)
		
		self.db_handler.users_data.update_last_state(update.effective_user.username, StateFlags.reply_to_question, None, context)
		context.user_data["processing"] = True
	
	async def view_languages_group(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
		"""
        Displays a group of languages.

        Args:
            update (Update): The Telegram update object.
            context (ContextTypes.DEFAULT_TYPE): The Telegram context object.
        """
		self.get_user_context(update, context)
		current_state = functions.get_current_state(context)
		
		if (
				current_state[0] not in ["start", StateFlags.next_languages_group, StateFlags.previous_languages_group] or current_state[1] != update.effective_message.message_id
		) and current_state[0] != "needed_language":
			await self.start_panel(update, context)
			return
		
		language = functions.get_language(context)
		
		if context.user_data["temp"].get("languages_group", None) is None:
			total_languages_count = len(self.languages_dict.keys())
		
			context.user_data["temp"]["languages_group"] = 0
			context.user_data["temp"]["languages_groups"] = total_languages_count // 9 + (1 if total_languages_count % 9 > 0 else 0)
		
		start_index: int = context.user_data["temp"]["languages_group"] * 9
		end_index: int = start_index + 9
		
		languages_group_data = dict(list(self.languages_dict.items())[start_index:end_index])
		
		keyboard = [
			[InlineKeyboardButton(language, callback_data=f"{StateFlags.set_language}_{literal}")] for literal, language in languages_group_data.items()
		]
		if current_state[0] != "needed_language" and language is not None:
			keyboard.append(
					[
						InlineKeyboardButton("<<", callback_data=StateFlags.previous_languages_group),
						InlineKeyboardButton(self.others_local[language]["back_button"], callback_data="start"),
						InlineKeyboardButton(">>", callback_data=StateFlags.next_languages_group)
					]
			)
		else:
			keyboard.append(
					[
						InlineKeyboardButton("<<", callback_data=StateFlags.previous_languages_group),
						InlineKeyboardButton(">>", callback_data=StateFlags.next_languages_group)
					]
			)
		
		reply_markup = InlineKeyboardMarkup(keyboard)
		
		if current_state[0] != "needed_language" and language is not None:
			message = await functions.edit_message(
					current_state[1],
					self.main_local[language]["language_choice_suggestion"],
					update,
					context,
					reply_markup=reply_markup
			)
		else:
			message = await update.effective_user.send_message("🇷🇺🇺🇸🇩🇪", reply_markup=reply_markup)
		
		self.db_handler.users_data.update_last_state(update.effective_user.username, StateFlags.view_languages_group, message.message_id, context)
	
	async def next_languages_group(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
		"""
        Navigates to the next group of languages.

        Args:
            update (Update): The Telegram update object.
            context (ContextTypes.DEFAULT_TYPE): The Telegram context object.
        """
		self.get_user_context(update, context)
		current_state = functions.get_current_state(context)
		
		if (
				current_state[0] not in [
					StateFlags.view_languages_group,
					StateFlags.next_languages_group,
					StateFlags.previous_languages_group
				] or current_state[1] != update.effective_message.message_id
		) and current_state[0] != "needed_language":
			await self.start_panel(update, context)
			return
		
		if context.user_data["temp"].get("languages_group", None) is None:
			total_languages_count = len(self.languages_dict.keys())
		
			context.user_data["temp"]["languages_group"] = 0
			context.user_data["temp"]["languages_groups"] = total_languages_count // 9 + (1 if total_languages_count % 9 > 0 else 0)
		
		start_languages_group = context.user_data["temp"]["languages_group"]
		
		try:
			context.user_data["temp"]["languages_group"] = (context.user_data["temp"]["languages_group"] + 1) % context.user_data["temp"]["languages_groups"]
		except ZeroDivisionError:
			context.user_data["temp"]["languages_group"] = 0
		self.db_handler.users_data.update_last_state(
				update.effective_user.username,
				StateFlags.next_languages_group,
				update.effective_message.message_id,
				context
		)
		
		if start_languages_group != context.user_data["temp"]["languages_group"]:
			await self.view_languages_group(update, context)
	
	async def previous_languages_group(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
		"""
        Navigates to the previous group of languages.

        Args:
            update (Update): The Telegram update object.
            context (ContextTypes.DEFAULT_TYPE): The Telegram context object.
        """
		self.get_user_context(update, context)
		current_state = functions.get_current_state(context)
		
		if (
				current_state[0] not in [
					StateFlags.view_languages_group,
					StateFlags.next_languages_group,
					StateFlags.previous_languages_group
				] or current_state[1] != update.effective_message.message_id
		) and current_state[0] != "needed_language":
			await self.start_panel(update, context)
			return
		
		if context.user_data["temp"].get("languages_group", None) is None:
			total_languages_count = len(self.languages_dict.keys())
		
			try:
				context.user_data["temp"]["languages_group"] = (context.user_data["temp"]["languages_group"] + 1) % context.user_data["temp"]["languages_groups"]
			except ZeroDivisionError:
				context.user_data["temp"]["languages_group"] = 0
			context.user_data["temp"]["languages_groups"] = total_languages_count // 9 + (1 if total_languages_count % 9 > 0 else 0)
		
		start_languages_group = context.user_data["temp"]["languages_group"]
		
		if context.user_data["temp"]["languages_group"] > 0:
			context.user_data["temp"]["languages_group"] = context.user_data["temp"]["languages_group"] - 1
		else:
			context.user_data["temp"]["languages_group"] = context.user_data["temp"]["languages_groups"] - 1
		
		self.db_handler.users_data.update_last_state(
				update.effective_user.username,
				StateFlags.previous_languages_group,
				update.effective_message.message_id,
				context
		)
		
		if start_languages_group != context.user_data["temp"]["languages_group"]:
			await self.view_languages_group(update, context)
	
	async def set_language(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
		"""
        Sets the user's preferred language.

        This method handles the callback query to set the user's language preference.
        It extracts the language code from the callback data, updates the user's language in the database,
        updates the last state, and returns to the start panel.

        Args:
            update (Update): The Telegram update object.
            context (ContextTypes.DEFAULT_TYPE): The Telegram context object.
        """
		current_state = functions.get_current_state(context)
		
		if (
				current_state[0] not in [
					StateFlags.view_languages_group,
					StateFlags.next_languages_group,
					StateFlags.previous_languages_group
				] or current_state[1] != update.effective_message.message_id
		) and current_state[0] != "needed_language":
			await self.start_panel(update, context)
			return
		
		language_literal = re.search(r"set_language_(\w+?)\Z", update.callback_query.data).group(1)
		
		self.db_handler.users_data.update_language(update.effective_user.username, language_literal, context)
		self.db_handler.users_data.update_last_state(
				update.effective_user.username,
				StateFlags.view_languages_group,
				context.user_data.get("current_state", (None, None))[1],
				context
		)
		
		await self.start_panel(update, context)
	
	def get_callback_query_handlers(self) -> list[CallbackQueryHandler]:
		"""
        Returns a list of CallbackQueryHandlers for main bot interactions.

        Returns:
            list[CallbackQueryHandler]: A list of CallbackQueryHandler objects.
        """
		return list(
				sorted(
						[
							CallbackQueryHandler(callback=self.set_language, pattern=StateFlags.set_language),
							CallbackQueryHandler(callback=self.view_languages_group, pattern=StateFlags.view_languages_group),
							CallbackQueryHandler(callback=self.previous_languages_group, pattern=StateFlags.previous_languages_group),
							CallbackQueryHandler(callback=self.next_languages_group, pattern=StateFlags.next_languages_group),
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
        start_panel (start_panel_type): A function to display the start panel of the bot.
        get_user_context (get_user_context_type): A function to retrieve user-specific context data including user role.
        db_handler (MySQLDataHandler): An instance of the MySQLDataHandler for database operations.
        doc (dict[str, list[str]]): A list of strings representing the documentation content to be displayed. Each string can contain HTML formatting.

    :Usage:
        main_view = Main_view(start_panel_function, db_handler_instance, documentation_list)
        main_view.view_doc(update, context) # Display the documentation.
    """
	
	def __init__(
			self,
			start_panel: start_panel_type,
			get_user_context: get_user_context_type,
			db_handler: data_handlers.MySQLDataHandler,
			doc: dict[str, list[str]]
	):
		"""
        Initializes the Main_view class.

        Args:
            start_panel (start_panel_type): The function to display the bot's start panel.
            get_user_context (get_user_context_type): The function to retrieve user role information.
            db_handler (MySQLDataHandler): The database handler instance.
            doc (dict[str, list[str]]): Dictionary with documentations in few languages.
        """
		self.start_panel = start_panel
		self.get_user_context = get_user_context
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
		self.get_user_context(update, context)
		language = functions.get_language(context)
		
		if language is None:
			await self.start_panel(update, context)
			return
		
		for doc_item in self.doc[language]:
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
			main_local: MainLocalDict,
			others_local: OthersLocalDict,
			languages_dict: LanguagesDict,
			doc: dict[str, list[str]]
	):
		"""
        Initializes the Main_controls class. Combines main functionality view, handling, and messaging components.

        Args:
            start_panel (start_panel_type): Function to display the start panel.
            get_user_context (get_user_context_type): Function to get user context.
            db_handler (MySQLDataHandler): Database handler instance.
            main_local (MainLocalDict): Localized strings for main operations (handle, message).
            others_local (OthersLocalDict): Localized strings for general application use.
            languages_dict (LanguagesDict): Dictionary of available languages.
            doc (dict[str, list[str]]): Dictionary with documentations in few languages.
        """
		self.view = Main_view(start_panel, get_user_context, db_handler, doc)
		self.handle = Main_handle(start_panel, get_user_context, db_handler, main_local["handle"], others_local, languages_dict)
		self.message = Main_message(start_panel, get_user_context, db_handler, main_local["message"])
	
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
