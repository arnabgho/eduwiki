__author__ = 'moonkey'

import wikipedia
import util.str_util


def get_wikipage(search_term, auto_suggest=True):
    """
    The search term from user may not directly corresponds to a wikipedia page,
    due to vagueness. There are 2 alternatives, "redirect" or "disambiguous".
    :param search_term:
    :param auto_suggest:let Wikipedia find a valid page title for the query
    :return:
    """
    page = wikipedia.page(util.str_util.normal_str(search_term), auto_suggest=auto_suggest)
    return page