import requests
from contextlib import contextmanager
from multiprocessing import Pool

from resource.py import Log
from resource.py.media.ingest import get_pb_domain_set

__author__ = 'gmena'


class YTS(object):
    def __init__(self, host: str, page: int = 0, limit: int = 50):
        # ignore 400 cause by IndexAlreadyExistsException when creating an index

        # CONSTANTS
        self.YTS_HOST = host
        self.YTS_RECURSIVE_LIMIT = limit  # limit result per page (step)

        self.yts_recursive_page = page  # start page
        self.yts_movies_indexed = dict()  # indexed
        self.req_session = requests.Session()
        self.pb_match = get_pb_domain_set()

    @contextmanager
    def request(self, query_string=None):
        """
        Handle http request
        :param query_string:
        :return:
        """
        # Request yifi
        _request: str = self.YTS_HOST + ('?%s' % query_string if query_string else '')
        _cookie = '__cfduid=d69cbd9b1eab1aac23ce5bdf7b56d617e1605989262; adcashufpv3=17981512371092097718392042062; __atuvc=1%7C47%2C5%7C48; PHPSESSID=7r9dv1f37no3qj4dde5hf241h7'
        _agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'

        try:
            conn = self.req_session.get(
                url=_request,
                timeout=60,
                headers={
                    "content-type": "json",
                    'user-agent': _agent,
                    'cookie': _cookie
                }
            )

            # Return json
            yield conn.json()
        except (Exception,) as e:
            print(e)
            yield {}

    def get_movies(self, page):
        # Req YTS
        print(f"Requesting page {str(page)}")
        _uri = 'page=' + str(page) + '&limit=' + str(self.YTS_RECURSIVE_LIMIT) + '&sort=date_added'
        with self.request(_uri) as conn_result:
            # OK 200?
            if 'status' in conn_result and conn_result['status'] != 'ok':
                return False
            if 'movies' not in conn_result['data']:
                return False
            # Yield result
            return conn_result['data']['movies']

    def request_generator(self) -> iter:
        """
        Request yts handler
        :return:
        """

        # Uri
        with self.request() as ping:
            if not 'data' in ping: return False
            total_pages = round(int(ping['data']['movie_count']) / self.YTS_RECURSIVE_LIMIT)
            total_pages = total_pages if self.yts_recursive_page == 0 else self.yts_recursive_page

            print(f"{Log.HEADER}Requesting {str(total_pages)} pages {Log.ENDC}")
            page_list = range(total_pages)

            with Pool(processes=10) as pool:
                p_async = pool.apply_async
                results = {}

                # Generate async pools
                for x in page_list:
                    results[x] = p_async(
                        self.get_movies, args=(x,)
                    )

                # Close pool
                pool.close()
                pool.join()
            # Generate dict with data
            for x, y in results.items():
                yield x, y.get()

    def migrate(self, resource_name: str):
        """
        Elastic migrate
        :param resource_name:
        :return:
        """
        # Get generator
        for page, movie_meta_iter in self.request_generator():
            if not movie_meta_iter:
                continue
            for movie_meta in movie_meta_iter:
                print('indexing ' + movie_meta['title'])
                current_imdb_code_set = {movie_meta['imdb_code']}
                public_domain_movie = self.pb_match.intersection(current_imdb_code_set)

                # Rewrite resource id
                movie_meta['page'] = page
                movie_meta['resource_id'] = movie_meta['id']
                movie_meta['resource_name'] = resource_name
                movie_meta['trailer_code'] = movie_meta['yt_trailer_code']
                movie_meta['pdm'] = bool(public_domain_movie)

                del movie_meta['yt_trailer_code']
                del movie_meta['id']
                del movie_meta['state']
                del movie_meta['url']
                # Push indexed movie
                self.yts_movies_indexed[
                    movie_meta['imdb_code']
                ] = movie_meta

        # Return result
        return self.yts_movies_indexed
