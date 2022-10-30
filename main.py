import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

from VK_bot import VkBot


def write_msg(user_id, message, attachment = 0):
    vk.method('messages.send', {'user_id': user_id,
                                'message': message,
                                'random_id': 0,     # Change randim
                                'attachment': attachment})

def get_all_wallPosts():
    wallToken = 'vk1.a.fQ65PvLwGGZPhjNMwsdv64UHI1yH5BA0vkGXyX2mldBDz5v_KW8ybJSXVNAhYTAnpG-wx9JqPPlFFOqZf6ZrGmdugzXxvzE2XlDs-yP8I7Pl0a3im1wl_Z2VcTi_mq-LDbF74EhgCacmqP8CZox1YXDIJAKK5sPgLG3DsbB2TYpHpSQiPbmUmF5XJDTsW3M2-UHcD6YqQocdBAvqxuCp6Q'
    WallVK = vk_api.VkApi(token=wallToken)
    print(WallVK.method('wall.get', {'count': 2,
                           'owner_id': -216704539})
         )

# API-ключ созданный ранее
token = "vk1.a.CQPil15hv85vAv3vZTQAK-rDVvsO11NZNIUkSeppoWPiA6TPQEKuQHAiIF8nH8GHWn1QJPiGuHSD8n14L0P3xG4QRRKQNn738DL--45JsyQO8KYuoaiWKbTnDUD2XDLX8Yy8dRDVD2F1-t9uECMhiwn694A4R4Mhqm2fGHuEU7vJj-XaB-e2KBmEDrp1Yka4lrQFfX1XcsQVbEziFwVILw"

# Авторизуемся как сообщество
vk = vk_api.VkApi(token=token)

# Работа с сообщениями
longpoll = VkLongPoll(vk)

# Основной цикл
for event in longpoll.listen():
    print("Server started")
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:

                print('New message:')
                print(f'For me by: {event.user_id}', end='')

                if event.text == 'Все записи':
                    get_all_wallPosts()
                    continue

                bot = VkBot(event.user_id)
                write_msg(event.user_id, bot.new_message(event.text),
                            bot.get_wallPost(event.text))

                print('Text: ', event.text)