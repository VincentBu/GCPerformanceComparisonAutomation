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

                for metric_result in gcperfsim_result_tables[gcperfsim_run][diff_level].values:
                    metric = metric_result[0]
                    if metric not in result_sum[gcperfsim_run][diff_level].keys():
                        result_sum[gcperfsim_run][diff_level][metric] = dict()
                        result_sum[gcperfsim_run][diff_level][metric]['Title'] = \
                            gcperfsim_result_tables[gcperfsim_run][diff_level].columns.tolist()
                        result_sum[gcperfsim_run][diff_level][metric]['Values'] = list()
                    
                    result_sum[gcperfsim_run][diff_level][metric]['Values'].append(metric_result.tolist())
                    

    summarize_root = os.path.join(output_root, 'summarize')
    if not os.path.exists(summarize_root):
        os.makedirs(summarize_root)

    for gcperfsim_run in gcperfsim_run_list:
        summarize_path = os.path.join(summarize_root, f'{gcperfsim_run}.md')
        summarize_table_string_lines = list()
        
        for diff_level in result_sum[gcperfsim_run].keys():
            summarize_table_string_lines.append(f'# {diff_level}\n')
            summarize_table_string_lines.append(
                f'| Metric | Base | {gcperfsim_run} | \u0394% | \u0394 | Counts |\n')
            summarize_table_string_lines.append(
                f'| :------- | :------- | :------- | :-------: | :-------: | :-------: |\n')
                
            for metric in result_sum[gcperfsim_run][diff_level].keys():
                metric_result = result_sum[gcperfsim_run][diff_level][metric]['Values'][0]
                base = metric_result[1]
                comparand = metric_result[2]
                diff_perc = metric_result[3]
                diff = metric_result[4]
                counts = len(result_sum[gcperfsim_run][diff_level][metric]['Values'])
                summarize_table_string_lines.append(
                    f'| {metric} | {base} | {comparand} | {diff_perc} | {diff} | {counts} |\n')
            
            summarize_table_string_lines.append(f'\n\n')    
        with open(summarize_path, 'w+', encoding='utf-8') as fd:
            fd.writelines(summarize_table_string_lines)    


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
                    result_sum[diff_level][microbenchmark_name] = dict()
                    result_sum[diff_level][microbenchmark_name]['Title'] = [
                        'Benchmark Name',
                        'Baseline',
                        'Comparand',
                        'Baseline Mean Duration (MSec)',
                        'Comparand Mean Duration (MSec)',
                        '\u0394 Mean Duration (MSec)',
                        '\u0394% Mean Duration',
                        'Counts',
                    ]
                    result_sum[diff_level][microbenchmark_name]['Values'] = list()
                    
                result_sum[diff_level][microbenchmark_name]['Values'].append([
                    microbenchmark_name,
                    compare_result['BaselineRunName'],
                    compare_result['ComparandRunName'],
                    compare_result['Baseline']['Statistics']['Mean'],
                    compare_result['Comparand']['Statistics']['Mean'],
                    compare_result['MeanDiff'],
                    compare_result['MeanDiffPerc'],
                ])

    summarize_root = os.path.join(output_root, 'summarize')
    if not os.path.exists(summarize_root):
        os.makedirs(summarize_root)
        
    summarize_table_string_lines = list()
    for diff_level in result_sum.keys():
        summarize_table_string_lines.append(f'# {diff_level}\n')
        summarize_table_string_lines.append(
            f'| Benchmark Name | Baseline | Comparand | Baseline Mean Duration (MSec) | Comparand Mean Duration (MSec) | \u0394 Mean Duration (MSec) | \u0394% Mean Duration | Counts |\n')
        summarize_table_string_lines.append(
            f'| :------- | :------- | :------- | -------: | -------: | -------: | -------: | :------- |\n')
            
        for microbenchmark_name in result_sum[diff_level].keys():
            microbenchmark_result = result_sum[diff_level][microbenchmark_name]['Values'][0]
            baseline_name = microbenchmark_result[1]
            comparand_name = microbenchmark_result[2]
            baseline_mean = '{:.2f}'.format(microbenchmark_result[3])
            comparand_mean = '{:.2f}'.format(microbenchmark_result[4])
            mean_diff = '{:.2f}'.format(microbenchmark_result[5])
            mean_diff_perc = '{:.2f}'.format(microbenchmark_result[6])
            counts = len(result_sum[diff_level][microbenchmark_name]['Values'])
            full_microbenchmark_name = microbenchmark_name.replace('<', '\\<').replace('>', '\\>')
            summarize_table_string_lines.append(
                f'| {full_microbenchmark_name} | {baseline_name} | {comparand_name} | {baseline_mean} | {comparand_mean} | {mean_diff} | {mean_diff_perc} | {counts} |\n')
        
        summarize_table_string_lines.append(f'\n\n')    

    summarize_path = os.path.join(summarize_root, f'result.md')
    with open(summarize_path, 'w+', encoding='utf-8') as fd:
        fd.writelines(summarize_table_string_lines)   
