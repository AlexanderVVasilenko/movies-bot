import concurrent.futures
from typing import Optional

from site_API.utils.site_api_handler import SiteApiInterface

querystring = {"s": "Avengers Endgame", "r": "json", "page": "1"}

site_api = SiteApiInterface()


def sorting_func(movie: dict) -> float:
    return float(movie["imdbRating"])


def get_movie_info(movie: dict) -> Optional[dict]:
    imdb_id = movie["imdbID"]
    movie_info = site_api.get_by_id()(imdb_id)
    return movie_info if movie_info["imdbRating"] != "N/A" else None


def _get_full_info_by_search(text: str) -> list[dict]:
    movies = []
    page_cnt = 0
    print(site_api.get_by_search()(title=text).json())
    page_amt = int(site_api.get_by_search()(title=text).json().get("totalResults"))
    if page_amt > 1000:
        return []

    while True:
        page_cnt += 1
        respond = site_api.get_by_search()(title=text, page=page_cnt).json()
        if respond["Response"] == "True":
            movies += respond["Search"]
        else:
            break

    with concurrent.futures.ThreadPoolExecutor() as executor:
        movie_info_list = list(executor.map(get_movie_info, movies))

    return [movie_info for movie_info in movie_info_list if movie_info is not None]


def get_movies_sorted_by_rating(title: str, amount: int, reverse: bool = False) -> list[dict]:
    movies_full_info = _get_full_info_by_search(title)
    sorted_by_rating = sorted(filter(None, movies_full_info), key=sorting_func, reverse=reverse)
    return sorted_by_rating[:amount]


def get_low(title: str, amount: int) -> list[dict]:
    return get_movies_sorted_by_rating(title, amount)


def get_high(title: str, amount: int) -> list[dict]:
    return get_movies_sorted_by_rating(title, amount, reverse=True)


def get_custom(title: str, min_rating: float, max_rating: float, amount: int) -> list[dict]:
    movies_full_info = _get_full_info_by_search(title)
    sorted_by_rating = sorted(filter(None, movies_full_info), key=sorting_func, reverse=True)

    index_max = next(
        (index for index, movie in enumerate(sorted_by_rating) if float(movie["imdbRating"]) <= max_rating), 0)
    index_min = next((index for index in range(len(sorted_by_rating) - 1, -1, -1) if
                      float(sorted_by_rating[index]["imdbRating"]) >= min_rating), len(sorted_by_rating))

    result = sorted_by_rating[index_max:index_min]
    return result[:amount]


if __name__ == '__main__':
    print(get_low("One Piece", 5))
