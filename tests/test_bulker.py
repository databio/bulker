import os
import subprocess
import yacman
from bulker.bulker import DEFAULT_CONFIG_FILEPATH

def capture(command):
    proc = subprocess.Popen(command,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
    )
    out,err = proc.communicate()
    return out, err, proc.returncode


def test_yacman():

	bc = yacman.YacAttMap(filepath=DEFAULT_CONFIG_FILEPATH)
	bc
	bc.bulker.default_crate_folder

	out, err, exitcode = capture([os.path.expandvars("$HOME/.local/bin/bulker"), "load", "demo"])
	assert exitcode == 0
	out, err, exitcode = capture([os.path.expandvars("$HOME/.local/bin/bulker"), "load", "bogusbogus"])
	assert exitcode == 1

	# manifest = yacman.YacAttMap(filepath="/home/ns5bc/code/bulker/demo/demo_manifest.yaml")
	# bc
	 