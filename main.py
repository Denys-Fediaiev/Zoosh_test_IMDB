import logging
import webbrowser

import requests
from bs4 import BeautifulSoup
# Operation:
#
# The application should be able to request a movie title as input for which to download search results from TMDBW with a request (TMDB: The Movie Database Wrapper - https://tmdb.sandbox.zoosh.ie/, graphQL based  API).
#
# Displays the results and some of their data (ID, name, category, score) in a list
#
# Using the ID as another input, the application tries to find the appropriate English wikipedia page (with a REST request) and then displays a summary of it in detail (e.g. first paragraph), with an available link in a new window in IMDB and wikipedia
logging.basicConfig(level=logging.INFO, filename="py_log.log",filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s")

api_url = "https://tmdb.sandbox.zoosh.ie/SearchMovies"


def get_movie():

    movie_title = input("What movie info do you need?\n Type title:\n ")

    body = """
    query SearchMovies {
      searchMovies(query: "$query") {
        id
        name
        overview
        releaseDate
        
      }
    }
    """

    query = body.replace("$query", movie_title)

    response = requests.post(api_url, json={"query": query, "movie_title": movie_title})
    best_match = [response.json()["data"]["searchMovies"][0]]

    # print(response.json())
    print(best_match)


def find_wiki_page():
    movie_id = input('type movie id: \n')

    body = '''
    query getMovie {
  movie(id: $id) {
    id
    name
    overview
  }
}
'''

    query = body.replace("$id", movie_id)

    response = requests.post(api_url, json={"query": query, "movie_id": movie_id})
    id_match = response.json()
    movie_data = id_match["data"]["movie"]
    logging.info(f"Movie data: {movie_data}")

    wikipedia_page_title = movie_data['name']

    search_url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&list=search&srsearch={wikipedia_page_title}&srprop=snippet"

    search_response = requests.get(search_url)
    search_data = search_response.json()
    search_results = search_data.get('query', {}).get('search', [])

    logging.info(f"Top match: {search_results[0]}")

    if not search_results:
        print("No search results found.")
        logging.error("No matches")
    else:
        # Assume the first search result is the most relevant
        wikipedia_title = search_results[0]['title']
        wikipedia_url = f"https://en.wikipedia.org/wiki/{wikipedia_title}"

        wikipedia_response = requests.get(wikipedia_url)
        wikipedia_soup = BeautifulSoup(wikipedia_response.content, "html.parser")

        for link in wikipedia_soup.find_all("a", href=True):
            if "imdb.com/title" in link['href']:
                imdb_id = link["href"].split("/")[-2]
                logging.info(f"Imdb link: {link['href']}")

        imdb_link = f"https://www.imdb.com/title/{imdb_id}"
        wiki_link = f"http://en.wikipedia.org/?curid={search_results[0]['pageid']}"
        soup = BeautifulSoup(search_results[0]['snippet'], features="html.parser")
        print(soup.get_text())
        print(f"IMDB link: {imdb_link}")
        print(f"Wiki link: {wiki_link}")
        webbrowser.open_new(imdb_link)
        webbrowser.open_new(wiki_link)


on = True
while on:
    choice = input("~~~MENU~~~\n Please choose your option:\n 1.Search movie by its title\n 2.Search movie by ID\n 3.Stop\n")
    if choice == "1":
        # movie = input("Type movie title\n")
        get_movie()
        go_on = input('Do you want to find Wikipedia page or return to menu?\n 1.Search by ID\n 2.Menu\n')
        if go_on == "1":
            find_wiki_page()
        elif go_on == "2":
            pass
        else:
            "Error Try again"

    elif choice == "2":
        find_wiki_page()

    elif choice == "3":
        on = False

    else:
        on = False
        print("Error, try again!")


