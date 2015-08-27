from autoassess.diagnose.util.NLPU import str_util
from autoassess.diagnose.util.NLPU.preprocess import ProcessUtil

__author__ = 'moonkey'

import wikipedia
from wikimongo_model import *
import wikitextparser as wtp
from collections import defaultdict
import random
from sys import maxint
import sys


class WikipediaWrapper:
    def __init__(self):
        pass

    @staticmethod
    def search(query, results=1, suggestion=True):
        return wikipedia.search(query, results=results, suggestion=suggestion)

    @staticmethod
    def page(title=None, pageid=None, auto_suggest=True, redirect=True):
        """
        The search term from user may not corresponds to a wikipedia page,
        due to vagueness. There are 2 alternatives, "redirect"/ "disambiguous".
        :param auto_suggest:let Wikipedia find a valid page title for the query
        :return:
        """
        if pageid is not None:
            pageid = int(pageid)
            page = WikipediaArticle.objects(pageid=pageid)
        else:
            page = WikipediaArticle.objects(title=title)
            if not page:
                results, suggestion = WikipediaWrapper.search(
                    title,
                    results=1,
                    suggestion=True)
                suggested_term = suggestion or results[0]
                page = WikipediaArticle.objects(title=suggested_term)

        if page:
            page = page[0]
        else:
            try:
                page = wikipedia.page(title=title,
                                      pageid=pageid,
                                      auto_suggest=auto_suggest,
                                      redirect=redirect)
            except UnicodeDecodeError:
                page = wikipedia.page(title=str_util.normal_str(title),
                                      pageid=pageid,
                                      auto_suggest=auto_suggest,
                                      redirect=redirect)
        if type(page) is wikipedia.WikipediaPage:
            page = WikipediaWrapper.save_page(page)
        return page

    @staticmethod
    def linked_terms(wikipage):
        """
        :param num: the number of linked texts to return
        :return: list(str), the first few texts that have a wikipedia link
        """

        if type(wikipage) is WikipediaArticle:
            for link in wikipage.wikilinks:
                yield link.target

        elif type(wikipage) is wikipedia.WikipediaPage:
            w_text = wikipage.wikitext
            wikilink_rx = re.compile(r'\[\[([^|\]]*\|)?([^\]]+)\]\]')

            for m in wikilink_rx.finditer(w_text):
                if m.group(1) is not None:
                    if "Image" in m.group(1) \
                            or "Template" in m.group(1) \
                            or "File" in m.group(1):
                        continue
                    link = m.group(1)[:-1]
                    yield link
                else:
                    if "Image" in m.group(2) \
                            or "Template" in m.group(2) \
                            or "File" in m.group(2):
                        continue
                    link = m.group(2)
                    yield link

    @staticmethod
    def save_page(wikipage):
        wt_parsed = wtp.parse(wikipage.wikitext)
        categories = []

        # ### parse categories from wikilinks
        cat_link_started = False  # the category links may not be the last few
        for link in reversed(wt_parsed.wikilinks):
            if link.target.startswith("Category:"):
                cat_link_started = True
                categories.append(link.target.replace("Category:", ""))
            else:
                if cat_link_started:
                    break
        # ###

        new_article = WikipediaArticle(
            title=wikipage.title,
            pageid=int(wikipage.pageid),

            wikitext=wikipage.wikitext,
            content=wikipage.content,
            summary=wikipage.summary,

            categories=categories,
            wikilinks=[WikiLink(target=l.target, text=l.text) for l in
                       wt_parsed.wikilinks],

            # sections=wt_parsed.sections,
        )
        new_article.save()
        return new_article

    @staticmethod
    def article_sentences(wikipage):
        sentences = []
        # if type(wikipage) is wikipedia.WikipediaPage:
        # content = wikipage.content
        nlutil = ProcessUtil()
        # sentences = nlutil.sent_tokenize(content)
        if type(wikipage) is not WikipediaArticle:
            pass
        else:
            for section_idx, section in enumerate(wikipage.sections):
                # make sure same content will not be visited repeatedly
                if section_idx != 0:
                    last_section_level = wikipage.sections[
                        section_idx - 1].level
                    if last_section_level < section.level:
                        continue

                if is_content_sections(section.title):
                    paragraphs = section.contents.split("\n")

                    former_unfinished_para = ""
                    for para_idx, para in enumerate(paragraphs):
                        para = para.strip()
                        if para == '':
                            continue
                        if para.startswith("=="):
                            continue  # skip this paragraph

                        # if para.endswith(",") or para.endswith(":") or \
                        # para.endswith(';') or para[-1].isalnum():
                        # missing equations will cause sentences to be broken
                        # also lists will be separated.
                        # TODO:: BTW, how would the list be tokenized?
                        if not para.endswith("."):
                            former_unfinished_para += para
                            continue
                        else:
                            para = former_unfinished_para + para
                            former_unfinished_para = ""

                        para_sentences = nlutil.sent_tokenize(para)
                        sentences += para_sentences
                        for sent in para_sentences:
                            yield sent
                            # return sentences

    @staticmethod
    def pages_from_category(category):
        category = category.replace(" ", "_")
        cat_links = WikiCategorylinks.objects(cl_to=category, cl_type='page')
        page_ids = [l.cl_from for l in cat_links]
        return page_ids

    @staticmethod
    def page_title_from_id(page_id):
        try:
            page_id_doc = WikiPageId.objects(id=int(page_id))[0]
            page_title = page_id_doc.page_title
        except Exception as e:
            try:
                page = WikipediaWrapper.page(pageid=page_id)
                page_title = page.title
            except Exception as e:
                print "Cannot retrieve title for page id:", page_id
                print e
                page_title = None
                return page_title
        page_title = page_title.replace("_", " ")
        # page_title = page_title.replace(u"\u2013", " ")
        # page_title = page_title.replace("-", " ")

        return page_title

    @staticmethod
    def page_ids_links_here(page_title):
        try:
            page_title = page_title.replace(" ", "_")
            pagelink_objs = Pagelinks.objects(to=page_title)
            pl_from_list = []
            if pagelink_objs:
                pl_from_list = [obj.pl_from for obj in pagelink_objs]
                # for obj in pagelink_objs:
                #     pl_from = obj.pl_from
                #     pl_from_list.append(pl_from)
            else:
                raise ValueError("No Pagelinks found for" + page_title)
            return pl_from_list
        except Exception as e:
            print >> sys.stderr, e
            return None


