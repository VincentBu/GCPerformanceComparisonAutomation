import os
import json
from io import StringIO

import pandas as pd
import markdown
from markdown.extensions.tables import TableExtension


TABLE_TITLE_LIST = [
    'Large Regressions', 'Large Improvements', 
    'Regressions', 'Improvements', 
    'Stale Regressions', 'Stale Improvements'
]

def extract_tables_and_tiltes_from_markdown(markdown_file_path: os.PathLike):
    # Read the markdown file
    with open(markdown_file_path, 'r', encoding='utf-8') as file:
        markdown_text = file.read()

    # Convert markdown to HTML
    tables_html = markdown.markdown(markdown_text, extensions=[TableExtension()])

    # Extract tables using Pandas
    tables = dict()
    for title, table in zip(TABLE_TITLE_LIST, pd.read_html(StringIO(tables_html))[-len(TABLE_TITLE_LIST):]):
        tables[title] = json.loads(table.to_json(orient='records'))

    return tables


def summarize_gcperfsim_result(output_root: os.PathLike):
    large_regressions_sum = dict()
    large_improvements_sum = dict()
    regressions_sum = dict()
    improvements_sum = dict()

    result_root = os.path.join(output_root, 'result')
    for dirname in os.listdir(result_root):
        result_dir = os.path.join(result_root, dirname)
        result_markdown_path = os.path.join(result_dir, 'Results.md')
        tables = extract_tables_and_tiltes_from_markdown(result_markdown_path)

        # summarize 'Large Regressions'
        large_regressions_test_name_list = map(
            lambda test: test['Metric'],
            tables['Large Regressions']
        )
        for large_regressions_test_name in large_regressions_test_name_list:
            if large_regressions_test_name not in large_regressions_sum.keys():
                large_regressions_sum[large_regressions_test_name] = 1
            else:
                large_regressions_sum[large_regressions_test_name] += 1

        # summarize 'Large Improvements'
        large_improvements_test_name_list = map(
            lambda test: test['Metric'],
            tables['Large Improvements']
        )
        for large_improvements_test_name in large_improvements_test_name_list:
            if large_improvements_test_name not in large_improvements_sum.keys():
                large_improvements_sum[large_improvements_test_name] = 1
            else:
                large_improvements_sum[large_improvements_test_name] += 1
        
        # summarize 'Regressions'
        regressions_test_name_list = map(
            lambda test: test['Metric'],
            tables['Regressions']
        )
        for regressions_test_name in regressions_test_name_list:
            if regressions_test_name not in regressions_sum.keys():
                regressions_sum[regressions_test_name] = 1
            else:
                regressions_sum[regressions_test_name] += 1

        # summarize 'Improvements'
        improvements_test_name_list = map(
            lambda test: test['Metric'],
            tables['Improvements']
        )
        for improvements_test_name in improvements_test_name_list:
            if improvements_test_name not in improvements_sum.keys():
                improvements_sum[improvements_test_name] = 1
            else:
                improvements_sum[improvements_test_name] += 1

    summarize_root = os.path.join(output_root, 'summarize')
    if not os.path.exists(summarize_root): os.makedirs(summarize_root)

    large_regressions_result_path = os.path.join(summarize_root, 'LargeRegressions.json')
    if None in large_regressions_sum.keys(): large_regressions_sum.pop(None)
    with open(large_regressions_result_path, 'w+') as fp:
        json.dump(large_regressions_sum, fp)

    large_improvements_result_path = os.path.join(summarize_root, 'LargeImprovements.json')
    if None in large_improvements_sum.keys(): large_improvements_sum.pop(None)
    with open(large_improvements_result_path, 'w+') as fp:
        json.dump(large_improvements_sum, fp)

    regressions_result_path = os.path.join(summarize_root, 'Regressions.json')
    if None in regressions_sum.keys(): regressions_sum.pop(None)
    with open(regressions_result_path, 'w+') as fp:
        json.dump(regressions_sum, fp)

    improvements_result_path = os.path.join(summarize_root, 'Improvements.json')
    if None in improvements_sum.keys(): improvements_sum.pop(None)
    with open(improvements_result_path, 'w+') as fp:
        json.dump(improvements_sum, fp)