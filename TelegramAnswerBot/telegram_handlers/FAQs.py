import re
from dataclasses import dataclass
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
	FaqHandleLocalDict,
	FaqLocalDict,
	FaqMessageLocalDict,
	FaqViewLocalDict,
	OthersLocalDict,
	get_user_context_type,
	start_panel_type
)


@dataclass(frozen=True)
class StateFlags:
	"""
	Constants representing the different states within the FAQ management workflow.

	This class defines string constants to represent the various stages involved in managing FAQs (Frequently Asked Questions).
	These constants are used to track the current state of interaction with the user,
	allowing the bot to maintain context and respond appropriately during different phases of FAQ management,
	including adding, removing, editing, and viewing FAQs.

	Attributes:
		input_faq_text (str): State for inputting the text of a new FAQ.
		input_faq_answer (str): State for inputting the answer to a new FAQ.
		add_faq (str): State for adding a new FAQ.

		input_faq_id_to_delete (str): State for inputting the ID of an FAQ to delete.
		remove_faq (str): State for removing an FAQ.

		clear_faq_confirmation (str): State for confirming the clearing of all FAQs.
		clear_faq_request (str): State for requesting confirmation to clear all FAQs.

		edit_faq_answer (str): State for editing the answer of an FAQ.
		edit_faq_text (str): State for editing the text of an FAQ.
		input_faq_instance_to_edit (str): State for inputting the content to edit an FAQ.
		input_faq_id_to_edit (str): State for inputting the ID of the FAQ to edit.
		edit_faq (str): State for initiating the FAQ editing process.

		handle_faq (str): The main state for handling FAQ-related operations.

		previous_fags_group (str): State for navigating to the previous group of FAQs.
		next_fags_group (str): State for navigating to the next group of FAQs.
		view_fag_answer (str): State for viewing the answer to a specific FAQ.
		view_fags_group (str): State for viewing a group of FAQs.
	"""
	input_faq_text = "input_faq_text"
	input_faq_answer = "input_faq_answer"
	add_faq = "add_faq"
	
	input_faq_id_to_delete = "input_faq_id_to_delete"
	remove_faq = "remove_faq"
	
	clear_faq_confirmation = "clear_faq_confirmation"
	clear_faq_request = "clear_faq_request"
	
	edit_faq_answer = "edit_faq_answer"
	edit_faq_text = "edit_faq_text"
	input_faq_instance_to_edit = "input_faq_instance_to_edit"
	input_faq_id_to_edit = "input_faq_id_to_edit"
	edit_faq = "edit_faq"
	
	handle_faq = "handle_faq"
	
	previous_fags_group = "previous_fags_group"
	next_fags_group = "next_fags_group"
	view_fag_answer = "view_fag_answer"
	view_fags_group = "view_fags_group"


