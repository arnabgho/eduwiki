from distractor_source import similar_page_titles_of_samecat
from autoassess.diagnose.util.wikipedia_util import WikipediaWrapper
from autoassess.diagnose.util.quesgen_util import topic_remove_bracket
import pattern

import sys


def item_distractor_generator(topic, exact_alias):
    if not exact_alias:
        raise ValueError('exact_alias is' + str(exact_alias))

    wikipage = WikipediaWrapper.page(title=topic)
    for p_title in similar_page_titles_of_samecat(wikipage):
        distractor = topic_remove_bracket(p_title)

        # Decapitalization
        if (distractor.istitle() or distractor.isupper()) and ' ' in distractor:
            pass  # do not decapitalize for "Markov Decision Process" or "MDP"
        elif exact_alias[0].isupper():
            distractor = distractor.capitalize()
        else:
            # by default the phrases will not be capitalized
            distractor[0] = distractor[0].lower()

        # noun_form = "singular" or "plural"
        noun_form = get_noun_form(exact_alias)
        if noun_form:
            if noun_form == 'singular':
                distractor = pattern.en.singularize(distractor)
            elif noun_form == 'plural':
                distractor = pattern.en.pluralize(distractor)
            else:
                print >> sys.stderr, "noun_form is not correct:", noun_form

        if distractor:
            yield distractor


def get_noun_form(noun):
    pluralized = pattern.en.pluralize(noun)
    singularized = pattern.en.singularize(noun)
    if singularized == pluralized:
        # heuristically believe with a higher chance it will be
        # the form should be better recognized with full sentence POS-Tagging
        return 'singular'
    if singularized == noun:
        return 'singular'
    if pluralized == noun:
        return 'plural'

    print >> sys.stderr, noun, "is either", singularized, 'nor', pluralized
    return 'singular'  # another heuristic, if none of the form matches.

