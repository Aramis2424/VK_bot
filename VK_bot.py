import config
from bot_parser import str_parser
from commands import Commands
from bot_parser import wallPosts_parser
from jobs import Jobs


class VKBOT:
    def __init__(self):
        print("Create new instance")

        # Parsing tools
        self.str_parser = str_parser.Parser()
        self.wall_parser = wallPosts_parser.WallPostsParser()

        # Flags
        self.post_index = 0
        # self.posts = []
        self.type_post = 0
        self.yn_continue = 0
        self.next_command = "any"

    def get_welcome_msg(self, user_id):
        """
        Send greetings message with user`s name
        @:param user_id - user`s id
        @:return "Привет + $USER_NAME"
        """
        user_name = self.str_parser.get_user_name_from_vk_id(user_id)

        return "Привет, " + user_name.split()[0] + "!\nЯ бот Центра карьеры МГТУ им. Н.Э. Баумана\n\n"

    def get_main_menu_msg(self, welcome_msg=False):
        # Сброс флагов и переменных
        self.next_command = "any"
        self.type_post = 0
        self.post_index = 0
        if welcome_msg:
            return "Что Вас интересует?", "mainMenu.json"
        return "Нужно что-нибудь еще?", "mainMenu.json"

    def processing(self, text, user_id):
        text = text.lower()
        if self.next_command == "menu":
            answer = self.get_main_menu_msg()
            self.next_command = "any"
        elif self.next_command == "link_consultCareer":
            answer = self.choose_command("Профориентация", user_id)
            self.next_command = "menu"
        elif self.next_command == "output_jobs":
            answer = ("Показать еще?", "YN_continue.json")
            self.next_command = "any"
        elif self.next_command == "any" and self.yn_continue:
            self.yn_continue = 0
            if text == "нет":
                answer = self.get_main_menu_msg()
            else:
                answer = self.output_jobs()
        else:
            answer = self.choose_command(text, user_id)
        return answer

    def output_jobs(self):
        if self.type_post == 1:
            posts = Jobs.vacancies
        elif self.type_post == 2:
            posts = Jobs.internships
        else:
            posts = Jobs.practices

        if self.post_index < len(posts):
            self.yn_continue = 1
            self.next_command = "output_jobs"
            self.post_index += 1
            index = self.post_index - 1
            return "wall" + str(-config.group_id) + "_" + str(posts[index]["id"])
        else:
            menu = self.get_main_menu_msg()
            return "К сожалению, это всё\n\n" + menu[0], menu[1]

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
            # self.next_command = "menu"  # TODO: это временно
            # return "В какой сфере вы ищете " + str(text) + "?", "jobsSphere.json"

            # if len(self.posts) == 0:  # т.е если в первый раз
            #     self.type_post = self.str_parser.select_post_type(text)
            #     self.posts = self.wall_parser.select_posts(self.type_post)
            self.type_post = self.str_parser.select_post_type(text)
            return self.output_jobs()

        # Career -- профориентация
        if text in Commands.career.value:
            if self.next_command == "any":
                self.next_command = "link_consultCareer"
                return "Это профориентационный тест\n" + "https://lift-bf.ru/career"
            self.next_command = "menu"
            return "А это карьерная консультация от нашей группы\n" + "https://vk.com/wall-190939167_998"

        if text in Commands.career_tips.value:
            self.next_command = "menu"
            return "Вот тег нашей группы\n" + "https://vk.com/topic-190939167_46757391"

        # Help -- помощь
        if text in Commands.help.value:
            return self.get_main_menu_msg(welcome_msg=True)

        # Exit -- пока 2020
        if text in Commands.exit.value:
            raise TimeoutError

        # Admin
        if text in Commands.admin.value:
            self.next_command = "/admin2022load"
            return "/Complete"

        # Unknown command
        menu = self.get_main_menu_msg(welcome_msg=True)
        return "Извините, но я Вас не понял\n" \
               "Пожалуйста, для отправки сообщений воспользуйтесь кнопками\n\n" + menu[0], menu[1]
