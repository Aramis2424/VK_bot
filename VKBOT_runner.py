import vk_api
from vk_bot import VKBOT
from vk_api.longpoll import VkLongPoll, VkEventType
from random import randint
import config


def send_message(user_id, message, attachment=0, keyboard='none'):
    vk.method('messages.send', {'peer_id': user_id,
                                'message': message,
                                'random_id': randint(-1024, 1024),
                                'attachment': attachment,
                                'keyboard': open("keyboards/" + keyboard + ".json", "r", encoding="UTF-8").read()})


def get_all_wall_posts():
    person_token = vk_api.VkApi(token=config.vk_api_person_token)
    posts = person_token.method('wall.get', {'count': config.MAX_COUNT_POSTS,
                                             'owner_id': -config.group_id})
    return posts


# Авторизуемся как сообщество
vk = vk_api.VkApi(token=config.vk_api_group_token)

# Работа с сообщениями
longpoll = VkLongPoll(vk)

# Словарь, где будут хранится разные объекты бота для разных пользователей
users_bot_class_dict = {}


def run():
    print("Server started")
    for event in longpoll.listen():

        if event.type == VkEventType.MESSAGE_NEW:

            if event.to_me:

                print('New message:')
                print('For me by: ', end='')

                print(event.user_id)

                user_id = event.user_id
                if user_id not in users_bot_class_dict:
                    users_bot_class_dict[user_id] = VKBOT()

                # Checking to welcome message send
                if not users_bot_class_dict[user_id].WELCOME_MSG_SEND:
                    send_message(event.user_id,
                                 users_bot_class_dict[user_id].get_welcome_msg(event.user_id))

                # Строка с текстом ответа
                # text[0] - сам текст
                # text[1] - прикрепление (attacment)
                text = users_bot_class_dict[user_id].update_screen(event.text)
                send_message(event.user_id, text[0], text[1])

                print('Text: ', event.text)
                print()
