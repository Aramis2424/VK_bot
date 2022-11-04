import bs4
import requests


class Parser:
    def __init__(self):
        pass

    LAST_USER_NAME = None

    def get_user_name_from_vk_id(self, user_id):

        b = self.set_http("https://vk.com/id" + str(user_id))
        user_name = self.clean_tag_from_str(b.findAll("title")[0])

        self.LAST_USER_NAME = user_name
        return user_name

    @staticmethod
    def set_http(http: str):
        request = requests.get(http)
        bs = bs4.BeautifulSoup(request.text, "html.parser")

        return bs

    @staticmethod
    def clean_tag_from_str(string):

        s = ""
        for char in string:
            s += char
        return s

    @staticmethod
    def clean_all_tag_from_str(string_line):

        """
        Очистка строки stringLine от тэгов и их содержимых
        :param string_line: Очищаемая строка
        :return: очищенная строка
        """

        result = ""
        not_skip = True
        for i in list(string_line):
            if not_skip:
                if i == "<":
                    not_skip = False
                else:
                    result += i
            else:
                if i == ">":
                    not_skip = True
        return result
