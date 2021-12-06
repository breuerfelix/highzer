import os
import requests
from .utils import locate_folder
from .config import UPLOAD_URL, PASSPHRASE


def upload_file(ident, file):
    folder = locate_folder(ident)
    _, ext = os.path.splitext(file)

    with open(f"{folder}/{file}", 'rb') as f:
        headers = { "filename": ident + ext }
        res = requests.post(f"{UPLOAD_URL}/upload", data=f, headers=headers)
        print(res.text)

    return res


def upload_youtube(ident):
    data = {
        "ident": ident,
        "passphrase": PASSPHRASE,
    }

    res = requests.post(f"{UPLOAD_URL}/youtube", json=data)
    return res


def upload_ident(ident):
    upload_file(ident, "merged.mp4")
    upload_file(ident, "meta.json")
    upload_youtube(ident)

