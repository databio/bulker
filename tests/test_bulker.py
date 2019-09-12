import os
import subprocess
import pytest

import yacman
from bulker.bulker import DEFAULT_CONFIG_FILEPATH
from bulker.bulker import bulker_init, bulker_load, load_remote_registry_path
import shutil


def test_yacman():

    bc = yacman.YacAttMap(filepath=DEFAULT_CONFIG_FILEPATH)
    bc
    bc.bulker.default_crate_folder

    # Not straightforward to test the CLI directly with pytest: This works on
    # local computer but not on travis; it can't find the executable

    # def capture(command):
    # proc = subprocess.Popen(command,
    #     stdout = subprocess.PIPE,
    #     stderr = subprocess.PIPE,
    # )
    # out,err = proc.communicate()
    # return out, err, proc.returncode


    # out, err, exitcode = capture([os.path.expandvars("$HOME/.local/bin/bulker"), "load", "demo"])
    # assert exitcode == 0
    # out, err, exitcode = capture([os.path.expandvars("$HOME/.local/bin/bulker"), "load", "bogusbogus"])
    # assert exitcode == 1

    # manifest = yacman.YacAttMap(filepath="/home/ns5bc/code/bulker/demo/demo_manifest.yaml")
    # bc

yaml_str = """\
---
one: 1
2: two
"""

def test_float_idx():

    data = yacman.YacAttMap(yamldata=yaml_str)
    # We should be able to access this by string, not by int index.
    assert(data['2'] == "two")
    with pytest.raises(KeyError):
        data[2]



def test_bulker_init():
    try:
        os.remove("test_bulker_init.yaml")
        shutil.rmtree('templates')
    except:
        pass
    bulker_init("test_bulker_init.yaml", DEFAULT_CONFIG_FILEPATH, "docker")
    bulker_config = yacman.YacAttMap(filepath=DEFAULT_CONFIG_FILEPATH)
    bulker_load

    manifest, cratevars = load_remote_registry_path(bulker_config, 
                                                     "demo",
                                                     None)
    try:
        os.remove("test_bulker_init.yaml")
        shutil.rmtree('templates')
    except:
        pass



# import inspect
# inspect.getsourcelines(yacman.yaml.SafeLoader.construct_pairs)