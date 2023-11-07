import os

from utils.terminal import run_command_sync, run_command_async, PIPE


def build_runtime(runtime_root: os.PathLike, vcvars64_activation_path: os.PathLike):
    print('build runtime')

    script_engine = 'cmd.exe'
    command = [script_engine, '/k', vcvars64_activation_path]
    p = run_command_async(
        command, 
        stdin=PIPE,
        cwd=runtime_root
    )
    p.stdin.write(b'build.cmd -s clr+libs -c Release\n')
    p.stdin.write(b'src\\tests\\build.cmd generatelayoutonly Release\n')
    p.communicate()


def build_infrastructure(performance_root: os.PathLike):
    print('build Infrastructure')

    command = 'dotnet build -c Release'.split(' ')
    infrastructure_root = os.path.join(
        performance_root, 'src', 'benchmarks', 'gc', 
        'GC.Infrastructure', 'GC.Infrastructure'
    )
    run_command_sync(command, cwd=infrastructure_root)
    assert os.path.exists(
        os.path.join(
            performance_root, 'artifacts', 'bin', 'GC.Infrastructure',
            'Release', 'net7.0', 'GC.Infrastructure.exe'
        )
    )


def build_GCPerfSim(performance_root: os.PathLike):
    print('build Infrastructure')

    command = 'dotnet build -c Release'.split(' ')
    gcperfsim_root = os.path.join(
        performance_root, 'src', 'benchmarks', 'gc', 'GCPerfSim'
    )
    run_command_sync(command, cwd=gcperfsim_root)
    assert os.path.exists(
        os.path.join(
            performance_root, 'artifacts', 'bin', 'GCPerfSim',
            'Release', 'net7.0', 'GCPerfSim.dll'
        )
    )


def build_Microbenchmarks(performance_root: os.PathLike):
    print('build Infrastructure')

    command = 'dotnet build -c Release'.split(' ')
    microbenchmarks_root = os.path.join(
        performance_root, 'src', 'benchmarks', 'micro'
    )
    run_command_sync(command, cwd=microbenchmarks_root)
    assert os.path.exists(
        os.path.join(
            performance_root, 'artifacts', 'bin', 'MicroBenchmarks',
            'Release', 'net8.0', 'MicroBenchmarks.dll'
        )
    )