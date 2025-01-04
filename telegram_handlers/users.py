import re
import functions
import data_handlers
from telegram.ext import CallbackQueryHandler, ContextTypes
from objects_types import get_user_context_type, start_panel_type
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update


class StateFlags:
    """
    Constants representing different states in the bot's workflow.

    This class defines string constants to represent various states within the bot's operation.
    These constants are utilized to track the current stage of interaction with the user, enabling the bot
    to maintain context and respond appropriately during different phases of user interaction, particularly
    for user management.

    Attributes:
        handle_moderator_username_to_delete_message (str): State for handling moderator username input to delete a message.
        handle_new_moderator_username_message (str): State for handling moderator username input for a new message.

        view_users_list (str): State for viewing the list of users.
        view_users_statistics (str): State for viewing users' statistics.
        view_users (str): State for the main user management menu.

        remove_user_role (str): State for removing a user's role.
        add_role_chosen (str): State for when a role has been chosen to be added.
        chose_user_to_add_role (str): State for choosing a user to add a role to.
        add_user_role (str): State for adding a role to a user.
        handle_users (str): State representing the main menu for user handling.
    """
    handle_moderator_username_to_delete_message = "handle_moderator_username_to_delete_message"
    handle_new_moderator_username_message = "handle_new_moderator_username_message"

    view_users_list = "view_users_list"
    view_users_statistics = "view_users_statistics"
    view_users = "view_users"

    remove_user_role = "remove_user_role"
    add_role_chosen = "add_role_chosen"
    chose_user_to_add_role = "chose_user_to_add_role"
    add_user_role = "add_user_role"
    handle_users = "handle_users"


class Users_messages:
    """
    Handles message-based interactions related to user management.

    This class processes text messages from users regarding adding or removing roles,
    interacting with the database to update user information and sending corresponding
    messages to inform users about the changes.

    Attributes:
        db_handler (MySQLDataHandler): An instance of the MySQLDataHandler for database interaction.

    :Usage:
        user_messages = Users_messages(db_handler_instance)
        user_messages.input_username_to_add_role(update, context) # Process adding a role
        user_messages.input_username_to_remove_role(update, context) # Process removing a role
    """
    def __init__(self, db_handler: data_handlers.MySQLDataHandler):
        """
        Initializes the Users_messages class.

        Args:
            db_handler (MySQLDataHandler): The data handler for database operations.
        """
        self.db_handler = db_handler

    async def input_username_to_add_role(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Processes a message containing a username to add a role to.

        Args:
            update (Update): The Telegram update object.
            context (ContextTypes.DEFAULT_TYPE): The Telegram context object.
        """
        username = functions.preprocess_username(update.message.text)

        self.db_handler.users_data.add_user(username, context.user_data["temp"]["role_to_set"])
        await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"@{username} получил роль {context.user_data['temp']['role_to_set']}!"
        )

        context.user_data.pop("processing")
        self.db_handler.users_data.update_last_state(update.effective_user.username, StateFlags.handle_new_moderator_username_message, None, context)

    async def input_username_to_remove_role(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Processes a message containing a username to remove a role from.

        Args:
            update (Update): The Telegram update object.
            context (ContextTypes.DEFAULT_TYPE): The Telegram context object.
        """
        username = functions.preprocess_username(update.message.text)

        accepted_roles = self.db_handler.users_data.get_roles_by_priority(context.user_data["role"], "<")
        user_data = self.db_handler.users_data.get_user_data(username)

        if user_data:
            if user_data["role"] not in accepted_roles:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Вы не можете забрать права у @{username}.")
            else:
                self.db_handler.users_data.remove_user(username)

                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"У @{username} больше нет прав!")

                if user_data["chat_id"] is not None:
                    await context.bot.send_message(chat_id=int(user_data["chat_id"]), text="У вас больше нет прав.")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"У @{username} нет роли.")

        context.user_data.pop("processing")
        self.db_handler.users_data.update_last_state(
                update.effective_user.username,
                StateFlags.handle_moderator_username_to_delete_message,
                None,
                context
        )