def filter_wikilink(topic, ignore_cat=False):
    if not topic:
        return None

    if topic.startswith("wikt") or topic.startswith("wikitionary"):
        return None
    elif topic.startswith("File:") or topic.startswith("Image:"):
        return None
    elif "(disambiguation)" in topic:
        return None
    elif '#' in topic:
        # for links containing section like
        # "Euclidean group#Direct_and_indirect_isometries"
        # TODO:: find the exact section of the page
        topic = topic[0:topic.find('#')]
        if not topic:
            return None

    if ignore_cat and topic.startswith("Category:"):
        return None

    # sometimes the wikilink is not properly capitalized
    # NOTE there is a risk ignored here: the true title might not be capitalized
    # which is rare.
    topic = topic[0].capitalize()+topic[1:]
    return topic


def is_content_sections(section_name):
    if section_name == '':  # for the first section
        return True

    section_name = section_name.lower()
    uninformative_sections = [
        'references', 'see also', 'external links']  # , 'notes']

    for us in uninformative_sections:
        if us in section_name or section_name in us:
            return False
    return True


def page_ids_of_same_category(wikipage, max_num=maxint, cat_count=False):
    cat_page_lists = []
    for cat in wikipage.categories:
        cat_page_list = WikipediaWrapper.pages_from_category(cat)

        # remove the wikipage itself
        if wikipage.pageid in cat_page_list:
            cat_page_list.remove(wikipage.pageid)
        cat_page_lists.append(cat_page_list)

    # merge lists and rank the pages by shared category count
    page_list = [item for sublist in cat_page_lists for item in sublist]
    counted_pages = count_rank(page_list)

    if len(counted_pages) <= max_num:
        if cat_count:
            return [p for p in counted_pages]
        else:
            return [p[0] for p in counted_pages]

    # first pick out pages with more shared categories
    result = []
    for p_c in counted_pages:
        page = p_c[0]
        count = p_c[1]
        if count > 1:
            if cat_count:
                result.append(p_c)
            else:
                result.append(page)
        else:
            break

        if len(result) >= max_num:
            return result

    one_count_pages = counted_pages[len(result):]
    rest_len = min(max_num - len(result), len(one_count_pages))
    random_one_count_pages = random.sample(one_count_pages, rest_len)
    if cat_count:
        result += random_one_count_pages
    else:
        result += [p[0] for p in random_one_count_pages]

    return result


def page_titles_of_same_category(wikipage, max_num=maxint, cat_count=False):
    page_ids = page_ids_of_same_category(
        wikipage, max_num, cat_count)
    page_titles = [WikipediaWrapper.page_title_from_id(pid)
                   for pid in page_ids]
    page_titles = [p for p in page_titles if p is not None]

    # in case the page title is not successfully retrieved, like the pageid is
    # no longer there.
    return page_titles


def count_rank(xs):
    counts = defaultdict(int)
    for x in xs:
        counts[x] += 1
    sorted_xs = sorted(counts.items(), reverse=True, key=lambda tup: tup[1])
    return sorted_xs


def test_wiki_util():
    page = WikipediaWrapper.page(title="Reinforcement learning")

    for cat in page.categories:
        print cat, WikipediaWrapper.pages_from_category(cat)


def remove_article(title):
    page = WikipediaWrapper.page(title=title)
    page.delete()


if __name__ == '__main__':
    from mongoengine import connect

    connect('eduwiki_db', host='localhost')
    test_wiki_util()