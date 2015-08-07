from distractor_source import similar_page_titles_of_samecat
from autoassess.diagnose.util.wikipedia_util import WikipediaWrapper


def generate_item_distractors(topic, noun_form=None, max_num=3):
    distractors = []

    wikipage = WikipediaWrapper.page(title=topic)
    for p_title in similar_page_titles_of_samecat(wikipage):
        distractor = p_title

        #TODO:: match the form here
        if noun_form:
            # noun_form = "singular" or "plural"
            pass

        if distractor:
            distractors.append(distractor)
            if len(distractors) >= max_num:
                break

    return distractors