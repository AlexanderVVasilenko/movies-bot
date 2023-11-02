from site_API.core import site_api

titles_by_search = site_api.get_by_search()
title_by_id = site_api.get_by_id()

respond = titles_by_search("Avengers", timeout=5, page=1).json()

print(respond)
