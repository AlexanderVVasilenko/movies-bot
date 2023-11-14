import concurrent.futures
import functools

from site_API.utils.site_api_handler import SiteApiInterface

querystring = {"s": "Avengers Endgame", "r": "json", "page": "1"}

site_api = SiteApiInterface()


def sorting_func(movie: dict) -> float:
    return float(movie["imdbRating"])


def get_movie_info(movie):
    imdb_id = movie["imdbID"]
    movie_info = site_api.get_by_id()(imdb_id)
    if movie_info["imdbRating"] != "N/A":
        return movie_info
    else:
        return None


def _get_full_info_by_search(text: str) -> list:
    movies = []
    page_cnt = 0
    page_amt = int(site_api.get_by_search()(title=text).json()["totalResults"])
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

    print(len(movie_info_list))
    print(movie_info_list)
    return movie_info_list
    # sorted_by_rating = sorted(filter(None, movie_info_list), key=sorting_func)
    # print(len(sorted_by_rating))
    # return sorted_by_rating[:amount]


def get_low(title: str, amount: int) -> list:
    movies_full_info = _get_full_info_by_search(title)
    sorted_by_rating = sorted(filter(None, movies_full_info), key=sorting_func)
    return sorted_by_rating[:amount]


def get_high(title: str, amount: int) -> list:
    movies_full_info = _get_full_info_by_search(title)
    sorted_by_rating = sorted(filter(None, movies_full_info),
                              key=sorting_func, reverse=True)
    return sorted_by_rating[:amount]

# def get_low(text: str, amount: int) -> list:
#     movies = []
#     page_cnt = 0
#     while True:
#         page_cnt += 1
#         respond = site_api.get_by_search()(title=text, page=page_cnt).json()
#         if respond["Response"] == "True":
#             movies += respond["Search"]
#         else:
#             break
#
#     full_info_movies = [site_api.get_by_id()(movie["imdbID"]).json()
#                         for movie in movies
#                         if site_api.get_by_id()(movie["imdbID"]).json()[
#                             "Metascore"] != "N/A"]
#
#     sorted_by_rating = sorted(full_info_movies, key=sorting_func)
#     return sorted_by_rating[:amount]


if __name__ == '__main__':
    print(get_low("One Piece", 5))
