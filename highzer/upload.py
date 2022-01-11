import requests
from .utils import locate_folder
from .config import UPLOAD_URL, PASSPHRASE


def upload_file(ident, file, filename):
    folder = locate_folder(ident)

    with open(f"{folder}/{file}", 'rb') as f:
        headers = { "filename": filename }
        res = requests.post(f"{UPLOAD_URL}/upload", data=f, headers=headers)
        print(res.text)

    return res


def upload_youtube(ident):
    data = {
        "ident": ident,
        "passphrase": PASSPHRASE,
    }

    return requests.post(f"{UPLOAD_URL}/youtube", json=data)


def upload_ident(ident, meta, dest = None):
    if not dest:
        dest = ident

    upload_file(ident, "merged.mp4", f"{dest}.mp4")
    upload_file(meta, "meta.json", f"{dest}.json")
    upload_youtube(dest)

