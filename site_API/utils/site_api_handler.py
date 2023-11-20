import json
from time import sleep


from requests import Response, get

from settings import SiteSettings, redis_client


site = SiteSettings()

URL = "https://movie-database-alternative.p.rapidapi.com/"
HEADERS = {
    "X-RapidAPI-Key": site.api_key.get_secret_value(),
    "X-RapidAPI-Host": "movie-database-alternative.p.rapidapi.com"
}


def make_request(query_params: dict, timeout: int) -> Response | int:
    response = get(URL, headers=HEADERS, params=query_params, timeout=timeout)

    if response.status_code == 200:
        return response
    elif response.status_code in (429, 520):
        sleep(1)
        return make_request(query_params, timeout)
    print(response.status_code)
    print(response.text)
    return response.status_code


def get_by_search(title: str, timeout=5, t_type: str = None, year: int = None, page: int = 1) -> Response | int:
    if year:
        year = str(year)

    query_params = {"s": title, "r": "json", "type": t_type, "y": year, "page": str(page)}
    return make_request(query_params, timeout)


def get_by_id(imdb_id: str, timeout=5, year: int = None, t_type: str = None, plot: str = None) -> dict:
    cache_key = f'{imdb_id}:{year}:{t_type}:{plot}'
    cached_response = redis_client.get(cache_key)

    if cached_response:
        return json.loads(cached_response.decode("utf-8"))

    year = str(year) if year else None

    query_params = {"r": "json", "i": imdb_id, "y": year, "type": t_type, "plot": plot}

    response = make_request(query_params, timeout)
    redis_client.setex(cache_key, 3600, json.dumps(response.json()))

    return response.json()


class SiteApiInterface:
    @classmethod
    def get_by_search(cls):
        return get_by_search

    @classmethod
    def get_by_id(cls):
        return get_by_id


if __name__ == '__main__':
    print(get_by_search("Batman").json())
