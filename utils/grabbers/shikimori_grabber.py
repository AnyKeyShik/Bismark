# -*- coding: utf-8 -*-

import json
import re
from random import randint

from .api_builder import ApiBuilder
from exceptions import AnimeNotFoundException

headers = {
    "User-Agent": "Bismark Bot",
    # "Authorization": "there is your secret key",
}

API = ApiBuilder("https://shikimori.org/", headers=headers)

forum_tag = re.compile("""\[[^\]^\[]*\]""", re.X)


class ShikimoriGrabber(object):
    def get_anime(self, name):
        anime_id = self.__find_anime_by_name(name)

        return self.__get_anime_stats(anime_id)

    @staticmethod
    def __find_anime_by_name(name):
        data = json.loads(API.api.animes.get(search=name))
        if data:
            id = data[0]["id"]
        else:
            raise AnimeNotFoundException("Anime by query \"{}\" is not found".format(name))
        return id

    @staticmethod
    def __get_summary_comments(anime_id, starting_page=1, page_limit=5):
        for page in range(starting_page, starting_page + page_limit):
            comments = json.loads(
                API.api.comments.get(commentable_id=anime_id, commentable_type="Topic", limit=30, page=page)
            )
            for comment in comments:
                if comment["is_summary"]:
                    yield comment

    @staticmethod
    def __get_anime_stats(anime_id):
        anime = json.loads(API.api.animes[anime_id].get())
        name = anime["name"]
        score = anime["score"]
        topic_id = anime["topic_id"]
        all_reviews = []
        if topic_id:
            for comment in ShikimoriGrabber.__get_summary_comments(topic_id, page_limit=5):
                all_reviews.append(comment["body"])
                if len(all_reviews) > 30:
                    break
        if all_reviews:
            review = all_reviews[randint(0, len(all_reviews) - 1)]
        else:
            review = "Не нашлось"
        review = forum_tag.sub("", review)
        return (
            "Полное название: {}\n"
            "Оценка: {}\n"
            "Отзыв:\n{}\n"
        ).format(name, score, review)

# a = ShikimoriGrabber()
# id = a.find_anime_by_name("SAO")
# print(a.get_anime_stats(id))
#
#
# r = requests.get(
#     "https://shikimori.org/api/users/whoami",
#     headers=headers
# )
#
# print(r.text)
