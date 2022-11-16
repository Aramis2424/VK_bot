from bot_parser import str_parser
from commands import Commands


class VKBOT:
    def __init__(self):
        print("Create new instance")

        # Parsing tools
        self.str_parser = str_parser.Parser()

        # Flag of next command
        self.cur_command = None
        self.next_command = "start"

    def get_welcome_msg(self, user_id):
        """
        Send greetings message with user`s name
        @:param user_id - user`s id
        @:return "Привет + $USER_NAME"
        """
        user_name = self.str_parser.get_user_name_from_vk_id(user_id)

        return "Привет, " + user_name.split()[0] + "!\nЯ бот Центра карьеры МГТУ им. Н.Э. Баумана\n\n"

    def get_main_menu_msg(self, welcome_msg=False):
        self.next_command = "start"
        if welcome_msg:
            return "Что Вас интересует?", "mainMenu.json"
        return "Нужно что-нибудь еще?", "mainMenu.json"

    def processing(self, text, user_id):
        if self.next_command == "final":
            answer = self.get_main_menu_msg()
            self.next_command = "start"
        else:
            answer = self.choose_command(text, user_id)
        return answer

    def choose_command(self, text, user_id):
        """
        Get and work with message
        :param text: str
        :param user_id: users`s ID
        :return: answer - str
        """
        text = text.lower()
        # Start -- начать
        if text in Commands.start.value:
            menu = self.get_main_menu_msg(welcome_msg=True)
            return self.get_welcome_msg(user_id) + menu[0], menu[1]

        # Greetings -- привет
        if text in Commands.greetings.value:
            menu = self.get_main_menu_msg(welcome_msg=True)
            return "Привет, рад встрече!\n\n" + menu[0], menu[1]

        # Jobs -- вакансии, стажировки, практики
        if text in Commands.jobs.value:
            self.next_command = "final"
            return "В какой сфере вы ищете " + str(text) + "?", "jobsSphere.json"

        # Help -- помощь
        if text in Commands.help.value:
            return self.get_main_menu_msg(welcome_msg=True)

        # Exit -- пока 2020
        if text in Commands.exit.value:
            raise TimeoutError

        # Unknown command
        menu = self.get_main_menu_msg(welcome_msg=True)
        return "Извините, но я Вас не понял\n" \
               "Пожалуйста, для отправки сообщений воспользуйтесь кнопками\n\n" + menu[0], menu[1]
