import os

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
    infrastructure_root = os.path.join(
        performance_root, 'artifacts', 'bin', 'GC.Infrastructure','Release', 'net7.0'
    )

    run_yaml_path = os.path.join(
        configuration_folder, 'Run.yaml'
    )

    command = f'GC.Infrastructure.exe run --configuration {run_yaml_path}'.split(' ')
    run_command_sync(command, cwd=infrastructure_root)