class Users_handle:
    """
    Handles callback query interactions related to user management.

    This class manages the flow of adding and removing roles from users, guiding the user
    through the process with interactive messages and callbacks. It utilizes the database
    to validate actions and update user information.

    Attributes:
        start_panel (function): The function to display the bot's start panel.
        get_user_context (function): The function to retrieve user-specific context data.
        db_handler (MySQLDataHandler): The data handler for database operations.

    :Usage:
        users_handle = Users_handle(start_panel_function, get_user_context_function, db_handler_instance)
        users_handle.remove_user_role(update, context) # Initiate removing a user's role.
        users_handle.chose_user_to_add_role(update, context) # Choose a user to add a role to.
        users_handle.add_user_role(update, context) # Initiate adding a user role.
        users_handle.handle_users(update, context) # Main entry point for user management interactions.
    """
    def __init__(
            self,
            start_panel: start_panel_type,
            get_user_context: get_user_context_type,
            db_handler: data_handlers.MySQLDataHandler
    ):
        """
        Initializes the Users_handle class.

        Args:
            start_panel (function): Function to display the start panel.
            get_user_context (function): Function to retrieve user context.
            db_handler (MySQLDataHandler): The database handler instance.
        """
        self.start_panel = start_panel
        self.get_user_context = get_user_context
        self.db_handler = db_handler

    async def remove_user_role(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handles the removal of a user's role.

        Prompts the user for the username of the user whose role needs to be removed.

        Args:
            update (Update): The Telegram update object.
            context (ContextTypes.DEFAULT_TYPE): The Telegram context object.
        """
        self.get_user_context(update, context)
        current_state = functions.get_current_state(context)

        if current_state[0] == StateFlags.handle_users and current_state[1] == update.effective_message.message_id:
            if context.user_data["abilities"]["able_to_users_handle"]:
                reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Отмена", callback_data=StateFlags.handle_users)]])

                message = await update.effective_message.edit_text(text="Введите username пользователя, у которого нужно забрать роль:", reply_markup=reply_markup)

                self.db_handler.users_data.update_last_state(update.effective_user.username, StateFlags.remove_user_role, message.message_id, context)
                context.user_data["processing"] = True
            else:
                await functions.warning_rights_error("У вас нет прав для удаления ролей.", self.start_panel, update, context)
        else:
            await self.start_panel(update, context)

    async def chose_user_to_add_role(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handles choosing a user to add a role to.

        Prompts the user for the username after a role has been selected.

        Args:
            update (Update): The Telegram update object.
            context (ContextTypes.DEFAULT_TYPE): The Telegram context object.
        """
        self.get_user_context(update, context)
        current_state = functions.get_current_state(context)

        if current_state[0] == StateFlags.add_user_role and current_state[1] == update.effective_message.message_id:
            if context.user_data["abilities"]["able_to_users_handle"]:
                message = await update.effective_message.edit_text(text="Введите username, которому присвоить роль:")

                self.db_handler.users_data.update_last_state(update.effective_user.username, StateFlags.chose_user_to_add_role, message.message_id, context)
                context.user_data["processing"] = True
                context.user_data["temp"]["role_to_set"] = re.search(r"_\*(\w+)\*\Z", update.callback_query.data).group(1)
            else:
                await functions.warning_rights_error("У вас нет прав для выдачи ролей.", self.start_panel, update, context)
        else:
            await self.start_panel(update, context)

    async def add_user_role(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handles the process of adding a role to a user.

        Presents a list of available roles for the user to choose from.

        Args:
            update (Update): The Telegram update object.
            context (ContextTypes.DEFAULT_TYPE): The Telegram context object.
        """
        self.get_user_context(update, context)
        current_state = functions.get_current_state(context)

        if current_state[0] == StateFlags.handle_users and current_state[1] == update.effective_message.message_id:
            if context.user_data["abilities"]["able_to_users_handle"]:
                accepted_roles = self.db_handler.users_data.get_roles_by_priority(context.user_data["role"], "<")

                keyboard = [
                    [
                        InlineKeyboardButton(accepted_role, callback_data=f"{StateFlags.chose_user_to_add_role}_*{accepted_role}*")
                    ] for accepted_role in accepted_roles
                ]
                keyboard.append([InlineKeyboardButton("Отмена", callback_data=StateFlags.handle_users)])
                reply_markup = InlineKeyboardMarkup(keyboard)

                message = await update.effective_message.edit_text(text="Выберите роль:", reply_markup=reply_markup)

                self.db_handler.users_data.update_last_state(update.effective_user.username, StateFlags.add_user_role, message.message_id, context)
                context.user_data["processing"] = True
            else:
                await functions.warning_rights_error("У вас нет прав для выдачи ролей.", self.start_panel, update, context)
        else:
            await self.start_panel(update, context)

    async def handle_users(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Provides the main interface for user management.

        Offers options to add or remove roles.

        Args:
            update (Update): The Telegram update object.
            context (ContextTypes.DEFAULT_TYPE): The Telegram context object.
        """
        self.get_user_context(update, context)
        current_state = functions.get_current_state(context)

        if current_state[0] in ["start", StateFlags.add_user_role, StateFlags.remove_user_role] and current_state[1] == update.effective_message.message_id:
            if context.user_data["abilities"]["able_to_users_handle"]:
                keyboard = [
                    [InlineKeyboardButton("Добавить роль", callback_data=StateFlags.add_user_role)],
                    [InlineKeyboardButton("Удалить роль", callback_data=StateFlags.remove_user_role)],
                    [InlineKeyboardButton("Назад", callback_data="start")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                message = await functions.edit_message(
                        message_to_edit=current_state[1],
                        text="Выберите режим управления:",
                        update=update,
                        context=context,
                        reply_markup=reply_markup
                )

                self.db_handler.users_data.update_last_state(update.effective_user.username, StateFlags.handle_users, message.message_id, context)
                context.user_data["processing"] = True
            else:
                await functions.warning_rights_error("У вас нет прав для управления пользователями.", self.start_panel, update, context)
        else:
            await self.start_panel(update, context)

    def get_callback_query_handlers(self) -> list[CallbackQueryHandler]:
        """
        Returns a list of CallbackQueryHandlers for user management interactions.

        Returns:
            list[CallbackQueryHandler]: A list of CallbackQueryHandler objects.
        """
        return list(
                sorted(
                        [
                            CallbackQueryHandler(callback=self.handle_users, pattern=StateFlags.handle_users),
                            CallbackQueryHandler(callback=self.add_user_role, pattern=StateFlags.add_user_role),
                            CallbackQueryHandler(callback=self.chose_user_to_add_role, pattern=StateFlags.chose_user_to_add_role),
                            CallbackQueryHandler(callback=self.remove_user_role, pattern=StateFlags.remove_user_role)
                        ],
                        key=lambda x: len(x.pattern.pattern),
                        reverse=True
                )
        )


class Users_view:
    """
    Handles displaying user-related information.

    This class provides functionalities to view user statistics, the list of users,
    and manages the navigation between these views. It interacts with the database
    to retrieve the necessary data and presents it to the user.

    Attributes:
        start_panel (function): The function to display the bot's start panel.
        get_user_context (function): The function to retrieve user-specific context data.
        db_handler (MySQLDataHandler): The data handler for database operations.

    :Usage:
        users_view = Users_view(start_panel_function, get_user_context_function, db_handler_instance)
        users_view.view_users_list(update, context) # Display the list of users.
        users_view.view_users_statistics(update, context) # Display user statistics.
        users_view.view_users(update, context) # Main entry point for viewing user information.
    """
    def __init__(
            self,
            start_panel: start_panel_type,
            get_user_context: get_user_context_type,
            db_handler: data_handlers.MySQLDataHandler
    ):
        """
        Initializes the Users_view class.

        Args:
            start_panel (function): The function to display the start panel.
            get_user_context (function): The function to retrieve user context.
            db_handler (MySQLDataHandler): The database handler instance.
        """
        self.start_panel = start_panel
        self.get_user_context = get_user_context
        self.db_handler = db_handler

    async def view_users_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Displays the list of users and their roles.

        Args:
            update (Update): The Telegram update object.
            context (ContextTypes.DEFAULT_TYPE): The Telegram context object.
        """
        self.get_user_context(update, context)
        current_state = functions.get_current_state(context)

        if current_state[0] == StateFlags.view_users and current_state[1] == update.effective_message.message_id:
            if context.user_data["abilities"]["able_to_users_view"]:
                await functions.edit_message(
                        message_to_edit=current_state[1],
                        text="\n".join(
                                f"@{row['username']} - {row['role']}" for index,
                                row in self.db_handler.users_data.get_users_data().iterrows()
                        ),
                        update=update,
                        context=context
                )

                self.db_handler.users_data.update_last_state(update.effective_user.username, StateFlags.view_users_list, None, context)
                context.user_data.pop("processing")

                await self.start_panel(update, context)
            else:
                await functions.warning_rights_error("У вас нет прав для просмотра списка пользователей.", self.start_panel, update, context)
        else:
            await self.start_panel(update, context)

    async def view_users_statistics(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Displays user statistics, such as the number of questions handled.

        Args:
            update (Update): The Telegram update object.
            context (ContextTypes.DEFAULT_TYPE): The Telegram context object.
        """
        self.get_user_context(update, context)
        current_state = functions.get_current_state(context)

        if current_state[0] == StateFlags.view_users and current_state[1] == update.effective_message.message_id:
            if context.user_data["abilities"]["able_to_users_view"]:
                moderators_statistics = self.db_handler.questions_data.get_users_statistics()

                await functions.edit_message(
                        message_to_edit=current_state[1],
                        text="\n".join(f"@{username}: {count}" for username, count in moderators_statistics.items()),
                        update=update,
                        context=context
                )

                self.db_handler.users_data.update_last_state(update.effective_user.username, StateFlags.view_users_statistics, None, context)
                context.user_data.pop("processing")

                await self.start_panel(update, context)
            else:
                await functions.warning_rights_error("У вас нет прав для просмотра статистики пользователей.", self.start_panel, update, context)
        else:
            await self.start_panel(update, context)

    async def view_users(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Provides the main interface for choosing between viewing user statistics or the user list.

        Args:
            update (Update): The Telegram update object.
            context (ContextTypes.DEFAULT_TYPE): The Telegram context object.
        """
        self.get_user_context(update, context)
        current_state = functions.get_current_state(context)

        if current_state[0] in ["start"] and current_state[1] == update.effective_message.message_id:
            if context.user_data["abilities"]["able_to_users_view"]:
                keyboard = [
                    [
                        InlineKeyboardButton("Посмотреть статистику пользователей", callback_data=StateFlags.view_users_statistics)
                    ],
                    [InlineKeyboardButton("Посмотреть список пользователей", callback_data=StateFlags.view_users_list)],
                    [InlineKeyboardButton("Назад", callback_data="start")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                message = await functions.edit_message(
                        message_to_edit=current_state[1],
                        text="Выберите режим просмотра:",
                        update=update,
                        context=context,
                        reply_markup=reply_markup
                )

                self.db_handler.users_data.update_last_state(update.effective_user.username, StateFlags.view_users, message.message_id, context)
                context.user_data["processing"] = True
            else:
                await functions.warning_rights_error("У вас нет прав для просмотра пользователей.", self.start_panel, update, context)
        else:
            await self.start_panel(update, context)

    def get_callback_query_handlers(self) -> list[CallbackQueryHandler]:
        """
        Returns a list of CallbackQueryHandlers for user viewing interactions.

        Returns:
            list[CallbackQueryHandler]: A list of CallbackQueryHandler objects.
        """
        return list(
                sorted(
                        [
                            CallbackQueryHandler(callback=self.view_users, pattern=StateFlags.view_users),
                            CallbackQueryHandler(callback=self.view_users_statistics, pattern=StateFlags.view_users_statistics),
                            CallbackQueryHandler(callback=self.view_users_list, pattern=StateFlags.view_users_list)
                        ],
                        key=lambda x: len(x.pattern.pattern),
                        reverse=True
                )
        )


class Users_controls:
    """
    Manages the control flow and interactions related to user management.

    This class acts as a central controller, combining the functionalities of Users_view,
    Users_handle, and Users_messages. It provides a unified interface for handling
    user interactions related to viewing user information, modifying user roles, and
    sending related messages.

    Attributes:
        view (Users_view): An instance of the Users_view class for displaying user information.
        handle (Users_handle): An instance of the Users_handle class for managing user actions.
        message (Users_messages): An instance of the Users_messages class for sending user-related messages.

    :Usage:
        users_controls = Users_controls(start_panel_function, get_user_context_function, db_handler_instance)
        handlers = users_controls.get_callback_query_handlers() # Retrieve all user management related handlers
    """
    def __init__(
            self,
            start_panel: start_panel_type,
            get_user_context: get_user_context_type,
            db_handler: data_handlers.MySQLDataHandler
    ):
        """
        Initializes the Users_controls class.

        Args:
            start_panel (function): The function to display the bot's start panel.
            get_user_context (function): The function to retrieve user-specific context data.
            db_handler (MySQLDataHandler): The data handler for database interactions.
        """
        self.view = Users_view(start_panel, get_user_context, db_handler)
        self.handle = Users_handle(start_panel, get_user_context, db_handler)
        self.message = Users_messages(db_handler)

    def get_callback_query_handlers(self) -> list[CallbackQueryHandler]:
        """
        Retrieves all callback query handlers related to user management.

        Combines handlers from Users_view and Users_handle, sorting them by pattern length
        in descending order to prioritize more specific handlers.

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
