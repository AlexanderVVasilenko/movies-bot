from requests import Response, get

from settings import SiteSettings

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

    return sc


def _get_by_search(title: str, timeout: int, t_type: str = None,
                   year: int = None, page: int = 1) -> Response | int:
    if year:
        year = str(year)

    params = {"s": title, "r": "json", "type": t_type, "y": year,
              "page": str(page)}
    return _make_respond(params, timeout)


def _get_by_id(imdb_i: str, timeout: int, year: int = None, t_type: str = None,
               plot: str = None) -> Response | int:
    if year:
        year = str(year)

    params = {"r": "json", "i": imdb_i, "y": year, "type": t_type,
              "plot": plot}
    return _make_respond(params, timeout)


class SiteApiInterface:
    @classmethod
    def get_by_search(cls):
        return _get_by_search

    @classmethod
    def get_by_id(cls):
        return _get_by_id
