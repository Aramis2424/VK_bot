from bot_parser import str_parser
from commands import Commands


class VKBOT:
    def __init__(self):
        print("Create new instance")

        # Parsing tools
        self.str_parser = str_parser.Parser()

        # Flag of next command
        self.cur_command = None
        self.next_command = "any"

    def get_welcome_msg(self, user_id):
        """
        Send greetings message with user`s name
        @:param user_id - user`s id
        @:return "Привет + $USER_NAME"
        """
        user_name = self.str_parser.get_user_name_from_vk_id(user_id)

        return "Привет, " + user_name.split()[0] + "!\nЯ бот Центра карьеры МГТУ им. Н.Э. Баумана\n\n"

    @staticmethod
    def get_main_menu_msg(welcome_msg=False):
        if welcome_msg:
            return "Что Вас интересует?", "mainMenu.json"
        return "Нужно что-нибудь еще?", "mainMenu.json"

    # TODO: добавить флаг конца диалога по конкретному вопросу (нужно для последовательной отправки сообщений)
    def processing(self, text, user_id):
        if self.next_command == "menu":
            answer = self.get_main_menu_msg()
            self.next_command = "any"
        elif self.next_command == "link_consultCareer":
            answer = self.choose_command("Профориентация", user_id)
            self.next_command = "menu"
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
            self.next_command = "menu"  # TODO: это временно
            return "В какой сфере вы ищете " + str(text) + "?", "jobsSphere.json"

        # Career -- профориентация
        if text in Commands.career.value:
            if self.next_command == "any":
                self.next_command = "link_consultCareer"
                return "Это профориентационный тест\n" + "https://lift-bf.ru/career"
            self.next_command = "menu"
            return "А это карьерная консультация от нашей группы\n" + "https://vk.com/wall-190939167_998"

        if text in Commands.career_tips.value:
            self.next_command = "menu"
            return "Тег нашей группы\n" + "https://vk.com/topic-190939167_46757391"

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
