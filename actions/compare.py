import os
import yaml

from utils.terminal import run_command_sync


def generate_configuration(
    configuration_folder: os.PathLike,
    output_path: os.PathLike, 
    performance_root: os.PathLike, 
    runtime_baseline_root: os.PathLike, 
    runtime_target_root: os.PathLike):
    print('generate configuration')
    if not os.path.exists(configuration_folder): os.makedirs(configuration_folder)

    GCPerfSim_dll = os.path.join(
        performance_root, 'artifacts', 'bin', 'GCPerfSim',
        'Release', 'net7.0', 'GCPerfSim.dll'
    )
    microbenchmark_path = os.path.join(
        performance_root, 'src', 'benchmarks', 'micro'
    )
    baseline_corerun_bin = os.path.join(
        runtime_baseline_root, 'artifacts', 'tests', 'coreclr',
        'windows.x64.Release', 'Tests', 'Core_Root', 'corerun.exe'
    )
    baseline_source = os.path.join(
        runtime_baseline_root, 'src', 'coreclr', 'gc'
    )
    target_corerun_bin = os.path.join(
        runtime_target_root, 'artifacts', 'tests', 'coreclr',
        'windows.x64.Release', 'Tests', 'Core_Root', 'corerun.exe'
    )
    target_source = os.path.join(
        runtime_target_root, 'src', 'coreclr', 'gc'
    )

    run_yaml_path = os.path.join(
        configuration_folder, 'Run.yaml'
    )
    run_yaml_content = f'''output_path: {output_path}
gcperfsim_path: {GCPerfSim_dll}
microbenchmark_path: {microbenchmark_path}

coreruns:
    baseline: 
      path: {baseline_corerun_bin}
      environment_variables:
          COMPlus_GCName: clrgcexp.dll
    run:
      path: {target_corerun_bin}
      environment_variables:
          COMPlus_GCName: clrgcexp.dll

trace_configuration_type: gc # Choose between: none, gc, verbose, cpu, cpu_managed, threadtime, join.

source_path:
  baseline: {baseline_source}
  run: {target_source}
    '''
    with open(run_yaml_path, 'w+') as fp:
        fp.write(run_yaml_content)


def run_comparison(performance_root: os.PathLike, configuration_folder: os.PathLike):
    print('run gc performance comparison')
    infrastructure_root = os.path.join(
        performance_root, 'artifacts', 'bin', 'GC.Infrastructure','Release', 'net7.0'
    )
    infrastructure_bin = os.path.join(
        infrastructure_root, 'GC.Infrastructure.exe'
    )
    run_yaml_path = os.path.join(
        configuration_folder, 'Run.yaml'
    )

    command = f'{infrastructure_bin} run --configuration {run_yaml_path}'.split(' ')
    run_command_sync(command, cwd=infrastructure_root)


def generate_gcperfsim_configuration(
    configuration_path: os.PathLike,
    output_root: os.PathLike,
    loops: int,
    scenario: str):
    print('generate gcperfsim configuration')
    if not os.path.exists(output_root): os.makedirs(output_root)

    new_configuration_root = os.path.join(output_root, 'configuration')
    if not os.path.exists(new_configuration_root): os.makedirs(new_configuration_root)

    new_result_root = os.path.join(output_root, 'result')
    if not os.path.exists(new_result_root): os.makedirs(new_result_root)

    with open(configuration_path, 'r') as f:
        config_yaml = yaml.load(f, yaml.Loader)
        for run_name in config_yaml['runs'].keys():
            if run_name != scenario: config_yaml['runs'].pop(run_name)

        configuration_base_name, ext_name = os.path.splitext(os.path.basename(configuration_path))
        for loop in range(loops):
            new_configuration_path = os.path.join(
                new_configuration_root,
                f'{configuration_base_name}_{scenario}_{loop+1}{ext_name}'
            )
            new_result_path = os.path.join(new_result_root, f'{configuration_base_name}_{scenario}_{loop+1}')
            with open(new_configuration_path, 'w+') as f:
                config_yaml['output']['path'] = new_result_path
                yaml.dump(config_yaml, f, default_flow_style=False)


def compare_gcperfsim(
    performance_root: os.PathLike,
    output_root: os.PathLike,
    loops: int):
    print(f'run gcperfsim {loops} times')
    
    infrastructure_root = os.path.join(
        performance_root, 'artifacts', 'bin', 'GC.Infrastructure','Release', 'net7.0'
    )
    infrastructure_bin = os.path.join(
        infrastructure_root, 'GC.Infrastructure.exe'
    )

    new_configuration_root = os.path.join(output_root, 'configuration')
    for idx, gcperfsim_configuration_name in enumerate(os.listdir(new_configuration_root)):
        print(f'loop {idx+1}')
        new_configuration_path = os.path.join(new_configuration_root, gcperfsim_configuration_name)
    
        command = f'{infrastructure_bin} gcperfsim --configuration {new_configuration_path}'.split(' ')
        run_command_sync(command, cwd=infrastructure_root)


def compare_microbenchmarks(times: int=10):
    pass