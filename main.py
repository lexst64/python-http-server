import sqlite3
import cgi
import json
import socket
from typing import Dict, Tuple, TypeVar
from http.server import BaseHTTPRequestHandler, HTTPServer
from utils import verify_user_data, UserDataVerifyError
from urllib.parse import urlparse, parse_qs


PORT = 5000
DB_PATH = 'Chinook_Sqlite.sqlite'
PATH_PARSE_SCHEME = '<path>;<params>?<query>#<fragment>'


Code = TypeVar('Code', int, int)
Message = TypeVar('Message', str, str)
Keyword = TypeVar('Keyword', str, str)
Value = TypeVar('Value', str, str)


def dict_to_json_string(__dict: dict, encode: bool = False) -> str | bytes:
    if encode:
        return json.dumps(__dict).encode('utf-8')
    return json.dumps(__dict)


def generate_http_headers(content_type='text/html', charset='utf-8', content_language='en'):
    headers = {
        'Content-type': f'{content_type}; charset={charset}',
        'Content-language': content_language,
        'Access-Control-Allow-Origin': '*',
        'Vary': 'Cookie, Accept-Encoding',
        'X-Cache-Info': 'not cacheable; meta data too large',
        'Transfer-Encoding': 'chunked',
    }
    return headers


def search_words_by_match(sorted_words: list | tuple, match: str) -> list:
    match = match.lower().strip()

    if not sorted_words:
        return sorted_words

    mid_index = len(sorted_words) // 2

    guess = sorted_words[mid_index]
    guess_part = guess[:len(match)].lower()

    if guess_part == match:
        sorted_words_copy = list(sorted_words)
        del sorted_words_copy[mid_index]
        return [guess] + search_words_by_match(sorted_words_copy, match)
    elif guess_part > match:
        return search_words_by_match(sorted_words[:mid_index], match)
    else:
        return search_words_by_match(sorted_words[mid_index + 1:], match)


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


def GET_main(http_request_handler: BaseHTTPRequestHandler, queries: dict):
    headers = generate_http_headers()
    with open('assets/index.html') as file:
        data: bytes = ''.join(file).encode('utf-8')
    send_response(http_request_handler, (200, 'OK'),
                  headers=headers, data=data)


def GET_nicknames(http_request_handler: BaseHTTPRequestHandler, queries: dict):
    headers = generate_http_headers('application/json')
    nicknames = get_nicknames_from_database()
    nicknames.sort()
    data = {
        'nicknames': nicknames,
    }

    if 'match' in queries:
        match = queries['match']
        found_nicknames = search_words_by_match(nicknames, match)
        data['nicknames'] = found_nicknames
    
    data = dict_to_json_string(data, True)
    send_response(http_request_handler, (200, 'OK'),
                  headers=headers, data=data)


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
def process_form(form: cgi.FieldStorage, params: list):
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
            'headers': generate_http_headers('application/json'),
            'data': dict_to_json_string({'error': str(err)}, True),
        }
    return generator


class CustomError(Exception):
    ...


CODES = {
    500: 'Internal Server Error',
    400: 'Bad Request',
    200: 'OK',
    404: 'Page Not Found',
}


def create_error_data(error_message: str) -> bytes:
    data = {
        'error_message': str(error_message),
    }
    return dict_to_json_string(data, True)


def POST_new_user(http_request_handler: BaseHTTPRequestHandler, queries: dict):
    headers = generate_http_headers('application/json')

    data = get_json_request_body(http_request_handler)

    try:
        params = {
            'nickname': data['nickname'],
            'name': data['name'],
            'password': data['password'],
        }
        add_user_to_database(**params)
    except KeyError as err:
        error_data = create_error_data(f'{err} param is missing')
        send_response(http_request_handler, (400, CODES[400]), headers=headers, data=error_data)
    except sqlite3.DatabaseError as err:
        error_data = create_error_data(f'database error: {err}')
        send_response(http_request_handler, (500, CODES[500]), headers=headers, data=error_data)
    except UserDataVerifyError as err:
        error_data = create_error_data(err)
        send_response(http_request_handler, (400, CODES[400]), headers=headers, data=error_data)
    else:
        send_response(http_request_handler, (200, CODES[200]), headers=headers)


def GET_page_not_found(http_request_handler: BaseHTTPRequestHandler, queries: dict):
    headers = generate_http_headers()
    with open('assets/page_not_found.html') as file:
        data = ''.join(file).encode('utf-8')
    send_response(http_request_handler, (404, CODES[404]),
                  headers=headers, data=data)


ROUTES = {
    # get-s
    '/': GET_main,
    '/nicknames': GET_nicknames,
    # post-s
    '/user/register': POST_new_user,
}


def get_content_length(http_request_handler: BaseHTTPRequestHandler) -> int:
    length: int | str = http_request_handler.headers.get('content-length', 0)
    return int(length)


def get_json_request_body(http_request_handler: BaseHTTPRequestHandler) -> dict:
    length = get_content_length(http_request_handler)
    data = json.loads(http_request_handler.rfile.read(length))
    return data


class CustomHTTPRequestHandler(BaseHTTPRequestHandler):
    def parse_path(self) -> dict:
        parsed_path = urlparse(self.path, PATH_PARSE_SCHEME)
        queries = parse_qs(parsed_path.query)
        # TODO: process error when strict mode is enebaled in parse_qs() ^
        queries = {key: value.pop() for key, value in queries.items()}
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
            GET_page_not_found(self, parsed_path['queries'])

    def do_POST(self):
        parsed_path = self.parse_path()
        try:
            ROUTES[parsed_path['path']](self, parsed_path['queries'])
        except KeyError:
            # TODO: implement error processing when path doesn't exist
            pass


def run():
    # ip_addr = socket.gethostbyname(socket.gethostname())
    ip_addr = 'localhost'
    http_server = HTTPServer((ip_addr, PORT), CustomHTTPRequestHandler)
    try:
        print(ip_addr)
        http_server.serve_forever()
    except KeyboardInterrupt:
        http_server.server_close()
    except Exception as err:
        raise err


if __name__ == '__main__':
    run()
