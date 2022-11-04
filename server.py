import vk_api
from vk_bot import VKBOT
from vk_api.longpoll import VkLongPoll, VkEventType
from random import randint
import config


class Server:
    def __init__(self, server_name: str = "Server_01"):
        # Server`s settings
        self.server_name = server_name
        self.group_id = config.group_id

        # authorization
        self.vk = vk_api.VkApi(token=config.vk_api_group_token)
        self.person_token = vk_api.VkApi(token=config.vk_api_person_token)
        self.longPoll = VkLongPoll(self.vk)

        # users dict
        self.users = {}

    def send_message(self, user_id, message, attachment, name_keyboard):
        self.vk.method('messages.send', {'peer_id': user_id,
                                         'message': message,
                                         'random_id': randint(-1024, 1024),
                                         'attachment': attachment,
                                         'keyboard': open("keyboards/" + name_keyboard, "r",
                                                          encoding="UTF-8").read()})

    @staticmethod
    def get_text_msg(answer):
        """
        Bot can return answer as str, or str and keyboard, or str, keyboard and attachment
        :param answer: tuple or str
        :return: tuple len 3
        """
        if type(answer) is tuple:
            if len(answer) == 3:
                return answer[0], answer[1], answer[2]
            if '.json' in answer[1]:
                return answer[0], 0, answer[1]
            return answer[0], answer[1], 'none.json'
        return answer, 0, 'none.json'

    @staticmethod
    def get_all_wall_posts(self):
        posts = self.person_token.method('wall.get', {'count': config.MAX_COUNT_POSTS,
                                                      'owner_id': -config.group_id})
        return posts

    def run(self):
        print("Server started")
        for event in self.longPoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    print('New message:')
                    print('For me by: ', end='')
                    print(event.user_id)
                    user_id = event.user_id
                    if user_id not in self.users:
                        self.users[user_id] = VKBOT()

                    if self.users[user_id].NEXT_COMMAND == 'final':
                        text = self.get_text_msg(
                            self.users[user_id].get_main_menu_msg())
                        self.send_message(event.user_id, text[0], text[1], text[2])
                        continue

                    text = self.get_text_msg(
                        self.users[user_id].processing(event.text.lower(), event.user_id))
                    self.send_message(event.user_id, text[0], text[1], text[2])
                    print('Text: ', event.text, '\n')
