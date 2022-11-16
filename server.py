from random import randint
from requests import exceptions
import os
import sys
import datetime
import traceback

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

from vk_bot import VKBOT
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

    @staticmethod
    def get_time():
        now = datetime.datetime.now()
        return "Time: " + str(now.strftime("%d-%m-%Y %H:%M"))

    def listening(self):
        for event in self.longPoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    # print('New message:')
                    print('For me by: ', end='')
                    print(event.user_id)
                    user_id = event.user_id
                    if user_id not in self.users:
                        self.users[user_id] = VKBOT()

                    # # TODO: Перенести обработчик NEXT_COMMAND в vk_bot;
                    # if self.users[user_id].NEXT_COMMAND == 'final':
                    #     text = self.get_text_msg(
                    #         self.users[user_id].get_main_menu_msg())
                    #     self.send_message(event.user_id, text[0], text[1], text[2])
                    #     continue

                    text = self.get_text_msg(
                        self.users[user_id].processing(event.text, event.user_id))
                    self.send_message(event.user_id, text[0], text[1], text[2])
                    print('Text: ', event.text)

    def run(self):
        print("========== Server started ==========")
        print(self.get_time(), "\n")
        try:
            self.listening()
        except (exceptions.ConnectionError, TimeoutError, exceptions.Timeout,
                exceptions.ConnectTimeout, exceptions.ReadTimeout):
            print("\n!!!------- Error Timeout -------!!!")
            print(self.get_time(), "\n")
            self.restart()
        finally:
            print("\n<><><><><> Unknown error <><><><><>\nFinish.")
            print(self.get_time(), "\n")
            file = open("error_file.txt", "w")
            file.write(f"Error: {traceback.format_exc()}\n{self.get_time()}")
            file.close()

    @staticmethod
    def restart():
        # print("argv was", sys.argv)
        # print("sys.executable was", sys.executable)
        # print("restart now")
        os.execv(sys.executable, ['python'] + sys.argv)
