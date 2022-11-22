from random import randint
from requests import exceptions
import os
import sys
import traceback
from datetime import datetime
from time import sleep

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
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
        self.longPoll = VkLongPoll(self.vk)

        # users dict
        self.users = {}

        self.wall_parser = wallPosts_parser.WallPostsParser()

        # TODO: эти же функции нужно запускать при событии новый пост
        # Начальная установка массивов
        self.update_vac()
        self.update_inter()
        self.update_prac()

    def send_message(self, user_id, message, attachment, name_keyboard):
        for i in range(3):
            try:
                self.vk.method('messages.send', {'user_id': user_id,
                                                 'message': message,
                                                 'random_id': randint(-1024, 1024),
                                                 'attachment': attachment,
                                                 'keyboard': open("keyboards/" + name_keyboard, "r",
                                                                  encoding="UTF-8").read()})
            except:  # TODO посмотреть какие бывают ошибки
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

    # TODO: удалить это
    def create_wall_posts_file(self):
        words_to_del = [
            "attachments",
            "post_source",
            "is_pinned",
            # "date",
            "comments",
            "likes",
            "reposts",
            "zoom_text",
            "hash",
            "from_id",
            "owner_id",
            "marked_as_ads",
            "can_delete",
            "is_favorite",
            "post_type",
            "can_pin",
            "postponed_id",
            "views",
            "can_edit",
            "created_by"
        ]
        data = {}

        # for i in range(0, 1700, 100):
        for i in range(1):
            posts = self.get_all_wall_posts(self, i)
            del posts["count"]
            for item in posts["items"]:
                for word in words_to_del:
                    if word in item:
                        del item[word]
                if "date" in item:
                    ut = item["date"]
                    item["date"] = \
                        datetime.utcfromtimestamp(ut).strftime('%d-%m-%Y')

                post_type = 0
                if "text" in item:
                    text = item["text"].split('\n')
                    # print(text)
                    if len(text) > 1:
                        if 'вакансия' in text[0].lower() or \
                                'вакансия' in text[1].lower():
                            post_type = 1
                        elif 'стажировка' in text[0].lower() or \
                                'стажировка' in text[1].lower():
                            post_type = 2
                        elif 'практика' in text[0].lower() or \
                                'практика' in text[1].lower():
                            post_type = 3

                item["info"] = post_type

            if len(data) == 0:
                data.update(posts)
            else:
                data["items"].extend(posts["items"])

        file = open(config.PATH_TO_DATA, "w")
        str_json = json.dumps(data,
                              indent=2,
                              ensure_ascii=False,
                              separators=(',', ': ')
                              )
        file.write(str_json)
        file.close()
        print('here')

    @staticmethod
    def get_time():
        now = datetime.now()
        return "Time: " + str(now.strftime("%d-%m-%Y %H:%M"))

    def listening(self):
        for event in self.longPoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    print('For me by: ', end='')
                    print(event.user_id)
                    print('Text: ', event.text)

                    user_id = event.user_id
                    if user_id not in self.users:
                        self.users[user_id] = VKBOT()

                    while True:
                        text = self.get_text_msg(
                            self.users[user_id].processing(event.text, event.user_id))
                        self.send_message(event.user_id, text[0], text[1], text[2])

                        if self.users[user_id].next_command == "any":
                            break
                        if self.users[user_id].next_command == "/admin2022load":
                            self.users[user_id].next_command = 'any'
                            self.create_wall_posts_file()
                            break

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
