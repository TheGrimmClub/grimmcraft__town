# /// script
# requires-python = ">=3.11,<3.12"
# dependencies = [
#     "python-aternos==3.0.4",
#     "python-dotenv",
# ]
# ///
#
# !!!
# TODO: THIS IS NOT WORKING, NO FILES !
# !!!
import os
from pathlib import Path
from dotenv import load_dotenv  # pyright: ignore[reportMissingImports]
from python_aternos import Client  # pyright: ignore[reportMissingImports]
from python_aternos.atconnect import AJAX_URL
# >> https://python-aternos.codeberg.page/howto/files/

debug = False

load_dotenv(Path.home() / ".env")   # explicit path since it's not in cwd

atclient = Client()
atclient.login(os.environ["ATERNOS_USER"], os.environ["ATERNOS_PASS"])

aternos = atclient.account

servers = aternos.list_servers()


s = aternos.list_servers()[0]

if debug:
    print(vars(s))                 # see the raw attributes
    # or:
    print([a for a in dir(s) if not a.startswith('_')])

    for i, s in enumerate(aternos.list_servers()):
        s.fetch()                 # populate _info
        print(i, s.servid)
        print(s._info)            # raw dict — see what keys actually exist




def download_world(server, world='world'):
    resp = server.atserver_request(
        f'{AJAX_URL}/worlds/download.php',   # <-- comma here
        'GET',
        params={'world': world},
    )
    return resp.content

for id,server in enumerate(servers):
    data = download_world(server, 'world')
    with open(f'world__{id}.zip', 'wb') as f:
        f.write(data)
    print('saved', len(data), 'bytes')
