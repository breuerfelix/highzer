import os

# this is the official Client-ID which is being used
# by everyone who is not logged in to twitch.tv while using the website
# no need to worry that i put it here (:
CLIENT_ID = "kimne78kx3ncx6brgo4mv6wki5h1ko"

# upload
UPLOAD_URL = os.getenv("UPLOAD_URL", "http://localhost:80")
PASSPHRASE = os.getenv("PASSPHRASE", "uploadpy")
