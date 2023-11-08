import os
import sys

import config
from utils.init import init_test


if __name__ == '__main__':
    init_test()

    action = sys.argv[1]

    if action == 'download':
        
        from actions import download
        performance_root = os.path.join(config.test_bed, 'performance')
        runtime_baseline_root = os.path.join(config.test_bed, config.runtime_baseline_name)
        runtime_target_root = os.path.join(config.test_bed, config.runtime_target_name)
        if len(sys.argv) <= 2:
            download.download_performance(performance_root)
            download.download_runtime(runtime_baseline_root, config.runtime_baseline_tag_number)
            download.download_runtime(runtime_target_root, config.runtime_target_tag_number)
            download.install_tool()
        else:
            repo = sys.argv[2]
            if repo == 'performance': download.download_performance(performance_root)
            elif repo == 'baseline': download.download_runtime(runtime_baseline_root, config.runtime_baseline_tag_number)
            elif repo == 'target': download.download_runtime(runtime_target_root, config.runtime_target_tag_number)
            elif repo == 'crank': download.install_tool()
            else: raise Exception(f'unknown repo: {repo}')

    elif action == 'build':
        import config
        from actions import build

        performance_root = os.path.join(config.test_bed, 'performance')
        runtime_baseline_root = os.path.join(config.test_bed, config.runtime_baseline_name)
        runtime_target_root = os.path.join(config.test_bed, config.runtime_target_name)

        if len(sys.argv) <= 2:
            build.build_runtime(runtime_baseline_root, config.vcvars64_activation_path)
            build.build_runtime(runtime_target_root, config.vcvars64_activation_path)
            build.build_Infrastructure(performance_root)
            build.build_GCPerfSim(performance_root)
            build.build_Microbenchmarks(performance_root)
        else:
            repo = sys.argv[2]
            if repo == 'performance': 
                build.build_Infrastructure(performance_root)
                build.build_GCPerfSim(performance_root)
                build.build_Microbenchmarks(performance_root)
            elif repo == 'baseline': build.build_runtime(runtime_baseline_root, config.vcvars64_activation_path)
            elif repo == 'target': build.build_runtime(runtime_target_root, config.vcvars64_activation_path)
            else: raise Exception(f'unknown repo: {repo}')
    elif action == 'test':
        from actions import compare
        
        configuration_folder = os.path.join(config.test_bed, 'Configurations')
        comparison_name = f'{config.runtime_target_name}_vs_{config.runtime_baseline_name}'
        output_folder = os.path.join(config.test_bed, 'Outputs', comparison_name)
        performance_root = os.path.join(config.test_bed, 'performance')
        runtime_baseline_root = os.path.join(config.test_bed, config.runtime_baseline_name)
        runtime_target_root = os.path.join(config.test_bed, config.runtime_target_name)

        compare.generate_configuration(configuration_folder, 
                                       output_folder,performance_root, runtime_baseline_root, runtime_target_root)
        compare.run_comparison(performance_root, configuration_folder)
    elif action == 'clean':
        from actions import clean
        clean.remove_dotnet_temp()
    else:
        raise Exception(f'unknown action: {action}')