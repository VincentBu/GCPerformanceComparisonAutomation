import os
import argparse

import config
from utils.init import init_test


if __name__ == '__main__':
    init_test()
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='action')

    parser_analyze = subparsers.add_parser('analyze')
    parser_analyze.add_argument(
        '-n',
        '--name', 
        dest='test_name',
        choices=['gcperfsim', 'microbenchmarks', 'aspnetbenchmark']
    )
    parser_analyze.add_argument(
        '-d',
        '--directory', 
        dest='output_root',
        type=str
    )

    args = parser.parse_args()
    
    action = args.action

    match action:
        case 'analyze':
            from actions import analysis
            test_name = args.test_name
            output_root = args.output_root
            if test_name == 'gcperfsim':
                analysis.summarize_gcperfsim_result(output_root)

            if test_name == 'microbenchmarks':
                analysis.summarize_microbenchmarks_result(output_root)

        case 'clean':
            from actions import clean
            clean.remove_dotnet_temp()

        case _: Exception(f'unknown action: {action}')