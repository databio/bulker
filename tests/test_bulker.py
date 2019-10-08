import os
import subprocess
import pytest

import yacman
from bulker.bulker import DEFAULT_CONFIG_FILEPATH
from bulker.bulker import bulker_init, bulker_load, load_remote_registry_path
from bulker.bulker import mkabs
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

    del data


def test_bulker_init():
    try:
        os.remove("test_bulker_init.yaml")
        shutil.rmtree('templates')
    except:
        pass
    bulker_init("test_bulker_init.yaml", DEFAULT_CONFIG_FILEPATH, "docker")
    bulker_config = yacman.YacAttMap(filepath=DEFAULT_CONFIG_FILEPATH)

    manifest, cratevars = load_remote_registry_path(bulker_config, 
                                                     "demo",
                                                     None)


    # del bulker_config

    try:
        os.remove("test_bulker_init.yaml")
        shutil.rmtree('templates')
    except:
        pass



def test_nonconfig_load():
    bulker_config = yacman.YacAttMap(filepath=DEFAULT_CONFIG_FILEPATH)
    # The 'load' command will write the new crate to the config file;
    # we don't want it to update the template config file, so make a dummy
    # filepath that we'll delete later.
    DUMMY_CFGFILEPATH = "bulker/templates/tmp.yaml"
    bulker_config._file_path = DUMMY_CFGFILEPATH
    bulker_config.make_writable()
    manifest, cratevars = load_remote_registry_path(bulker_config, "demo", None)
    exe_template = mkabs(bulker_config.bulker.executable_template, os.path.dirname(bulker_config._file_path))
    import jinja2
    with open(exe_template, 'r') as f:
    # with open(DOCKER_TEMPLATE, 'r') as f:
        contents = f.read()
        exe_template_jinja = jinja2.Template(contents)
    bulker_load(manifest, cratevars, bulker_config, exe_template_jinja, force=True)
    bulker_config.unlock()
    del bulker_config
    try:
        os.remove(DUMMY_CFGFILEPATH)
    except:
        pass


# import inspect
# inspect.getsourcelines(yacman.yaml.SafeLoader.construct_pairs)