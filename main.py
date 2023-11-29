import os
import argparse

import config
from utils.init import init_test


if __name__ == '__main__':
    init_test()
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='action')

    parser_download = subparsers.add_parser('download')
    parser_download.add_argument(
        '-r',
        '--repo', 
        dest='download_repo',
        choices=['performance', 'baseline', 'target', 'crank']
    )

    parser_build = subparsers.add_parser('build')
    parser_build.add_argument(
        '-r',
        '--repo', 
        dest='build_repo',
        choices=['performance', 'baseline', 'target']
    )

    parser_test = subparsers.add_parser('test')
    parser_build.add_argument(
        '-n',
        '--name', 
        dest='test_name',
        choices=['gcperfsim', 'microbenchmark', 'aspnet']
    )
    parser_build.add_argument(
        '-s',
        '--scenario', 
        dest='scenario',
        type=str
    )

    parser_build.add_argument(
        '-l',
        '--loops', 
        dest='loops',
        type=int
    )

    args = parser.parse_args()
    
    action = args.action

    match action:
        case 'download':
            from actions import download
            performance_root = os.path.join(config.test_bed, 'performance')
            runtime_baseline_root = os.path.join(config.test_bed, config.runtime_baseline_name)
            runtime_target_root = os.path.join(config.test_bed, config.runtime_target_name)
            repo = args.download_repo
            match repo:
                case 'performance': download.download_performance(performance_root)
                case 'baseline': download.download_runtime(runtime_baseline_root, config.runtime_baseline_tag_number)
                case 'target': download.download_runtime(runtime_target_root, config.runtime_target_tag_number)
                case 'crank': download.install_tool()
                case None: 
                    download.download_performance(performance_root)
                    download.download_runtime(runtime_baseline_root, config.runtime_baseline_tag_number)
                    download.download_runtime(runtime_target_root, config.runtime_target_tag_number)
                    download.install_tool()

        case 'build':
            import config
            from actions import build

            performance_root = os.path.join(config.test_bed, 'performance')
            runtime_baseline_root = os.path.join(config.test_bed, config.runtime_baseline_name)
            runtime_target_root = os.path.join(config.test_bed, config.runtime_target_name)

            repo = args.build_repo
            
            match repo:
                case 'performance': 
                    build.build_Infrastructure(performance_root)
                    build.build_GCPerfSim(performance_root)
                    build.build_Microbenchmarks(performance_root)
                case 'baseline': build.build_runtime(runtime_baseline_root, config.vcvars64_activation_path)
                case 'target': build.build_runtime(runtime_target_root, config.vcvars64_activation_path)
                case None:
                    build.build_runtime(runtime_baseline_root, config.vcvars64_activation_path)
                    build.build_runtime(runtime_target_root, config.vcvars64_activation_path)
                    build.build_Infrastructure(performance_root)
                    build.build_GCPerfSim(performance_root)
                    build.build_Microbenchmarks(performance_root)

        case 'test':
            from actions import compare
            
            configuration_folder = os.path.join(config.test_bed, 'Configurations')
            comparison_name = f'{config.runtime_target_name}_vs_{config.runtime_baseline_name}'
            output_folder = os.path.join(config.test_bed, 'Outputs', comparison_name)
            performance_root = os.path.join(config.test_bed, 'performance')
            runtime_baseline_root = os.path.join(config.test_bed, config.runtime_baseline_name)
            runtime_target_root = os.path.join(config.test_bed, config.runtime_target_name)

            test_name = args.test_name
            match test_name:
                case 'gcperfsim':
                    test_name = args.test_name
                    loops = args.loops
                    scenario =args.scenario

                    gcperfsim_configuration_path = os.path.join(
                        config.test_bed, 
                        'Outputs', 
                        comparison_name, 
                        'Suites',
                        'GCPerfSim',
                        'LowVolatilityRun.yaml')
                    
                    gcperfsim_output_root = os.path.join(
                        config.test_bed, 
                        'Outputs', 
                        comparison_name, 
                        'GCPerfSim',
                        f'GCPerfSim_{scenario}')
                    compare.generate_gcperfsim_configuration(
                        gcperfsim_configuration_path,
                        gcperfsim_output_root,
                        loops,
                        scenario
                    )
                    compare.compare_gcperfsim(
                        performance_root,
                        gcperfsim_output_root,
                        loops
                    )
                case None:
                    compare.generate_configuration(configuration_folder, 
                                                output_folder,performance_root, runtime_baseline_root, runtime_target_root)
                    compare.run_comparison(performance_root, configuration_folder)

        case 'clean':
            from actions import clean
            clean.remove_dotnet_temp()

        case _: Exception(f'unknown action: {action}')