import json
from time import sleep

import redis
from requests import Response, get

from settings import SiteSettings

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
site = SiteSettings()

URL = "https://movie-database-alternative.p.rapidapi.com/"
HEADERS = {
    "X-RapidAPI-Key": site.api_key.get_secret_value(),
    "X-RapidAPI-Host": "movie-database-alternative.p.rapidapi.com"
}


def _make_respond(querystring: dict, timeout: int) -> Response | int:
    respond = get(URL, headers=HEADERS, params=querystring, timeout=timeout)

    sc = respond.status_code

    if sc == 200:
        return respond
    elif sc in (429, 520):
        sleep(1)
        return _make_respond(querystring, timeout)
    print(sc)
    print(respond.text)
    return sc


def _get_by_search(title: str, timeout=5, t_type: str = None,
                   year: int = None, page: int = 1) -> Response | int:
    if year:
        year = str(year)

    params = {"s": title, "r": "json", "type": t_type, "y": year,
              "page": str(page)}
    return _make_respond(params, timeout)


def _get_by_id(imdb_id: str, timeout=5, year: int = None, t_type: str = None,
               plot: str = None) -> dict:
    cache_key = f'{imdb_id}:{year}:{t_type}:{plot}'
    cached_response = redis_client.get(cache_key)

    if cached_response:
        return json.loads(cached_response.decode("utf-8"))

    if year:
        year = str(year)

    params = {"r": "json", "i": imdb_id, "y": year, "type": t_type,
              "plot": plot}

    response = _make_respond(params, timeout)
    redis_client.setex(cache_key, 3600, json.dumps(response.json()))

    return response.json()


class SiteApiInterface:
    @classmethod
    def get_by_search(cls):
        return _get_by_search

    @classmethod
    def get_by_id(cls):
        return _get_by_id


if __name__ == '__main__':
    print(_get_by_search("Batman").json())