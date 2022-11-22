from _datetime import datetime, timedelta
import json
from config import PATH_TO_DATA


class WallPostsParser:
    @staticmethod
    def select_posts(neededType=None, count=10):
        # time_delta = timedelta(days=count)
        # end_date = datetime(2022, 11, 15)
        # end_date = datetime.now() - time_delta
        res = []
        with open(PATH_TO_DATA,  "r", encoding="utf8") as file:
            posts = json.load(file)
            if neededType:
                for item in posts["items"]:
                    if item["info"] == neededType:
                        # if datetime.strptime(item["date"], '%d-%m-%Y') < \
                        #         end_date:
                        #     break
                        res.append(item)
        return res

    @staticmethod
    def redact_post(post):
        words_to_del = [
            "donut",
            "short_text_rate",
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

        for word in words_to_del:
            if word in post:
                del post[word]
        if "date" in post:
            ut = post["date"]
            post["date"] = \
                datetime.utcfromtimestamp(ut).strftime('%d-%m-%Y')

        post_type = 0
        if "text" in post:
            text = post["text"].split('\n')
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

        post["info"] = post_type

        return post
