import os 

from utils.git import git_clone, git_checkout
from utils.terminal import run_command_sync

def download_runtime(runtime_root: os.PathLike, commit_number: str) -> None:
    '''clone dotnet/runtime to testbed

    :return: None
    '''
    assert not os.path.exists(runtime_root)
    print(f'clone runtime from github')
    git_clone('dotnet', 'runtime', runtime_root)
    git_checkout(runtime_root, commit_number)


def download_performance(performance_root: os.PathLike) -> None:
    '''clone dotnet/runtime to testbed

    :return: None
    '''
    assert not os.path.exists(performance_root)
    print(f'clone performance from github')
    git_clone('dotnet', 'performance', performance_root)


def install_tool() -> None:
    command = 'dotnet tool install Microsoft.Crank.Controller --version "0.2.0-*" --global'.split(' ')
    run_command_sync(command)
