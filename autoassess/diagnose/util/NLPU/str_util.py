__author__ = 'moonkey'

import unicodedata
import urllib


def normal_str(text):
    """
    normalize unicode and return ascii text
    return "ascii" if there is an UnicodeEncodeError
    """
    # return str(text)
    return text
    # try:
    # return unicodedata.normalize('NFKD', text).encode('ascii')
    # except UnicodeEncodeError as u:
    #     return text.decode('utf-8')
    # return "ascii_encoding_error" + str(u)