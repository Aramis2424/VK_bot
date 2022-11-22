from _datetime import datetime, timedelta
import json
from config import  PATH_TO_DATA


class WallPostsParser:
    @staticmethod
    def select_posts(neededType=None, count=10):
        time_delta = timedelta(days=count)
        # end_date = datetime(2022, 11, 15)
        end_date = datetime.now() - time_delta
        res = []
        with open(PATH_TO_DATA,  "r", encoding="utf8") as file:
            posts = json.load(file)
            if neededType:
                for item in posts["items"]:
                    if item["info"] == neededType:
                        if datetime.strptime(item["date"], '%d-%m-%Y') < \
                                end_date:
                            break
                        res.append(item)
        return res
