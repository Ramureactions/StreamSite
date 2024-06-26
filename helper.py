import re
import urllib.parse

import validators
from hashids import Hashids

from config import (
    HASH_SALT,
    NEW_DL_BASE_URL,
    NEW_DL_BASE_URL_3,
    OLD_DL_BASE_URL_1,
    OLD_DL_BASE_URL_2,
    OLD_DL_BASE_URL_3,
)

hashids = Hashids(salt=HASH_SALT)


def gen_video_link(old_video_url):
    return (
        old_video_url.replace(OLD_DL_BASE_URL_1, NEW_DL_BASE_URL)
        .replace(OLD_DL_BASE_URL_2, NEW_DL_BASE_URL)
        .replace(OLD_DL_BASE_URL_3, NEW_DL_BASE_URL_3)
    )


def hide_name(name):
    words = name.split()
    hidden_words = []
    for word in words:
        if len(word) > 4:
            hidden_word = word[:2] + "***" + word[-2:]
        else:
            hidden_word = word
        hidden_words.append(hidden_word)
    return " ".join(hidden_words)


def decode_string(encoded):
    decoded = "".join([chr(i) for i in hashids.decode(encoded)])
    return decoded


def is_valid_url(url):
    return validators.url(url)


def extract_gdrive_id(gdrive_link):
    if "drive.google.com" not in gdrive_link:
        return None
    match = re.match(
        r"^https://drive\.google\.com/file/d/([a-zA-Z0-9_-]+)/?.*$", gdrive_link
    )
    if match:
        return match.group(1)
    query_params = urllib.parse.parse_qs(urllib.parse.urlparse(gdrive_link).query)
    if "id" in query_params:
        return query_params["id"][0]
    return None