class FAQs_message:
	"""
	Handles message-based interactions related to FAQs.

	This class manages text-based interactions with users concerning FAQs, potentially including
	processes like reporting issues or providing feedback on FAQs.
	It uses localized strings for better internationalization.

	Attributes:
		start_panel (function): A function to display the start panel of the bot.
		get_user_context (function): Function to retrieve user context.
		db_handler (MySQLDataHandler): An instance of the MySQLDataHandler for database operations.
		faq_local (FaqViewLocalDict): Localized strings specific to FAQ view operations.
		others_local (OthersLocalDict): Localized strings for general application use.
	"""
	
	def __init__(
			self,
			start_panel: start_panel_type,
			get_user_context: get_user_context_type,
			db_handler: data_handlers.MySQLDataHandler,
			faq_local: FaqMessageLocalDict,
			others_local: OthersLocalDict
	):
		"""
		Initializes the FAQs_message handler.

		Args:
			start_panel (start_panel_type): Function to return to the start panel.
			get_user_context (get_user_context_type): Function to retrieve user context.
			db_handler (data_handlers.MySQLDataHandler): The database handler for interacting with the database.
			faq_local (FaqMessageLocalDict): Localized strings specific to FAQ message operations.
			others_local (OthersLocalDict): Localized strings for general application use.
		"""
		self.start_panel = start_panel
		self.get_user_context = get_user_context
		self.db_handler = db_handler
		self.faq_local = faq_local
		self.others_local = others_local
	
	async def input_faq_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
		"""
		Handles the input of an answer for a new FAQ.

		Args:
			update (Update): The Telegram update object.
			context (ContextTypes.DEFAULT_TYPE): The Telegram bot context.
		"""
		self.get_user_context(update, context)
		language = functions.get_language(context)
		
		if language is None:
			await self.start_panel(update, context)
			return
		
		faq_question_answer = update.message.text
		new_faq_id = context.user_data["temp"]["new_faq_id"]
		
		self.db_handler.faqs_data.change_fag_answer(new_faq_id, faq_question_answer)
		
		await context.bot.send_message(
				chat_id=update.effective_chat.id,
				text=self.faq_local[language]["new_faq_saved_notification"]
		)
		
		context.user_data["temp"] = {}
		context.user_data.pop("processing")
		self.db_handler.users_data.update_last_state(
				update.effective_user.username,
				StateFlags.input_faq_answer,
				None,
				context
		)
	
	async def input_faq_id_to_delete(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
		"""
		Handles the input of an id for a FAQ answer to delete.

		Args:
			update (Update): The Telegram update object.
			context (ContextTypes.DEFAULT_TYPE): The Telegram bot context.
		"""
		self.get_user_context(update, context)
		language = functions.get_language(context)
		
		if language is None:
			await self.start_panel(update, context)
			return
		
		try:
			faq_id = int(update.message.text)
		except ValueError:
			await context.bot.send_message(
					chat_id=update.effective_chat.id,
					text=self.others_local[language]["integer_needed_warning"]
			)
		else:
			if not self.db_handler.faqs_data.check_faq_exists(faq_id):
				await context.bot.send_message(
						chat_id=update.effective_chat.id,
						text=self.faq_local[language]["no_faq_with_id_warning"].format(id=faq_id)
				)
			else:
				self.db_handler.faqs_data.delete_faq(faq_id)
		
				await context.bot.send_message(
						chat_id=update.effective_chat.id,
						text=self.faq_local[language]["faq_with_id_deleted_confirmation"].format(id=faq_id)
				)
		finally:
			context.user_data.pop("processing")
			self.db_handler.users_data.update_last_state(
					update.effective_user.username,
					StateFlags.input_faq_id_to_delete,
					None,
					context
			)
	
	async def input_faq_id_to_edit(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
		"""
		Handles the input of an id for a FAQ answer to edit.

		Args:
			update (Update): The Telegram update object.
			context (ContextTypes.DEFAULT_TYPE): The Telegram bot context.
		"""
		self.get_user_context(update, context)
		language = functions.get_language(context)
		
		if language is None:
			await self.start_panel(update, context)
			return
		
		try:
			faq_id = int(update.message.text)
		except ValueError:
			await context.bot.send_message(
					chat_id=update.effective_chat.id,
					text=self.others_local[language]["integer_needed_warning"]
			)
		
			context.user_data.pop("processing")
			self.db_handler.users_data.update_last_state(
					update.effective_user.username,
					StateFlags.input_faq_id_to_edit,
					None,
					context
			)
		else:
			if not self.db_handler.faqs_data.check_faq_exists(faq_id):
				await context.bot.send_message(
						chat_id=update.effective_chat.id,
						text=self.faq_local[language]["no_faq_with_id_warning"].format(id=faq_id)
				)
		
				context.user_data.pop("processing")
				self.db_handler.users_data.update_last_state(
						update.effective_user.username,
						StateFlags.input_faq_id_to_edit,
						None,
						context
				)
			else:
				context.user_data["temp"]["faq_edit_id"] = faq_id
		
				keyboard = [
					[
						InlineKeyboardButton(
								self.faq_local[language]["faq_question_choice_button"],
								callback_data=StateFlags.edit_faq_text
						)
					],
					[
						InlineKeyboardButton(
								self.faq_local[language]["faq_answer_choice_button"],
								callback_data=StateFlags.edit_faq_answer
						)
					]
				]
				reply_markup = InlineKeyboardMarkup(keyboard)
		
				message = await context.bot.send_message(
						chat_id=update.effective_chat.id,
						text=self.others_local[language]["faq_instance_choice_suggestion"],
						reply_markup=reply_markup
				)
				self.db_handler.users_data.update_last_state(
						update.effective_user.username,
						StateFlags.input_faq_id_to_edit,
						message.message_id,
						context
				)
	
	async def input_faq_instance_to_edit(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
		"""
		Handles the input of an instance for a FAQ answer to edit.

		Args:
			update (Update): The Telegram update object.
			context (ContextTypes.DEFAULT_TYPE): The Telegram bot context.
		"""
		self.get_user_context(update, context)
		language = functions.get_language(context)
		
		if language is None:
			await self.start_panel(update, context)
			return
		
		faq_edit_id = context.user_data["temp"]["faq_edit_id"]
		faq_edit_instance = context.user_data["temp"]["faq_edit_instance"]
		faq_instance_text = update.message.text
		
		if faq_edit_instance == "answer":
			self.db_handler.faqs_data.change_fag_answer(faq_edit_id, faq_instance_text)
		elif faq_edit_instance == "question":
			self.db_handler.faqs_data.change_fag_question(faq_edit_id, faq_instance_text)
		else:
			raise ValueError(f"Unknown faq_edit_instance: {faq_edit_instance}")
		
		await context.bot.send_message(
				chat_id=update.effective_chat.id,
				text=self.others_local[language]["faq_instance_changed_confirmation"]
		)
		
		context.user_data["temp"] = {}
		context.user_data.pop("processing")
		self.db_handler.users_data.update_last_state(
				update.effective_user.username,
				StateFlags.input_faq_instance_to_edit,
				None,
				context
		)
	
	async def input_faq_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
		"""
		Handles the input of a FAQ text.

		Args:
			update (Update): The Telegram update object.
			context (ContextTypes.DEFAULT_TYPE): The Telegram bot context.
		"""
		self.get_user_context(update, context)
		language = functions.get_language(context)
		
		if language is None:
			await self.start_panel(update, context)
			return
		
		faq_question_text = update.message.text
		new_faq_id = self.db_handler.faqs_data.add_faq(faq_question_text, "")
		
		await context.bot.send_message(
				chat_id=update.effective_chat.id,
				text=self.others_local[language]["input_faq_answer_suggestion"]
		)
		
		context.user_data["temp"]["new_faq_id"] = new_faq_id
		self.db_handler.users_data.update_last_state(
				update.effective_user.username,
				StateFlags.input_faq_text,
				None,
				context
		)


class FAQs_handle:
	"""
	Handles callback query-based interactions related to FAQ management.

	This class manages actions such as adding, deleting, editing, and clearing FAQs.

	Attributes:
		start_panel (function): A function to display the start panel of the bot.
		get_user_context (function): A function to retrieve user context.
		db_handler (MySQLDataHandler): An instance of the MySQLDataHandler for database operations.
		faq_local (FaqHandleLocalDict): Localized strings specific to FAQ handle operations.
		others_local (OthersLocalDict): Localized strings for general application use.
	"""
	
	def __init__(
			self,
			start_panel: start_panel_type,
			get_user_context: get_user_context_type,
			db_handler: data_handlers.MySQLDataHandler,
			faq_local: FaqHandleLocalDict,
			others_local: OthersLocalDict
	):
		"""
		Initializes the FAQs_handle.

		Args:
			start_panel (start_panel_type): The function to call to display the start panel.
			get_user_context (get_user_context_type): The function to retrieve user context.
			db_handler (data_handlers.MySQLDataHandler): The database handler.
			faq_local (FaqHandleLocalDict): Localized strings specific to FAQ handling operations.
			others_local (OthersLocalDict): Localized strings for general application use.
		"""
		self.start_panel = start_panel
		self.get_user_context = get_user_context
		self.db_handler = db_handler
		self.faq_local = faq_local
		self.others_local = others_local
	
	async def clear_faq_confirmation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
		"""
		Handles the confirmation of clearing the FAQ. Clears all FAQs if the user has the required permissions and the state is valid.

		Args:
			update (Update): The Telegram update object.
			context (ContextTypes.DEFAULT_TYPE): The Telegram bot context.
		"""
		self.get_user_context(update, context)
		language = functions.get_language(context)
		
		if language is None:
			await self.start_panel(update, context)
			return
		
		current_state = functions.get_current_state(context)
		if current_state[0] not in [StateFlags.clear_faq_request] or current_state[1] != update.effective_message.message_id:
			await self.start_panel(update, context)
			return
		
		if not context.user_data["abilities"]["able_to_faqs_handle"]:
			await functions.warning_rights_error(
					self.faq_local[language]["cant_clear_faq_warning"],
					self.start_panel,
					update,
					context
			)
			return
		
		self.db_handler.faqs_data.clear_faqs()
		
		await update.effective_message.edit_text(text=self.faq_local[language]["faq_cleared_notification"])
		
		self.db_handler.users_data.update_last_state(
				update.effective_user.username,
				StateFlags.clear_faq_confirmation,
				None,
				context
		)
		
		await self.start_panel(update, context)
	
	async def clear_faq_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
		"""
		Handles the request to clear the FAQ. Presents a confirmation button to the user if they have the necessary permissions and the current state is valid.

		Args:
			update (Update): The Telegram update object.
			context (ContextTypes.DEFAULT_TYPE): The Telegram bot context.
		"""
		self.get_user_context(update, context)
		language = functions.get_language(context)
		
		if language is None:
			await self.start_panel(update, context)
			return
		
		current_state = functions.get_current_state(context)
		if current_state[0] not in [StateFlags.handle_faq] or current_state[1] != update.effective_message.message_id:
			await self.start_panel(update, context)
			return
		
		if not context.user_data["abilities"]["able_to_faqs_handle"]:
			await functions.warning_rights_error(
					self.faq_local[language]["cant_clear_faq_warning"],
					self.start_panel,
					update,
					context
			)
			return
		
		keyboard = [
			[
				InlineKeyboardButton(
						self.faq_local[language]["faq_clear_button"],
						callback_data=StateFlags.clear_faq_confirmation
				)
			],
			[
				InlineKeyboardButton(
						self.others_local[language]["decline_button"],
						callback_data=StateFlags.handle_faq
				)
			]
		]
		reply_markup = InlineKeyboardMarkup(keyboard)
		
		message = await update.effective_message.edit_text(
				text=self.faq_local[language]["faq_clear_aware"],
				reply_markup=reply_markup
		)
		
		self.db_handler.users_data.update_last_state(
				update.effective_user.username,
				StateFlags.clear_faq_request,
				message.message_id,
				context
		)
		context.user_data["processing"] = True
	
	async def edit_faq_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
		"""
		Handles the editing of an FAQ answer. Prompts the user for the new answer text.

		Args:
			update (Update): The Telegram update object.
			context (ContextTypes.DEFAULT_TYPE): The Telegram bot context.
		"""
		self.get_user_context(update, context)
		language = functions.get_language(context)
		
		if language is None:
			await self.start_panel(update, context)
			return
		
		current_state = functions.get_current_state(context)
		if current_state[0] not in [StateFlags.input_faq_id_to_edit] or current_state[1] != update.effective_message.message_id:
			await self.start_panel(update, context)
			return
		
		if not context.user_data["abilities"]["able_to_faqs_handle"]:
			await functions.warning_rights_error(
					self.faq_local[language]["cant_faq_edit_warning"],
					self.start_panel,
					update,
					context
			)
			return
		
		await update.effective_message.edit_text(text=self.faq_local[language]["input_faq_new_answer_suggestion"])
		
		self.db_handler.users_data.update_last_state(
				update.effective_user.username,
				StateFlags.edit_faq_answer,
				None,
				context
		)
		context.user_data["temp"]["faq_edit_instance"] = "answer"
		context.user_data["processing"] = True
	
	async def edit_faq_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
		"""
		Handles the editing of an FAQ question text. Prompts the user for the new question text.

		Args:
			update (Update): The Telegram update object.
			context (ContextTypes.DEFAULT_TYPE): The Telegram bot context.
		"""
		self.get_user_context(update, context)
		language = functions.get_language(context)
		
		if language is None:
			await self.start_panel(update, context)
			return
		
		current_state = functions.get_current_state(context)
		if current_state[0] not in [StateFlags.input_faq_id_to_edit] or current_state[1] != update.effective_message.message_id:
			await self.start_panel(update, context)
			return
		
		if not context.user_data["abilities"]["able_to_faqs_handle"]:
			await functions.warning_rights_error(
					self.faq_local[language]["cant_faq_edit_warning"],
					self.start_panel,
					update,
					context
			)
			return
		
		await update.effective_message.edit_text(text=self.faq_local[language]["input_faq_new_question_suggestion"])
		
		self.db_handler.users_data.update_last_state(
				update.effective_user.username,
				StateFlags.edit_faq_text,
				None,
				context
		)
		context.user_data["temp"]["faq_edit_instance"] = "question"
		context.user_data["processing"] = True
	
	async def edit_faq(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
		"""
		Handles the initiation of the FAQ editing process. Prompts the user for the FAQ ID to edit.

		Args:
			update (Update): The Telegram update object.
			context (ContextTypes.DEFAULT_TYPE): The Telegram bot context.
		"""
		self.get_user_context(update, context)
		language = functions.get_language(context)
		
		if language is None:
			await self.start_panel(update, context)
			return
		
		current_state = functions.get_current_state(context)
		if current_state[0] not in [StateFlags.handle_faq] or current_state[1] != update.effective_message.message_id:
			await self.start_panel(update, context)
			return
		
		if not context.user_data["abilities"]["able_to_faqs_handle"]:
			await functions.warning_rights_error(
					self.faq_local[language]["cant_faq_edit_warning"],
					self.start_panel,
					update,
					context
			)
			return
		
		reply_markup = InlineKeyboardMarkup(
				[
					[
						InlineKeyboardButton(
								self.others_local[language]["decline_button"],
								callback_data=StateFlags.handle_faq
						)
					]
				]
		)
		
		message = await update.effective_message.edit_text(
				text=self.faq_local[language]["input_faq_id_to_edit_suggestion"],
				reply_markup=reply_markup
		)
		
		self.db_handler.users_data.update_last_state(
				update.effective_user.username,
				StateFlags.edit_faq,
				message.message_id,
				context
		)
		context.user_data["processing"] = True
	
	async def remove_faq(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
		"""
		Handles the removal of an FAQ. Prompts the user for the FAQ ID to remove.

		Args:
			update (Update): The Telegram update object.
			context (ContextTypes.DEFAULT_TYPE): The Telegram bot context.
		"""
		self.get_user_context(update, context)
		language = functions.get_language(context)
		
		if language is None:
			await self.start_panel(update, context)
			return
		
		current_state = functions.get_current_state(context)
		if current_state[0] not in [StateFlags.handle_faq] or current_state[1] != update.effective_message.message_id:
			await self.start_panel(update, context)
			return
		
		if not context.user_data["abilities"]["able_to_faqs_handle"]:
			await functions.warning_rights_error(
					self.faq_local[language]["cant_faq_delete_warning"],
					self.start_panel,
					update,
					context
			)
			return
		
		reply_markup = InlineKeyboardMarkup(
				[
					[
						InlineKeyboardButton(
								self.others_local[language]["decline_button"],
								callback_data=StateFlags.handle_faq
						)
					]
				]
		)
		
		message = await update.effective_message.edit_text(
				text=self.faq_local[language]["input_faq_id_to_delete_suggestion"],
				reply_markup=reply_markup
		)
		
		self.db_handler.users_data.update_last_state(
				update.effective_user.username,
				StateFlags.remove_faq,
				message.message_id,
				context
		)
		context.user_data["processing"] = True
	
	async def add_faq(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
		"""
		Handles the addition of a new FAQ. Prompts the user for the question text.

		Args:
			update (Update): The Telegram update object.
			context (ContextTypes.DEFAULT_TYPE): The Telegram bot context.
		"""
		self.get_user_context(update, context)
		language = functions.get_language(context)
		
		if language is None:
			await self.start_panel(update, context)
			return
		
		current_state = functions.get_current_state(context)
		if current_state[0] not in [StateFlags.handle_faq] or current_state[1] != update.effective_message.message_id:
			await self.start_panel(update, context)
			return
		
		if not context.user_data["abilities"]["able_to_faqs_handle"]:
			await functions.warning_rights_error(
					self.faq_local[language]["cant_create_faq_warning"],
					self.start_panel,
					update,
					context
			)
			return
		
		reply_markup = InlineKeyboardMarkup(
				[
					[
						InlineKeyboardButton(
								self.others_local[language]["decline_button"],
								callback_data=StateFlags.handle_faq
						)
					]
				]
		)
		
		message = await update.effective_message.edit_text(
				text=self.faq_local[language]["input_faq_question_suggestion"],
				reply_markup=reply_markup
		)
		
		self.db_handler.users_data.update_last_state(
				update.effective_user.username,
				StateFlags.add_faq,
				message.message_id,
				context
		)
		context.user_data["processing"] = True
	
	async def handle_faq(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
		"""
		Presents the main FAQ management menu to the user, allowing them to choose actions like adding, deleting, editing, or clearing FAQs.

		Args:
			update (Update): The Telegram update object.
			context (ContextTypes.DEFAULT_TYPE): The Telegram bot context.
		"""
		self.get_user_context(update, context)
		language = functions.get_language(context)
		
		if language is None:
			await self.start_panel(update, context)
			return
		
		current_state = functions.get_current_state(context)
		if current_state[0] not in [
			"start",
			StateFlags.add_faq,
			StateFlags.remove_faq,
			StateFlags.edit_faq,
			StateFlags.clear_faq_request
		] or current_state[1] != update.effective_message.message_id:
			await self.start_panel(update, context)
			return
		
		if not context.user_data["abilities"]["able_to_faqs_handle"]:
			await functions.warning_rights_error(
					self.others_local[language]["cant_handle_faq_warning"],
					self.start_panel,
					update,
					context
			)
			return
		
		keyboard = [
			[
				InlineKeyboardButton(
						self.faq_local[language]["create_faq_button"],
						callback_data=StateFlags.add_faq
				)
			],
			[
				InlineKeyboardButton(
						self.faq_local[language]["delete_faq_button"],
						callback_data=StateFlags.remove_faq
				)
			],
			[
				InlineKeyboardButton(
						self.faq_local[language]["edit_faq_button"],
						callback_data=StateFlags.edit_faq
				)
			],
			[
				InlineKeyboardButton(
						self.faq_local[language]["faq_clear_button"],
						callback_data=StateFlags.clear_faq_request
				)
			],
			[
				InlineKeyboardButton(self.others_local[language]["back_button"], callback_data="start")
			]
		]
		reply_markup = InlineKeyboardMarkup(keyboard)
		
		message = await functions.edit_message(
				message_to_edit=current_state[1],
				text=self.faq_local[language]["faq_handle_choice"],
				update=update,
				context=context,
				reply_markup=reply_markup
		)
		
		self.db_handler.users_data.update_last_state(
				update.effective_user.username,
				StateFlags.handle_faq,
				message.message_id,
				context
		)
		context.user_data["processing"] = True
	
	def get_callback_query_handlers(self) -> list[CallbackQueryHandler]:
		"""
		Returns a list of callback query handlers for FAQ management actions.

		Returns:
			 list[CallbackQueryHandler]: A list of CallbackQueryHandler objects.
		"""
		return list(
				sorted(
						[
							CallbackQueryHandler(self.handle_faq, pattern=StateFlags.handle_faq),
							CallbackQueryHandler(self.add_faq, pattern=StateFlags.add_faq),
							CallbackQueryHandler(self.remove_faq, pattern=StateFlags.remove_faq),
							CallbackQueryHandler(self.edit_faq, pattern=StateFlags.edit_faq),
							CallbackQueryHandler(self.edit_faq_text, pattern=StateFlags.edit_faq_text),
							CallbackQueryHandler(self.edit_faq_answer, pattern=StateFlags.edit_faq_answer),
							CallbackQueryHandler(self.clear_faq_request, pattern=StateFlags.clear_faq_request),
							CallbackQueryHandler(self.clear_faq_confirmation, pattern=StateFlags.clear_faq_confirmation)
						],
						key=lambda x: len(x.pattern.pattern),
						reverse=True
				)
		)


class FAQs_view:
	"""
	Handles user interaction with Frequently Asked Questions (FAQs).

	This class manages the display and navigation of FAQs, allowing users to view groups of FAQs,
	navigate between groups, and view individual FAQ answers.
	It uses localized strings for better internationalization.

	Attributes:
		start_panel (function): A function to display the start panel of the bot.
		get_user_context (function): A function to retrieve user context.
		db_handler (MySQLDataHandler): An instance of the MySQLDataHandler for database operations.
		faq_local (FaqViewLocalDict): Localized strings specific to FAQ view operations.
		others_local (OthersLocalDict): Localized strings for general application use.
	"""
	
	def __init__(
			self,
			start_panel: start_panel_type,
			get_user_context: get_user_context_type,
			db_handler: data_handlers.MySQLDataHandler,
			faq_local: FaqViewLocalDict,
			others_local: OthersLocalDict
	):
		"""
		Initializes the FAQs_view class.

		Args:
			start_panel (function): The function to display the bot's start panel.
			get_user_context (function): The function to retrieve user-specific context data.
			db_handler (MySQLDataHandler): The data handler for database interaction.
			faq_local (FaqViewLocalDict): Localized strings for FAQ view.
			others_local (OthersLocalDict): Localized strings for general use.
		"""
		self.start_panel = start_panel
		self.get_user_context = get_user_context
		self.db_handler = db_handler
		self.faq_local = faq_local
		self.others_local = others_local
	
	async def view_faqs_group(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
		"""
		Displays a group of FAQs to the user.

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
		if current_state[0] not in ["start", StateFlags.next_fags_group, StateFlags.previous_fags_group] or current_state[1] != update.effective_message.message_id:
			await self.start_panel(update, context)
			return
		
		if context.user_data["temp"].get("faq_group", None) is None:
			total_faqs_count = self.db_handler.faqs_data.get_total_faqs_count()
		
			context.user_data["temp"]["faq_group"] = 0
			context.user_data["temp"]["faq_groups"] = total_faqs_count // 9 + (1 if total_faqs_count % 9 > 0 else 0)
		
		faqs_group_data = self.db_handler.faqs_data.get_faq_group(9, context.user_data["temp"]["faq_group"] * 9)
		
		keyboard = [
			[
				InlineKeyboardButton(
						f"{row['faq_id']}. {row['question']}",
						callback_data=f"{StateFlags.view_fag_answer}_id{row['faq_id']}"
				)
			]
			for index, row in faqs_group_data.iterrows()
		]
		keyboard.append(
				[
					InlineKeyboardButton("<<", callback_data=StateFlags.previous_fags_group),
					InlineKeyboardButton(self.others_local[language]["back_button"], callback_data="start"),
					InlineKeyboardButton(">>", callback_data=StateFlags.next_fags_group)
				]
		)
		reply_markup = InlineKeyboardMarkup(keyboard)
		
		message = await functions.edit_message(
				current_state[1],
				self.faq_local[language]["faq_choice_suggestion"],
				update,
				context,
				reply_markup=reply_markup
		)
		
		self.db_handler.users_data.update_last_state(
				update.effective_user.username,
				StateFlags.view_fags_group,
				message.message_id,
				context
		)
	
	async def next_faqs_group(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
		"""
		Navigates to the next group of FAQs.

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
		if current_state[0] not in [
			StateFlags.view_fags_group,
			StateFlags.next_fags_group,
			StateFlags.previous_fags_group
		] or current_state[1] != update.effective_message.message_id:
			await self.start_panel(update, context)
			return
		
		if context.user_data["temp"].get("faq_group", None) is None:
			total_faqs_count = self.db_handler.faqs_data.get_total_faqs_count()
		
			context.user_data["temp"]["faq_group"] = 0
			context.user_data["temp"]["faq_groups"] = total_faqs_count // 9 + (1 if total_faqs_count % 9 > 0 else 0)
		
		start_faq_group = context.user_data["temp"]["faq_group"]
		
		try:
			context.user_data["temp"]["faq_group"] = (context.user_data["temp"]["faq_group"] + 1) % context.user_data["temp"]["faq_groups"]
		except ZeroDivisionError:
			context.user_data["temp"]["faq_group"] = 0
		self.db_handler.users_data.update_last_state(
				update.effective_user.username,
				StateFlags.next_fags_group,
				update.effective_message.message_id,
				context
		)
		
		if start_faq_group != context.user_data["temp"]["faq_group"]:
			await self.view_faqs_group(update, context)
	
	async def previous_faqs_group(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
		"""
		Navigates to the previous group of FAQs.

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
		if current_state[0] not in [
			StateFlags.view_fags_group,
			StateFlags.next_fags_group,
			StateFlags.previous_fags_group
		] or current_state[1] != update.effective_message.message_id:
			await self.start_panel(update, context)
			return
		
		if context.user_data["temp"].get("faq_group", None) is None:
			total_faqs_count = self.db_handler.faqs_data.get_total_faqs_count()
		
			try:
				context.user_data["temp"]["faq_group"] = (context.user_data["temp"]["faq_group"] + 1) % context.user_data["temp"]["faq_groups"]
			except ZeroDivisionError:
				context.user_data["temp"]["faq_group"] = 0
			context.user_data["temp"]["faq_groups"] = total_faqs_count // 9 + (1 if total_faqs_count % 9 > 0 else 0)
		
		start_faqs_group = context.user_data["temp"]["faq_group"]
		
		if context.user_data["temp"]["faq_group"] > 0:
			context.user_data["temp"]["faq_group"] = context.user_data["temp"]["faq_group"] - 1
		else:
			context.user_data["temp"]["faq_group"] = context.user_data["temp"]["faq_groups"] - 1
		
		self.db_handler.users_data.update_last_state(
				update.effective_user.username,
				StateFlags.previous_fags_group,
				update.effective_message.message_id,
				context
		)
		
		if start_faqs_group != context.user_data["temp"]["faq_group"]:
			await self.view_faqs_group(update, context)
	
	async def view_faq_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
		"""
		Displays the answer to a specific FAQ.

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
		if current_state[0] not in [
			StateFlags.view_fags_group,
			StateFlags.next_fags_group,
			StateFlags.previous_fags_group
		] or current_state[1] != update.effective_message.message_id:
			await self.start_panel(update, context)
			return
		
		faq_id = int(re.search(r"_id(\d+)\Z", update.callback_query.data).group(1))
		faq_line = self.db_handler.faqs_data.get_faq(faq_id)
		
		await update.effective_message.edit_text(
				text=self.faq_local[language]["faq_view"].format(
						question=faq_line['question'],
						answer=faq_line['answer'],
						views_count=faq_line['views_count']
				)
		)
		
		self.db_handler.users_data.update_last_state(
				update.effective_user.username,
				StateFlags.view_fag_answer,
				None,
				context
		)
		
		await self.start_panel(update, context)
	
	def get_callback_query_handlers(self) -> list[CallbackQueryHandler]:
		"""
		Returns a list of CallbackQueryHandlers for FAQs interaction.

		Returns:
			list[CallbackQueryHandler]: A list of CallbackQueryHandler objects.
		"""
		return list(
				sorted(
						[
							CallbackQueryHandler(callback=self.view_faqs_group, pattern=StateFlags.view_fags_group),
							CallbackQueryHandler(callback=self.view_faq_answer, pattern=StateFlags.view_fag_answer),
							CallbackQueryHandler(
									callback=self.previous_faqs_group,
									pattern=StateFlags.previous_fags_group
							),
							CallbackQueryHandler(callback=self.next_faqs_group, pattern=StateFlags.next_fags_group)
						],
						key=lambda x: len(x.pattern.pattern),
						reverse=True
				)
		)


class FAQs_controls:
	"""
	Manages the control flow and interactions related to FAQs.

	This class acts as a central controller, combining the functionalities of FAQs_view, FAQs_handle, and FAQs_message.
	It provides a unified interface for handling user interactions with FAQs, including viewing, managing, and messaging.

	Attributes:
		view (FAQs_view): An instance of the FAQs_view class for displaying FAQs.
		handle (FAQs_handle): An instance of the FAQs_handle class for managing FAQs.
		message (FAQs_message): An instance of the FAQs_message class for messaging related to FAQs.

	:Usage:
		faq_controls = FAQs_controls(start_panel_function, get_user_context_function, db_handler_instance)
		handlers = faq_controls.get_callback_query_handlers() # Retrieve all FAQ related handlers
	"""
	
	def __init__(
			self,
			start_panel: start_panel_type,
			get_user_context: get_user_context_type,
			db_handler: data_handlers.MySQLDataHandler,
			faq_local: FaqLocalDict,
			others_local: OthersLocalDict
	):
		"""
		Initializes the FAQs_controls class.

		Args:
			start_panel (function): The function to display the bot's start panel.
			get_user_context (function): The function to retrieve user-specific context data.
			db_handler (MySQLDataHandler): The data handler for database interaction.
			faq_local (FaqLocalDict): A dictionary containing localized data for FAQ-related messages.
			others_local (OthersLocalDict): A dictionary containing other localized strings used in the application.
		"""
		self.view = FAQs_view(
				start_panel,
				get_user_context,
				db_handler,
				faq_local["view"],
				others_local
		)
		
		self.handle = FAQs_handle(
				start_panel,
				get_user_context,
				db_handler,
				faq_local["handle"],
				others_local
		)
		
		self.message = FAQs_message(
				start_panel,
				get_user_context,
				db_handler,
				faq_local["message"],
				others_local
		)
	
	def get_callback_query_handlers(self) -> list[CallbackQueryHandler]:
		"""
		Retrieves all callback query handlers related to FAQs.

		Combines handlers from FAQs_view and FAQs_handle, sorting them by pattern length
		in descending order to prioritize more specific handlers.

		Returns:
			list[CallbackQueryHandler]: A list of combined and sorted CallbackQueryHandler objects.
		"""
		return list(
				sorted(
						self.view.get_callback_query_handlers() +
						self.handle.get_callback_query_handlers(),
						key=lambda x: len(x.pattern.pattern),
						reverse=True
				)
		)
