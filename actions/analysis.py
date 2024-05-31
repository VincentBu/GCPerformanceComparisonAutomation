import os
import json
from io import StringIO

import pandas as pd
import numpy as np
import markdown
from markdown.extensions.tables import TableExtension


gcperfsim_run_list = [
    'normal', 
    'soh_pinning',
    'poh',
    'loh'
]


diff_level_list = [
    'LargeRegressions',
    'Regressions',
    'StaleRegressions',
    'StaleImprovements',
    'Improvements',
    'LargeImprovements'
]


def difference_level(n: np.float64):
    if isinstance(n, str):
        if n == '∞':
            return 'LargeRegressions'
        if n == '-∞':
            return 'LargeImprovements'
    n = float(n)
    if n > 20:
        return 'LargeRegressions'
    if 20 >= n >=5:
        return 'Regressions'
    if 5 > n >=0:
        return 'StaleRegressions'
    
    if -5 < n <= 0:
        return 'StaleImprovements'
    if -20 <= n <= -5:
        return 'Improvements'
    if n <= -20:
        return 'LargeImprovements'


def extract_tables_from_markdown(markdown_file_path: os.PathLike):
    # Read the markdown file
    with open(markdown_file_path, 'r', encoding='utf-8') as file:
        markdown_text = file.read()

    # Convert markdown to HTML
    tables_html = markdown.markdown(markdown_text, extensions=[TableExtension()])

    # Extract tables using Pandas
    tables = pd.read_html(StringIO(tables_html))
    
    return tables


def get_gcperfsim_result_table(tables: list[pd.DataFrame]):
    titled_tables = dict()

    for gcperfsim_run in gcperfsim_run_list:
        titled_tables[gcperfsim_run] = dict()

        for table in tables:
            #  ignore summary table
            if gcperfsim_run not in table.columns:
                continue

            # ignore empty table
            if not isinstance(table.values[0][0], str):
                continue

            delta_percentage = table.values[0][3]
            diff_level = difference_level(delta_percentage)

            titled_tables[gcperfsim_run][diff_level] = table.copy()

    return titled_tables


def summarize_gcperfsim_result(output_root: os.PathLike):
    result_sum = dict()
    result_root = os.path.join(output_root, 'Results')
    for dirname in os.listdir(result_root):
        result_dir = os.path.join(result_root, dirname)
        result_markdown_path = os.path.join(result_dir, 'Results.md')
        result_table_list = extract_tables_from_markdown(result_markdown_path)
        gcperfsim_result_tables = get_gcperfsim_result_table(result_table_list)

        for gcperfsim_run in gcperfsim_run_list:
            if gcperfsim_run not in result_sum.keys():
                result_sum[gcperfsim_run] = dict()
            for diff_level in diff_level_list:
                if diff_level not in result_sum[gcperfsim_run].keys():
                    result_sum[gcperfsim_run][diff_level] = dict()
            
                if diff_level not in gcperfsim_result_tables[gcperfsim_run].keys():
                    continue

                for metric in gcperfsim_result_tables[gcperfsim_run][diff_level]['Metric']:
                    if metric not in result_sum[gcperfsim_run][diff_level].keys():
                        result_sum[gcperfsim_run][diff_level][metric] = 1
                    else:
                        result_sum[gcperfsim_run][diff_level][metric] += 1

    for gcperfsim_run in gcperfsim_run_list:
        summarize_root = os.path.join(output_root, 'summarize')
        if not os.path.exists(summarize_root):
            os.makedirs(summarize_root)

        summarize_path = os.path.join(summarize_root, f'{gcperfsim_run}.json')
        with open(summarize_path, 'w+') as fp:
            json.dump(result_sum[gcperfsim_run], fp)    


def get_microbenchmarks_result_table(tables: list[pd.DataFrame]):
    titled_tables = dict()

    for table in tables:
        #  ignore summary table
        if 'Benchmark Name' not in table.columns:
            continue

        # ignore empty table
        if not isinstance(table.values[0][0], str):
            continue

        delta_percentage = table.values[0][6]
        diff_level = difference_level(delta_percentage)

        titled_tables[diff_level] = table.copy()

    return titled_tables


def summarize_microbenchmarks_result(output_root: os.PathLike):
    result_sum = dict()

    result_root = os.path.join(output_root, 'Results')
    for dirname in os.listdir(result_root):
        result_dir = os.path.join(result_root, dirname)
        result_json_path = os.path.join(result_dir, 'Results.json')
        with open(result_json_path, 'r') as fp:
            result = json.load(fp)[0]

        for diff_level in diff_level_list:
            if diff_level not in result_sum.keys():
                result_sum[diff_level] = dict()

            for compare_result in result[diff_level]:
                microbenchmark_name = compare_result['MicrobenchmarkName']
                if microbenchmark_name not in result_sum[diff_level].keys():
                    result_sum[diff_level][microbenchmark_name] = 1
                else:
                    result_sum[diff_level][microbenchmark_name] += 1

    summarize_root = os.path.join(output_root, 'summarize')
    if not os.path.exists(summarize_root):
        os.makedirs(summarize_root)

    summarize_path = os.path.join(summarize_root, f'result.json')
    with open(summarize_path, 'w+') as fp:
        json.dump(result_sum, fp)  

'''
def summarize_microbenchmarks_result(output_root: os.PathLike):
    result_sum = dict()

    result_root = os.path.join(output_root, 'Results')
    for dirname in os.listdir(result_root):
        result_dir = os.path.join(result_root, dirname)
        result_markdown_path = os.path.join(result_dir, 'Results.md')
        result_table_list = extract_tables_from_markdown(result_markdown_path)
        microbenchmarks_result_tables = get_microbenchmarks_result_table(result_table_list)

        for diff_level in diff_level_list:
            if diff_level not in result_sum.keys():
                result_sum[diff_level] = dict()
            if diff_level not in microbenchmarks_result_tables.keys():
                continue
            for benchmark in microbenchmarks_result_tables[diff_level]['Benchmark Name']:
                if benchmark not in result_sum[diff_level].keys():
                    result_sum[diff_level][benchmark] = 1
                else:
                    result_sum[diff_level][benchmark] += 1

    summarize_root = os.path.join(output_root, 'summarize')
    if not os.path.exists(summarize_root):
        os.makedirs(summarize_root)

    summarize_path = os.path.join(summarize_root, f'result.json')
    with open(summarize_path, 'w+') as fp:
        json.dump(result_sum, fp)    
'''