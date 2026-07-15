# /// script
# requires-python = ">=3.11,<3.12"
# dependencies = [
#     "python-aternos",
#     "python-dotenv",
# ]
# ///
#
# !!!
# TODO: THIS IS NOT WORKING, NO FILES !
# !!!
from getpass import getpass
from dotenv import load_dotenv
import os
from pathlib import Path
from python_aternos import Client
# >> https://python-aternos.codeberg.page/howto/files/
#
load_dotenv(Path.home() / ".env")   # explicit path since it's not in cwd

atclient = Client()
user = os.environ["ATERNOS_USER"]
password = os.environ["ATERNOS_PASS"]

atclient = Client()
atclient.login(os.environ["ATERNOS_USER"], os.environ["ATERNOS_PASS"])

aternos = atclient.account

s = aternos.list_servers()[2]
files = s.files()

while True:

    inp = input('> ').strip()
    cmd = inp.lower()

    if cmd == 'help':
        print(
            '''Commands list:
            help - show this message
            quit - exit from the script
            world - download the world
            list [path] - show directory (or root) contents'''
        )

    if cmd == 'quit':
        break

    elif cmd.startswith('list'):
        path = inp[4:].strip()
        directory = files.list_dir(path)

        print(path, 'contains:')
        for file in directory:
            print('\t' + file.name)

    elif cmd == 'world':
        file = files.get_file('/world')
        with open('world.zip', 'wb') as f:
            f.write(file.get_content())

    elif cmd == 'list2':

        for f in files.list_dir(''):
            print('root:', f.path, '(dir)' if f.is_dir else f.size)

        for f in files.list_dir('world'):        # go inside the world dir
            print('world:', f.path, '(dir)' if f.is_dir else f.size)
