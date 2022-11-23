from random import randint
from requests import exceptions
import os
import sys
import traceback
from datetime import datetime
from time import sleep

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import json

from vk_bot import VKBOT
from bot_parser import wallPosts_parser
from jobs import Jobs
import config


class Server:
    def __init__(self, server_name: str = "Server_01"):
        # Server`s settings
        self.server_name = server_name
        self.group_id = config.group_id

        # authorization
        self.vk = vk_api.VkApi(token=config.vk_api_group_token)
        self.person_token = vk_api.VkApi(token=config.vk_api_person_token)
        # self.longPoll = VkLongPoll(self.vk)
        self.longPoll = VkBotLongPoll(self.vk, self.group_id)

        # users dict
        self.users = {}

        # Обработчик записей на стене
        self.wall_parser = wallPosts_parser.WallPostsParser()

        # Начальная установка массивов записей
        self.update_vac()
        self.update_inter()
        self.update_prac()

    def send_message(self, user_id, message, attachment, name_keyboard):
        for i in range(3):  # Трижды пытается отправить сообщение если будет ошибка
            try:
                self.vk.method('messages.send', {'user_id': user_id,
                                                 'message': message,
                                                 'random_id': randint(-1024, 1024),
                                                 'attachment': attachment,
                                                 'keyboard': open("keyboards/" + name_keyboard, "r",
                                                                  encoding="UTF-8").read()})
            except vk_api.exceptions:
                sleep(0.5)
                continue
            else:
                sleep(0.2)  # Нужно чтобы бот корректно отправлял несколько сообщений подряд
                break

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
        elif "wall" in answer:  # just wall post, without text
            if "карьерная консультация" not in answer:
                return '', answer, 'none.json'
        return answer, 0, 'none.json'

    @staticmethod
    def get_all_wall_posts(self, offset=0):
        posts = self.person_token.method('wall.get', {'count': config.MAX_COUNT_POSTS,
                                                      'owner_id': -config.group_id,
                                                      'offset': offset})
        return posts

    def create_wall_posts_file(self):
        data = {}
        # for i in range(1):
        for i in range(0, 2000, 100):
            posts = self.get_all_wall_posts(self, i)
            del posts["count"]
            for item in posts["items"]:
                self.wall_parser.redact_post(item)

            if len(data) == 0:
                data.update(posts)
            else:
                data["items"].extend(posts["items"])

        file = open(config.PATH_TO_DATA, "w", encoding="utf8")
        str_json = json.dumps(data,
                              indent=2,
                              ensure_ascii=False,
                              separators=(',', ': ')
                              )
        file.write(str_json)
        file.close()

    @staticmethod
    def get_time():
        now = datetime.now()
        return "Time: " + str(now.strftime("%d-%m-%Y %H:%M"))

    def listening(self):
        vip_users = []
        if len(sys.argv) > 1 and sys.argv[1] == "test":  # Тестовый режим
            vip_users = [467289684, 392239205, 233248602]
        for event in self.longPoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                # я не знаю как по-другому достать данные =)
                data_dict = event.obj.values()
                user_id = -999
                msg_text = - 998
                for item in data_dict:
                    msg_text = item["text"]
                    user_id = item["from_id"]
                    break
                if vip_users and user_id not in vip_users:  # Тестовый режим
                    continue

                # print('For me by: ', end='')
                # print(user_id)
                # print('Text: ', msg_text)

                if user_id not in self.users:
                    self.users[user_id] = VKBOT()

                while True:
                    text = self.get_text_msg(
                        self.users[user_id].processing(msg_text, user_id))
                    self.send_message(user_id, text[0], text[1], text[2])

                    if self.users[user_id].next_command == "any":
                        break
                    if self.users[user_id].next_command == "/admin2022load":
                        self.users[user_id].next_command = 'any'
                        self.create_wall_posts_file()
                        break
            elif event.type == VkBotEventType.WALL_POST_NEW:
                print("New post")
                self.update_file(event.obj)
                self.update_vac()
                self.update_inter()
                self.update_prac()

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

    def update_vac(self):
        Jobs.vacancies = self.wall_parser.select_posts(1)

    def update_inter(self):
        Jobs.internships = self.wall_parser.select_posts(2)

    def update_prac(self):
        Jobs.practices = self.wall_parser.select_posts(3)

    def update_file(self, new_post):
        new_post = self.wall_parser.redact_post(new_post)
        with open(config.PATH_TO_DATA, "r", encoding="utf8") as file:
            posts = json.load(file)
            # posts["items"].append(new_post)
            posts["items"] = [new_post] + posts["items"]

        with open(config.PATH_TO_DATA, "w", encoding="utf8") as file:
            str_json = json.dumps(posts,
                                  indent=2,
                                  ensure_ascii=False,
                                  separators=(',', ': ')
                                  )
            file.write(str_json)
