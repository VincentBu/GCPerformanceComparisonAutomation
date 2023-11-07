import os
import sys
import configparser

import config
from utils.sysinfo import get_rid


def load_config(config_file_path: os.PathLike) -> None:
    '''load config from conf file

    :param config_file_path: abs path of config file
    :return: None
    '''
    conf = configparser.ConfigParser()
    conf.read(config_file_path)
    
    config.rid = get_rid()

    config.test_bed = conf['Test']['testbed']
    
    config.vcvars64_activation_path = conf['Build']['vcvars64']

    config.runtime_baseline_name = conf['Runtime']['baselineName']
    config.runtime_baseline_tag_number = conf['Runtime']['baselineCommit']
    config.runtime_target_name = conf['Runtime']['targetName']
    config.runtime_target_tag_number = conf['Runtime']['targetCommit']


def init_test() -> None:
    config_file_path = os.path.join(
        os.path.dirname(
            os.path.abspath(
                sys.argv[0]
            )
        ),
        'run.conf'
    )
    load_config(config_file_path)
    if not os.path.exists(config.test_bed): os.makedirs(config.test_bed)
    