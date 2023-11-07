from subprocess import Popen, PIPE


def run_command_sync(command: str, **kwargs) -> None:
    '''run command and wait for return
    
    :param command: command to run
    :param kwargs: see Popen kwargs for details
    :return: None
    '''
    if 'shell' in kwargs.keys():
        if all(kwargs['shell'] == True, isinstance(command, str)) \
            or all(kwargs['shell'] == False, isinstance(command, list)):
            print(command)
            p = Popen(command, **kwargs)
            p.communicate()
        else:
            raise(f'command type {type(command)} doesn\'t match with shell parameter.')
    else:
        if isinstance(command, list):
            print(command)
            p = Popen(command, **kwargs)
            p.communicate()
        else:
            raise(f'command type {type(command)} doesn\'t match with shell parameter.')
    

def run_command_async(command: str, **kwargs) -> Popen:
    '''run command but not wait for return
    
    :param command: command to run
    :param kwargs: see Popen kwargs for details
    :return: None
    '''
    if 'shell' in kwargs.keys():
        if all(kwargs['shell'] == True, isinstance(command, str)) \
            or all(kwargs['shell'] == False, isinstance(command, list)):
            print(command)
            return Popen(command, **kwargs)
        else:
            raise(f'command type {type(command)} doesn\'t match with shell parameter.')
    else:
        if isinstance(command, list):
            print(command)
            return Popen(command, **kwargs)
        else:
            raise(f'command type {type(command)} doesn\'t match with shell parameter.')
    