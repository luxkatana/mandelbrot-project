from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import ThreadedFTPServer

import shutil
import os
from secrets import choice
import string

HOMEDIR: str | None = None
if HOMEDIR is None:
    dirname = os.path.join(os.path.dirname(__file__), "mandelbrot_buffer")
    if os.path.exists(dirname) is True:
        shutil.rmtree(dirname)
    os.mkdir(dirname)
    HOMEDIR = dirname

length: int
random_string = lambda length: "".join(
    [choice(string.printable) for _ in range(length)]
)


def create_authorizer():
    return DummyAuthorizer()


def create_user(authorizer: DummyAuthorizer) -> tuple[str, str]:
    user = random_string(10)
    password = random_string(20)
    authorizer.add_user(user, password, HOMEDIR, "w")
    return (user, password)


def create_ftp_server(
    authorizer: DummyAuthorizer, addr: tuple[str, int]
) -> ThreadedFTPServer:
    handler = FTPHandler
    handler.authorizer = authorizer
    return ThreadedFTPServer(addr, handler)
