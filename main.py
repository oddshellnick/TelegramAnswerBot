import logging
from TelegramAnswerBot.functions import build_hidden_files
from telegram import (
	InlineKeyboardButton,
	InlineKeyboardMarkup,
	Update
)
from TelegramAnswerBot import (
	data_handlers,
	functions,
	telegram_handlers
)
from telegram.ext import (
	ApplicationBuilder,
	CallbackQueryHandler,
	CommandHandler,
	ContextTypes,
	MessageHandler,
	filters
)


class AnswerBot:
	"""
    The main bot class that orchestrates all bot functionalities.

    This class initializes the database connection, various control instances for different bot features,
    and handles the main Telegram bot event loop.
    It manages user authentication, context, and delegates tasks to specialized handler classes.

    Attributes:
        settings (dict): settings for database and Telegram API.
        doc (list[str]): Documentation content to be displayed to users.
        db_handler (MySQLDataHandler): Instance for database operations.
        users_controls (Users_controls): Controls user management features.
        questions_controls (Questions_controls): Controls question management features.
        FAQs_controls (FAQs_controls): Controls FAQ management features.
        main_controls (Main_controls): Controls main bot functionalities (asking/answering questions and viewing documentation).
    """
	
	def __init__(self):
		"""Initializes the AnswerBot."""
		self.settings = functions.read_settings()
		self.doc = functions.read_doc()
		self.localizations = functions.read_localizations()
		
		self.db_handler = data_handlers.MySQLDataHandler(self.settings["MySQL_pool_config"])
		self.users_controls = telegram_handlers.users.Users_controls(
				self.start,
				self.get_user_context,
				self.db_handler,
				self.localizations["users"],
				self.localizations["others"],
				self.localizations["roles"]
		)
		self.questions_controls = telegram_handlers.questions.Questions_controls(
				self.start,
				self.get_user_context,
				self.db_handler,
				self.localizations["questions"],
				self.localizations["others"]
		)
		self.FAQs_controls = telegram_handlers.FAQs.FAQs_controls(
				self.start,
				self.get_user_context,
				self.db_handler,
				self.localizations["faq"],
				self.localizations["others"]
		)
		self.main_controls = telegram_handlers.main.Main_controls(
				self.start,
				self.get_user_context,
				self.db_handler,
				self.localizations["main"],
				self.localizations["others"],
				self.localizations["languages"],
				self.doc
		)
	
	def get_user_context(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
		"""
        Retrieves and sets user context data, including role and abilities.

        This function fetches user role and abilities from the database and updates the context with this information.
        It also handles loading additional user-specific data if the user has a role other than "user".
        This includes handling the addition of chat_id to the database.

        Args:
             update (Update): The Telegram update object.
             context (ContextTypes.DEFAULT_TYPE): The Telegram context object.
        """
		if not context.user_data.get("role", False):
			user = update.effective_user
		
			context.user_data["role"], initialized = self.db_handler.users_data.get_user_role(user.username)
			context.user_data["abilities"] = self.db_handler.users_data.get_role_abilities(context.user_data["role"])
		
			if initialized:
				context.user_data["language"] = self.db_handler.users_data.get_user_language(user.username)
		
				for key, value in self.db_handler.users_data.get_user_data(user.username)["user_context_data"].items():
					context.user_data[key] = value
			else:
				self.db_handler.users_data.add_user(user.username, context.user_data["role"])
		
			if context.user_data["abilities"]["receives_messages"]:
				if self.db_handler.users_data.get_user_chat_id(user.username) is None:
					self.db_handler.users_data.add_user_chat_id(user.username, update.effective_chat.id)
	
	async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
		"""
        Displays the main menu for the user based on their abilities.

        Args:
            update (Update): The Telegram update object.
            context (ContextTypes.DEFAULT_TYPE): The Telegram context object.
        """
		self.get_user_context(update, context)
		language = functions.get_language(context)
		context.user_data["temp"] = {}
		
		if language is None:
			self.db_handler.users_data.update_last_state(
					update.effective_user.username,
					"needed_language",
					context.user_data.get("current_state", (None, None))[1],
					context
			)
			await self.main_controls.handle.view_languages_group(update, context)
			return
		
		keyboard = []
		
		if context.user_data["abilities"]["able_to_faqs_handle"]:
			keyboard.append(
					[
						InlineKeyboardButton(
								self.localizations["start"][language]["handle_faq"],
								callback_data=telegram_handlers.FAQs.StateFlags.handle_faq
						)
					]
			)
		
		if context.user_data["abilities"]["able_to_faqs_view"]:
			keyboard.append(
					[
						InlineKeyboardButton(
								self.localizations["start"][language]["view_faq"],
								callback_data=telegram_handlers.FAQs.StateFlags.view_fags_group
						)
					]
			)
		
		if context.user_data["abilities"]["able_to_questions_handle"]:
			keyboard.append(
					[
						InlineKeyboardButton(
								self.localizations["start"][language]["handle_questions"],
								callback_data=telegram_handlers.questions.StateFlags.handle_questions
						)
					]
			)
		
		if context.user_data["abilities"]["able_to_questions_view"]:
			keyboard.append(
					[
						InlineKeyboardButton(
								self.localizations["start"][language]["view_questions"],
								callback_data=telegram_handlers.questions.StateFlags.view_questions
						)
					]
			)
		
		if context.user_data["abilities"]["able_to_users_handle"]:
			keyboard.append(
					[
						InlineKeyboardButton(
								self.localizations["start"][language]["handle_users"],
								callback_data=telegram_handlers.users.StateFlags.handle_users
						)
					]
			)
		
		if context.user_data["abilities"]["able_to_users_view"]:
			keyboard.append(
					[
						InlineKeyboardButton(
								self.localizations["start"][language]["view_users"],
								callback_data=telegram_handlers.users.StateFlags.view_users
						)
					]
			)
		
		if context.user_data["abilities"]["able_to_ask"]:
			keyboard.append(
					[
						InlineKeyboardButton(
								self.localizations["start"][language]["ask_question"],
								callback_data=telegram_handlers.main.StateFlags.ask_question
						)
					]
			)
		
		if context.user_data["abilities"]["able_to_answer"]:
			keyboard.append(
					[
						InlineKeyboardButton(
								self.localizations["start"][language]["answer_question"],
								callback_data=telegram_handlers.main.StateFlags.answer_question
						)
					]
			)
		
		keyboard.append(
				[
					InlineKeyboardButton("🤖", callback_data=telegram_handlers.main.StateFlags.view_doc),
					InlineKeyboardButton(
							self.localizations["start"][language]["chose_language"],
							callback_data=telegram_handlers.main.StateFlags.view_languages_group
					)
				]
		)
		
		reply_markup = InlineKeyboardMarkup(keyboard)
		
		message = await functions.edit_message(
				message_to_edit=functions.get_current_state(context)[1],
				text=self.localizations["start"][language]["mode_choice"],
				update=update,
				context=context,
				reply_markup=reply_markup
		)
		
		self.db_handler.users_data.update_last_state(update.effective_user.username, "start", message.message_id, context)
	
	async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
		"""
        Handles incoming text messages from users.

        Delegates message handling to the appropriate control class based on the current state.

        Args:
            update (Update): The Telegram update object.
            context (ContextTypes.DEFAULT_TYPE): The Telegram context object.
        """
		self.get_user_context(update, context)
		current_state = functions.get_current_state(context)
		
		if current_state[0] == telegram_handlers.main.StateFlags.ask_question:
			await self.main_controls.message.input_question(update, context)
		elif current_state[0] == telegram_handlers.main.StateFlags.reply_to_question:
			await self.main_controls.message.input_answer(update, context)
		elif current_state[0] == telegram_handlers.questions.StateFlags.view_questions_list:
			await self.questions_controls.message.input_number_of_questions_to_view(update, context)
		elif current_state[0] == telegram_handlers.users.StateFlags.chose_user_to_add_role:
			await self.users_controls.message.input_username_to_add_role(update, context)
		elif current_state[0] == telegram_handlers.users.StateFlags.remove_user_role:
			await self.users_controls.message.input_username_to_remove_role(update, context)
		elif current_state[0] == telegram_handlers.FAQs.StateFlags.add_faq:
			await self.FAQs_controls.message.input_faq_text(update, context)
		elif current_state[0] == telegram_handlers.FAQs.StateFlags.input_faq_text:
			await self.FAQs_controls.message.input_faq_answer(update, context)
		elif current_state[0] == telegram_handlers.FAQs.StateFlags.remove_faq:
			await self.FAQs_controls.message.input_faq_id_to_delete(update, context)
		elif current_state[0] == telegram_handlers.FAQs.StateFlags.edit_faq:
			await self.FAQs_controls.message.input_faq_id_to_edit(update, context)
		elif current_state[0] in [telegram_handlers.FAQs.StateFlags.edit_faq_text, telegram_handlers.FAQs.StateFlags.edit_faq_answer]:
			await self.FAQs_controls.message.input_faq_instance_to_edit(update, context)
		
		if not context.user_data.get("processing", False):
			await self.start(update, context)
	
	def get_callback_query_handlers(self) -> list[CallbackQueryHandler]:
		"""
        Returns a combined list of all callback query handlers.

        Returns:
            list[CallbackQueryHandler]: A list of CallbackQueryHandler instances for all features.
        """
		return list(
				sorted(
						self.main_controls.get_callback_query_handlers() +
						self.users_controls.get_callback_query_handlers() +
						self.questions_controls.get_callback_query_handlers() +
						self.FAQs_controls.get_callback_query_handlers() +
						[CallbackQueryHandler(self.start, pattern="start")],
						key=lambda x: len(x.pattern.pattern),
						reverse=True
				)
		)
	
	def run(self):
		"""Starts the bot's main loop."""
		application = ApplicationBuilder().token(self.settings["telegram_token"]).build()
		application.add_handler(CommandHandler("start", self.start))
		
		for handler in self.get_callback_query_handlers():
			application.add_handler(handler)
		
		application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
		application.run_polling()


logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

if __name__ == "__main__":
	hidden_files_built = build_hidden_files()

	if len(hidden_files_built) == 0:
		answer_bot = AnswerBot()
		answer_bot.run()
	else:
		message = f"Some hidden files were created:\n- {'\n- '.join(str(path.relative_to(".")) for path in hidden_files_built)}\n\nFill them with your data."
		print(message)
