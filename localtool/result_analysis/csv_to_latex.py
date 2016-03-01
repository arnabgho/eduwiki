# Source: http://josechristian.com/2013/06/05/csv-to-tex-table-python/
# converts a csv file to a tex table.
from re import sub


def csv_to_tex_table(str_csv_file, str_tex_file=""):
    if not str_tex_file:
        str_tex_file = str_csv_file.replace(".csv", ".tex")

    # read csv file
    with open(str_csv_file, 'r') as file_r_csv:
        str_csv_contents = file_r_csv.read()
    list_csv_rows = str_csv_contents.split('\n')

    # tex document format
    # str_tex_start = '\documentclass{article}\n\\begin{document}\n'
    # str_tex_end = '\end{document}'

    # table format
    # get number of columns
    list_tex_tab_start = [
        '\\begin{table}[t]\n\centering\n\t\\begin{tabular}{'
    ]
    list_row_comps = list_csv_rows[0].split(',')
    for int_col in range(0, len(list_row_comps)):
        list_tex_tab_start.append('c ')
    list_tex_tab_start.append('}\n')
    str_tex_tab_start = ''.join(list_tex_tab_start)

    str_tex_tab_end = '\n\t\\end{tabular}\n\\end{table}\n'

    # change the csv rows to tex rows
    list_tex_rows = []
    for str_csv_row in list_csv_rows:
        if len(str_csv_row) > 1:
            row_array = str_csv_row.split(',')
            for idx, e in enumerate(row_array):
                if '0.' in e:
                    if '*' in e:
                        start_count = e.count('*')
                        row_array[idx] = "${:.3f}$".format(
                            float(e.replace('*', '')))
                        row_array[idx] += '*' * start_count
                    else:
                        row_array[idx] = "${:.3f}$".format(float(e))
            str_tex_row = ' & '.join(row_array)
            # str_tex_row = sub(',', ' & ', str_csv_row.rstrip('\r\n'))
            list_tex_rows.append('\t\t' + str_tex_row + '\t\\\\\n')
    str_tex_rows = ''.join(list_tex_rows)

    # build output
    list_full_tex_output = [
        # str_tex_start,
        str_tex_tab_start,
        str_tex_rows,
        str_tex_tab_end,
        # str_tex_end
    ]

    # create output file
    file_output = open(str_tex_file + '.tex', 'w')
    file_output.write(''.join(list_full_tex_output))
    file_output.close()


if __name__ == "__main__":
    print "IRT Alpha"
    # csv_to_tex_table(
    # str_csv_file='multiple/analysis_result/all_score_correlations.csv')
    # csv_to_tex_table(
    #     str_csv_file='multiple/analysis_result/all_irt_discriminations_d0.csv')
    # csv_to_tex_table(
    # str_csv_file='multiple/analysis_result/all_irt_discriminations_d1.csv')
    csv_to_tex_table(
        str_csv_file='multiple/analysis_result/3run/all_irt_discriminations_all.csv')