import functions
import data_handlers
from telegram.ext import CallbackQueryHandler, ContextTypes
from objects_types import get_user_context_type, start_panel_type
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update


class StateFlags:
    """
    Defines string constants representing different states within the bot's conversation flow related to question management.

    These flags are used to track the current state of interaction with the user, allowing
    the bot to respond appropriately to different inputs and callbacks related to question viewing,
    statistics, and clearing questions.

    Attributes:
        input_number_of_questions_to_view (str): State for handling user input for the number of questions to view.

        view_questions_list (str): State for viewing the list of questions.
        view_questions_statistics (str): State for viewing question statistics.
        view_questions (str): State for general question viewing options.

        clear_questions_confirm (str): State for confirming the clearing of questions.
        clear_questions_request (str): State for requesting to clear questions.
        handle_questions (str): State for general handling of question-related actions.
    """
    input_number_of_questions_to_view = "input_number_of_questions_to_view"

    view_questions_list = "view_questions_list"
    view_questions_statistics = "view_questions_statistics"
    view_questions = "view_questions"

    clear_questions_confirm = "clear_questions_confirm"
    clear_questions_request = "clear_questions_request"
    handle_questions = "handle_questions"


class Question_message:
    """
    Handles message-based interactions related to question viewing.

    This class processes user input for specifying the number of questions to view and
    retrieves and displays the corresponding questions from the database. It handles
    potential errors in user input and provides appropriate feedback.

    Attributes:
        db_handler (MySQLDataHandler): An instance of the MySQLDataHandler for database interaction.

    :Usage:
        question_message = Question_message(db_handler_instance)
        question_message.input_number_of_questions_to_view(update, context) # Process user input for the number of questions to view.
    """
    def __init__(self, db_handler: data_handlers.MySQLDataHandler):
        """
        Initializes the Question_message class.

        Args:
            db_handler (MySQLDataHandler): The data handler for database operations.
        """
        self.db_handler = db_handler

    async def input_number_of_questions_to_view(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Processes a message containing the number of questions to view.

        Retrieves and displays the specified number of questions from the database.
        Handles invalid input (non-integer values) and provides feedback to the user.

        Args:
            update (Update): The Telegram update object.
            context (ContextTypes.DEFAULT_TYPE): The Telegram context object.
        """
        try:
            number_of_questions = int(update.message.text)
        except ValueError:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Вводить нужно только целое число.")
        else:
            total_questions = self.db_handler.questions_data.get_total_questions_count()
            if number_of_questions > total_questions:
                questions = self.db_handler.questions_data.get_questions_text_list()
                questions_to_view = "\n\n".join(f"{i + 1}: {questions[i]}" for i in range(len(questions))) + f"\n\nВсего вопросов: {len(questions)}"
            elif number_of_questions > 0:
                questions = self.db_handler.questions_data.get_questions_text_list(number_of_questions)
                questions_to_view = "\n\n".join(f"{i + 1}: {questions[i]}" for i in range(len(questions)))
            else:
                questions_to_view = "Нужно указать количество вопросов для просмотра больше нуля."

            await context.bot.send_message(chat_id=update.effective_chat.id, text=questions_to_view)
        finally:
            context.user_data.pop("processing")
            self.db_handler.users_data.update_last_state(update.effective_user.username, StateFlags.input_number_of_questions_to_view, None, context)


class Questions_handle:
    """
    Handles callback query interactions related to question management.

    This class provides functionalities for clearing all questions, including a confirmation step.
    It manages the interaction flow and ensures that only authorized users can perform these actions.

    Attributes:
        start (function): The function to display the bot's start panel.
        get_user_context (function): The function to retrieve user-specific context data.
        db_handler (MySQLDataHandler): The data handler for database operations.

    :Usage:
        questions_handle = Questions_handle(start_panel_function, get_user_context_function, db_handler_instance)
        questions_handle.clear_questions_confirm(update, context) # Confirm clearing all questions.
        questions_handle.clear_questions_request(update, context) # Request to clear questions (confirmation step).
        questions_handle.handle_questions(update, context) # Main entry point for question management interactions.
    """
    def __init__(self, start_panel: start_panel_type, get_user_context: get_user_context_type, db_handler: data_handlers.MySQLDataHandler):
        """
        Initializes the Questions_handle class.

        Args:
            start_panel (function): The function to display the start panel.
            get_user_context (function): The function to retrieve user context.
            db_handler (MySQLDataHandler): The database handler instance.
        """
        self.start = start_panel
        self.get_user_context = get_user_context
        self.db_handler = db_handler

    async def clear_questions_confirm(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Confirms and executes the clearing of all questions.

        Args:
            update (Update): The Telegram update object.
            context (ContextTypes.DEFAULT_TYPE): The Telegram context object.
        """
        self.get_user_context(update, context)
        current_state = functions.get_current_state(context)

        if current_state[0] == StateFlags.clear_questions_request and current_state[1] == update.effective_message.message_id:
            if context.user_data["abilities"]["able_to_questions_handle"]:
                self.db_handler.questions_data.clear_questions_data()

                await update.effective_message.edit_text(text="Вопросы очищены.")

                self.db_handler.users_data.update_last_state(update.effective_user.username, StateFlags.clear_questions_confirm, None, context)

                await self.start(update, context)
            else:
                await functions.warning_rights_error("У вас нет прав для очищения вопросов.", self.start, update, context)
        else:
            await self.start(update, context)

    async def clear_questions_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Requests confirmation from the user before clearing all questions.

        Args:
            update (Update): The Telegram update object.
            context (ContextTypes.DEFAULT_TYPE): The Telegram context object.
        """
        self.get_user_context(update, context)
        current_state = functions.get_current_state(context)

        if current_state[0] == StateFlags.handle_questions and current_state[1] == update.effective_message.message_id:
            if context.user_data["abilities"]["able_to_questions_handle"]:
                keyboard = [
                    [InlineKeyboardButton("Очистить вопросы", callback_data=StateFlags.clear_questions_confirm)],
                    [InlineKeyboardButton("Отмена", callback_data=StateFlags.handle_questions)]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                message = await update.effective_message.edit_text(text="Вы уверены, что хотите очистить все вопросы?", reply_markup=reply_markup)

                self.db_handler.users_data.update_last_state(update.effective_user.username, StateFlags.clear_questions_request, message.message_id, context)
                context.user_data["processing"] = True
            else:
                await functions.warning_rights_error("У вас нет прав для очищения вопросов.", self.start, update, context)
        else:
            await self.start(update, context)

    async def handle_questions(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Provides the main interface for question management options.

        Args:
            update (Update): The Telegram update object.
            context (ContextTypes.DEFAULT_TYPE): The Telegram context object.
        """
        self.get_user_context(update, context)
        current_state = functions.get_current_state(context)

        if current_state[0] in ["start", StateFlags.clear_questions_request] and current_state[1] == update.effective_message.message_id:
            if context.user_data["abilities"]["able_to_questions_handle"]:
                keyboard = [
                    [InlineKeyboardButton("Очистить вопросы", callback_data=StateFlags.clear_questions_request)],
                    [InlineKeyboardButton("Назад", callback_data="start")]
                ]

                reply_markup = InlineKeyboardMarkup(keyboard)

                message = await functions.edit_message(
                        message_to_edit=current_state[1],
                        text="Выберите режим управления вопросами:",
                        update=update,
                        context=context,
                        reply_markup=reply_markup
                )

                self.db_handler.users_data.update_last_state(update.effective_user.username, StateFlags.handle_questions, message.message_id, context)
                context.user_data["processing"] = True
            else:
                await functions.warning_rights_error("У вас нет прав для управления вопросами.", self.start, update, context)
        else:
            await self.start(update, context)

    def get_callback_query_handlers(self) -> list[CallbackQueryHandler]:
        """
        Returns a list of CallbackQueryHandlers for question management interactions.

        Returns:
            list[CallbackQueryHandler]: A list of CallbackQueryHandler objects.
        """
        return list(
                sorted(
                        [
                            CallbackQueryHandler(callback=self.handle_questions, pattern=StateFlags.handle_questions),
                            CallbackQueryHandler(callback=self.clear_questions_request, pattern=StateFlags.clear_questions_request),
                            CallbackQueryHandler(callback=self.clear_questions_confirm, pattern=StateFlags.clear_questions_confirm)
                        ],
                        key=lambda x: len(x.pattern.pattern),
                        reverse=True
                )
        )


class Questions_view:
    """
    Handles displaying question-related information.

    This class provides functionalities to view question statistics, a list of questions,
    and manages the navigation between these views. It interacts with the database to
    retrieve the necessary data and presents it to the user. It also handles user input
    for specifying the number of questions to display in the list view.

    Attributes:
        start (function): The function to display the bot's start panel.
        get_user_context (function): The function to retrieve user-specific context data.
        db_handler (MySQLDataHandler): The data handler for database operations.

    :Usage:
        questions_view = Questions_view(start_panel_function, get_user_context_function, db_handler_instance)
        questions_view.view_questions_list(update, context) # Prompt for and display a list of questions.
        questions_view.view_questions_statistics(update, context) # Display question statistics.
        questions_view.view_questions(update, context) # Main entry point for viewing question information.
    """
    def __init__(self, start_panel: start_panel_type, get_user_context: get_user_context_type, db_handler: data_handlers.MySQLDataHandler):
        """
        Initializes the Questions_view class.

        Args:
            start_panel (function): The function to display the start panel.
            get_user_context (function): The function to retrieve user context.
            db_handler (MySQLDataHandler): The database handler instance.
        """
        self.start = start_panel
        self.get_user_context = get_user_context
        self.db_handler = db_handler

    async def view_questions_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Prompts the user to enter the number of questions they want to view.

        Args:
            update (Update): The Telegram update object.
            context (ContextTypes.DEFAULT_TYPE): The Telegram context object.
        """
        self.get_user_context(update, context)
        current_state = functions.get_current_state(context)

        if current_state[0] == StateFlags.view_questions and current_state[1] == update.effective_message.message_id:
            if context.user_data["abilities"]["able_to_questions_view"]:
                reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Отмена", callback_data=StateFlags.view_questions)]])

                message = await update.effective_message.edit_text(text="Введите количество вопросов для просмотра:", reply_markup=reply_markup)

                self.db_handler.users_data.update_last_state(update.effective_user.username, StateFlags.view_questions_list, message.message_id, context)
                context.user_data["processing"] = True
            else:
                await functions.warning_rights_error("У вас нет прав для просмотра списка вопросов.", self.start, update, context)
        else:
            await self.start(update, context)

    async def view_questions_statistics(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Displays statistics about the questions, such as total count, answered/unanswered counts, and average answer time.

        Args:
            update (Update): The Telegram update object.
            context (ContextTypes.DEFAULT_TYPE): The Telegram context object.
        """
        self.get_user_context(update, context)
        current_state = functions.get_current_state(context)

        if current_state[0] == StateFlags.view_questions and current_state[1] == update.effective_message.message_id:
            if context.user_data["abilities"]["able_to_questions_view"]:
                questions_stats = self.db_handler.questions_data.get_questions_stats()

                percent_unanswered = (questions_stats["unanswered_questions"] / questions_stats["total_questions"]) * 100 if questions_stats["total_questions"] else 0
                percent_processing = (questions_stats["processing_questions"] / questions_stats["total_questions"]) * 100 if questions_stats["total_questions"] else 0
                percent_answered = (questions_stats["answered_questions"] / questions_stats["total_questions"]) * 100 if questions_stats["total_questions"] else 0

                average_answer_time = self.db_handler.questions_data.get_average_answer_time()
                average_answer_time = functions.format_time(average_answer_time)

                stats_text = "\n".join(
                        [
                            f"Всего вопросов: {questions_stats['total_questions']}",
                            f"Не обработано: {questions_stats['unanswered_questions']} ({percent_unanswered:.1f}%)",
                            f"Обрабатывается: {questions_stats['processing_questions']} ({percent_processing:.1f}%)",
                            f"Обработано: {questions_stats['answered_questions']} ({percent_answered:.1f}%)",
                            f"Среднее время ответа: {average_answer_time}"
                        ]
                )

                await functions.edit_message(message_to_edit=current_state[1], text=stats_text, update=update, context=context)

                self.db_handler.users_data.update_last_state(update.effective_user.username, StateFlags.view_questions_statistics, None, context)

                await self.start(update, context)
            else:
                await functions.warning_rights_error("У вас нет прав для просмотра статистики вопросов.", self.start, update, context)
        else:
            await self.start(update, context)

    async def view_questions(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Provides the main interface for choosing between viewing question statistics or the question list.

        Args:
            update (Update): The Telegram update object.
            context (ContextTypes.DEFAULT_TYPE): The Telegram context object.
        """
        self.get_user_context(update, context)
        current_state = functions.get_current_state(context)

        if current_state[0] in ["start", StateFlags.view_questions_statistics, StateFlags.view_questions_list] and current_state[1] == update.effective_message.message_id:
            if context.user_data["abilities"]["able_to_questions_view"]:
                keyboard = [
                    [
                        InlineKeyboardButton("Посмотреть статистику вопросов", callback_data=StateFlags.view_questions_statistics)
                    ],
                    [InlineKeyboardButton("Посмотреть список вопросов", callback_data=StateFlags.view_questions_list)],
                    [InlineKeyboardButton("Назад", callback_data="start")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                message = await functions.edit_message(
                        message_to_edit=current_state[1],
                        text="Выберите режим просмотра вопросов:",
                        update=update,
                        context=context,
                        reply_markup=reply_markup
                )

                self.db_handler.users_data.update_last_state(update.effective_user.username, StateFlags.view_questions, message.message_id, context)
                context.user_data["processing"] = True
            else:
                await functions.warning_rights_error("У вас нет прав для просмотра вопросов.", self.start, update, context)
        else:
            await self.start(update, context)

    def get_callback_query_handlers(self) -> list[CallbackQueryHandler]:
        """
        Returns a list of CallbackQueryHandlers for question viewing interactions.

        Returns:
            list[CallbackQueryHandler]: A list of CallbackQueryHandler objects.
        """
        return list(
                sorted(
                        [
                            CallbackQueryHandler(callback=self.view_questions, pattern=StateFlags.view_questions),
                            CallbackQueryHandler(callback=self.view_questions_statistics, pattern=StateFlags.view_questions_statistics),
                            CallbackQueryHandler(callback=self.view_questions_list, pattern=StateFlags.view_questions_list)
                        ],
                        key=lambda x: len(x.pattern.pattern),
                        reverse=True
                )
        )


class Questions_controls:
    """
    Manages the control flow and interactions related to question management.

    This class acts as a central controller, combining the functionalities of Questions_view,
    Questions_handle, and Question_message. It provides a unified interface for handling
    user interactions related to viewing question information, managing questions (e.g., clearing),
    and processing message-based inputs related to questions.

    Attributes:
        view (Questions_view): An instance of the Questions_view class for displaying question information.
        handle (Questions_handle): An instance of the Questions_handle class for managing question-related actions.
        message (Question_message): An instance of the Question_message class for handling message-based question interactions.

    :Usage:
        questions_controls = Questions_controls(start_panel_function, get_user_context_function, db_handler_instance)
        handlers = questions_controls.get_callback_query_handlers() # Retrieve all question management related handlers.
    """
    def __init__(self, start_panel: start_panel_type, get_user_context: get_user_context_type, db_handler: data_handlers.MySQLDataHandler):
        """
        Initializes the Questions_controls class.

        Args:
            start_panel (function): The function to display the bot's start panel.
            get_user_context (function): The function to retrieve user-specific context data.
            db_handler (MySQLDataHandler): The data handler for database interactions.
        """
        self.view = Questions_view(start_panel, get_user_context, db_handler)
        self.handle = Questions_handle(start_panel, get_user_context, db_handler)
        self.message = Question_message(db_handler)

    def get_callback_query_handlers(self) -> list[CallbackQueryHandler]:
        """
        Retrieves all callback query handlers related to question management.

        Combines handlers from Questions_view and Questions_handle, sorting them by pattern
        length in descending order to prioritize more specific handlers.

        Returns:
            list[CallbackQueryHandler]: A list of combined and sorted CallbackQueryHandler objects.
        """
        return list(
                sorted(
                        self.view.get_callback_query_handlers() + self.handle.get_callback_query_handlers(),
                        key=lambda x: len(x.pattern.pattern),
                        reverse=True
                )
        )