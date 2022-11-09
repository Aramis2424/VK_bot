from bot_parser import str_parser
from commands import Commands


class VKBOT:
    def __init__(self):
        print("Create new instance")

        self.cur_command = None
        self.next_command = None

        # Parsing tools
        self.str_parser = str_parser.Parser()

        # Flag of welcome message
        self.WELCOME_MSG_SEND = False

        # Flag of next command
        self.NEXT_COMMAND = "any"

    def get_welcome_msg(self, user_id):
        """
        Send greetings message with user`s name
        @:param user_id - user`s id
        @:return "Привет + $USER_NAME"
        """
        user_name = self.str_parser.get_user_name_from_vk_id(user_id)
        self.WELCOME_MSG_SEND = True

        return "Привет, " + user_name.split()[0] + "!\nЯ бот Центра карьеры МГТУ им. Н.Э. Баумана\n\n"

    def get_main_menu_msg(self):
        self.NEXT_COMMAND = "any"
        if self.WELCOME_MSG_SEND:
            return "Нужно что-нибудь еще?", "mainMenu.json"
        self.WELCOME_MSG_SEND = True
        return "Что Вас интересует?", "mainMenu.json"

    def processing(self, text, user_id):
        """
        Get and work with message
        :param text: str
        :param user_id: users`s ID
        :return: answer - str
        """
        text = text.lower()
        # Start
        if text in Commands.start.value:
            menu = self.get_main_menu_msg()
            return self.get_welcome_msg(user_id) + menu[0], menu[1]

        # Jobs
        if text in Commands.jobs.value:
            self.NEXT_COMMAND = "final"
            return "В какой сфере вы ищете " + str(text) + "?", "jobsSphere.json"

        # Greetings
        if text in Commands.greetings.value:
            menu = self.get_main_menu_msg()
            return "Привет, рад встрече!\n\n" + menu[0], menu[1]

        # Help
        if text in Commands.help.value:
            return self.get_main_menu_msg()

        # Exit
        if text in Commands.exit.value:
            raise TimeoutError

        # Unknown command
        menu = self.get_main_menu_msg()
        return "Извините, но я Вас не понял\n" \
               "Пожалуйста, для отправки сообщений используйте кнопки\n\n" + menu[0], menu[1]
