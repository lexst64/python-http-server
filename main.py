import sqlite3
import cgi
import json
from typing import Dict, Tuple, TypeVar
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse
from utils import verify_user_data, UserDataVerifyError
from urllib.parse import urlparse, parse_qs, ParseResult


DB_PATH = 'Chinook_Sqlite.sqlite'
PATH_PARSE_SCHEME = '<path>;<params>?<query>#<fragment>'


Code = TypeVar('Code', int, int)
Message = TypeVar('Message', str, str)
Keyword = TypeVar('Keyword', str, str)
Value = TypeVar('Value', str, str)


def search_words_by_match(sorted_words: list|tuple, match: str) -> list:
        sorted_words = sorted_words.copy()
        match = match.lower()

        found_words = []
        low = 0
        high = len(sorted_words) - 1
        while high >= low:
            mid = (high + low) // 2

            guess: str = sorted_words[mid]
            guess_part = guess[:len(match)].lower()
            
            if guess_part == match:
                found_words.append(sorted_words[mid])
                del sorted_words[mid]
                high = len(sorted_words) - 1
            elif guess_part > match:
                high = mid - 1
            else:
                low = mid + 1
        return found_words


def send_response(
    http_request_handler: BaseHTTPRequestHandler,
    response: Tuple[Code, Message],
    *,
    headers: Dict[Keyword, Value] = None,
    data: bytes = None,
):
    http_request_handler.send_response(*response)
    if headers:
        for key, value in headers.items():
            http_request_handler.send_header(key, value)
    http_request_handler.end_headers()
    if data:
        http_request_handler.wfile.write(data)


def get_main(http_request_handler: BaseHTTPRequestHandler, queries: dict):
    headers = {
        'Content-type': 'text/html',
        'Content-language': 'en',
    }
    with open('assets/index.html') as file:
        data: bytes = ''.join(file).encode('utf-8')
    send_response(http_request_handler, (200, 'OK'),
                  headers=headers, data=data)


def get_nicknames(http_request_handler: BaseHTTPRequestHandler, queries: dict):
    headers = {
        'Content-type': 'application/json',
        'Content-language': 'en',
    }
    nicknames = get_nicknames_from_database()
    nicknames.sort()
    data = {
        'nicknames': nicknames,
    }
    if queries:
        match = queries['match'][-1]
        found_nicknames = search_words_by_match(nicknames, match)
        data['nicknames'] = found_nicknames
    data = json.dumps(data).encode('utf-8')
    send_response(http_request_handler, (200, 'OK'), headers=headers, data=data)


def add_user_to_database(*, nickname: str, name: str, password: str):
    # raises UserDataVerifyError if failed
    verify_user_data(nickname, name, password)
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    params = {
        'nickname': nickname,
        'name': name,
        "password": password,
    }
    cursor.execute(
        'insert into User values (Null, :nickname, :name, :password)', params)
    connection.commit()
    connection.close()


def get_nicknames_from_database() -> list:
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute('select Nickname from User')
    # cursor.fetchall() returns a list of tuples that contain names
    nicknames = [nickname[0] for nickname in cursor.fetchall()]
    connection.close()
    return nicknames


# TODO: rename function
def fn(form: cgi.FieldStorage, params: list):
    result_params = {}
    for param in params:
        value = form.getvalue(param)
        if value is None:
            raise CustomError('param error')
        result_params[param] = value
    return result_params


def create_response_args_generator(http_request_handler, ):
    def generator(err, *, code=500, desc=''):
        return [http_request_handler, (code, desc)], {
            'headers': {'Content-Type': 'application/json'},
            'data': json.dumps({'error': str(err)}).encode('utf-8'),
        }
    return generator


class CustomError(Exception):
    ...


CODES = {
    500: {'code': 500, 'desc': 'Internal Server Error'},
    400: {'code': 400, 'desc': 'Bad Request'},
}


def register_new_user(http_request_handler: BaseHTTPRequestHandler, queries: dict):
    headers = {'Content-type': 'plain/text'}
    form = cgi.FieldStorage(
        http_request_handler.rfile,
        http_request_handler.headers,
        environ={'REQUEST_METHOD': 'POST'},
    )
    try:
        params = fn(form, ['nickname', 'password', 'name'])
        add_user_to_database(**params)
    except Exception as err:
        error_args_generator = create_response_args_generator(
            http_request_handler)
        error_response = {
            UserDataVerifyError: CODES[400],
            sqlite3.DatabaseError: CODES[500],
            CustomError: CODES[400],
            'default': CODES[500],
        }
        arg1, arg2 = error_args_generator(
            err, **(error_response.get(type(err)) or error_response.get('default')))
        send_response(*arg1, **arg2)
    else:
        send_response(http_request_handler, (200, 'OK'), headers=headers)


def get_page_not_found(http_request_handler: BaseHTTPRequestHandler, queries: dict):
    headers = {
        'Content-type': 'text/html',
        'Content-language': 'en',
    }
    with open('assets/page_not_found.html') as file:
        data: bytes = ''.join(file).encode('utf-8')
    send_response(http_request_handler, (404, 'page not found'),
                  headers=headers, data=data)


ROUTES = {
    # get-s
    '/': get_main,
    '/nicknames': get_nicknames,
    # post-s
    '/user/register': register_new_user,
}


class CustomHTTPRequestHandler(BaseHTTPRequestHandler):
    def parse_path(self) -> dict:
        parsed_path = urlparse(self.path, PATH_PARSE_SCHEME)
        queries = parse_qs(parsed_path.query)
        # TODO: process error when strict mode is enebaled in parse_qs() ^
        parse_result = {
            'path': parsed_path.path,
            'queries': queries,
        }
        return parse_result

    def do_GET(self):
        parsed_path = self.parse_path()
        try:
            ROUTES[parsed_path['path']](self, parsed_path['queries'])
        except KeyError:
            get_page_not_found(self, parsed_path['queries'])

    def do_POST(self):
        parsed_path = self.parse_path()
        try:
            ROUTES[parsed_path['path']](self, parsed_path['queries'])
        except KeyError:
            # TODO: implement error processing when path doesn't exist
            pass


def run():
    http_server = HTTPServer(('localhost', 5000), CustomHTTPRequestHandler)
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        http_server.server_close()
    except Exception as err:
        raise err


if __name__ == '__main__':
    run()
