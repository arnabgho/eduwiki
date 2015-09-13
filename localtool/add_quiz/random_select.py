import random


def random_selection(name, original_count, select_count=10, negatives=[]):
    print 'quiz name', name
    shuffled = range(1, original_count + 1)
    for n in negatives:
        shuffled.remove(n)
    random.shuffle(shuffled)
    selected = shuffled[:select_count]
    selected = sorted(selected)
    print 'selected:', selected
    with open('./select_result/' + name + '.txt', 'w') as quiz_select_file:
        quiz_select_file.write(str(selected) + '\n')
        quiz_select_file.write('Negatives:' + '\n')
        quiz_select_file.write(str(negatives))
    return selected


if __name__ == "__main__":
    print "Random Selection"
    # random_selection(
    # 'Vietnam War', 30,
    #     negatives=[13, 14, 15, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29])
    random_selection('Earthquake1', 8, select_count=int(10 * 8 / float(25)))
    random_selection('Earthquake2', 11, select_count=int(10 * 11 / float(25)))
    random_selection(
        'Earthquake3', 6,
        select_count=10-int(10 * 8 / float(25))-int(10 * 11 / float(25)))