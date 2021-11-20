import time
import requests
import scrape
from flask import Flask
from multiprocessing import Process


DUMMY_REPLY = 'Cool it works lol'
count = 0


def mock_server():
    app = Flask(__name__)

    @app.route('/')
    def dummy():
        return DUMMY_REPLY

    @app.route('/different')
    def counter():
        global count
        count += 1
        return count

    app.run(host='0.0.0.0', port=50000)
    # 50000 is dynamic/private, seems safe
    # see https://en.wikipedia.org/wiki/List_of_TCP_and_UDP_port_numbers


def start_mock():
    print('Starting mock server.')
    proc = Process(target=mock_server)
    proc.start()
    return proc


def stop_mock(proc: Process):
    print('Stopping mock server.')
    proc.terminate()


def test_mock_server_starts():
    server = start_mock()
    assert server.is_alive()
    stop_mock(server)


def test_mock_server_replies():
    server = start_mock()
    assert server.is_alive()
    req = requests.get('http://localhost:50000')
    assert req.status_code == 200
    print(f'{req.status_code}: {req.text}')
    assert req.text == DUMMY_REPLY
    stop_mock(server)


def test_get_page():
    server = start_mock()
    assert server.is_alive()
    req = scrape.get_page('http://localhost:50000')
    assert req.text == DUMMY_REPLY
    stop_mock(server)


def test_safe_filename():
    bad = '&()*#%)@myfile#$(*&#(@./jpg'
    good = 'myfile.jpg'
    new = scrape.safe_filename(bad)
    assert new == good


def test_get_filename():
    url = 'https://example.com/example.txt'
    result = scrape.get_filename(url)
    assert result == 'example.txt'


def test_hash():
    source = b'hello'
    output = scrape.hash_it(source)
    assert output == '2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824'
