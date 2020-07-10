""" Computing configuration representation """


import argparse
import copy
import jinja2
import logging
import logmuse
import os
import psutil
import sys
import yacman
import signal
import shutil

from distutils.dir_util import copy_tree
from distutils.spawn import find_executable

from ubiquerg import is_url, is_command_callable, parse_registry_path as prp, \
                    query_yes_no


from . import __version__

TEMPLATE_SUBDIR = "templates"
DEFAULT_CONFIG_FILEPATH =  os.path.join(
        os.path.dirname(__file__),
        TEMPLATE_SUBDIR,
        "bulker_config.yaml")

TEMPLATE_ABSPATH = os.path.join(
        os.path.dirname(__file__),
        TEMPLATE_SUBDIR)

DOCKER_EXE_TEMPLATE = "docker_executable.jinja2"
DOCKER_SHELL_TEMPLATE = "docker_shell.jinja2"
DOCKER_BUILD_TEMPLATE = "docker_build.jinja2"

SINGULARITY_EXE_TEMPLATE = "singularity_executable.jinja2"
SINGULARITY_SHELL_TEMPLATE = "singularity_shell.jinja2"
SINGULARITY_BUILD_TEMPLATE = "singularity_build.jinja2"

RCFILE_TEMPLATE = "start.sh"
RCFILE_STRICT_TEMPLATE = "start_strict.sh"

DEFAULT_BASE_URL = "http://hub.bulker.io"

LOCAL_EXE_TEMPLATE = """
#!/bin/sh\n\n{cmd} "$@"
"""

_LOGGER = logging.getLogger(__name__)

PROC = -1

# TODO: move to exceptions file

import abc

#__all__ = ["MissingCrateError"]

class BulkerError(Exception):
    """ Base exception type for this package """
    __metaclass__ = abc.ABCMeta


class MissingCrateError(BulkerError):
    """ Error type for request of an unavailable genome asset. """
    pass



class _VersionInHelpParser(argparse.ArgumentParser):
    def format_help(self):
        """ Add version information to help text. """
        return "version: {}\n".format(__version__) + \
               super(_VersionInHelpParser, self).format_help()


def build_argparser():
    """
    Builds argument parser.

    :return argparse.ArgumentParser
    """

    banner = "%(prog)s - manage containerized executables"
    additional_description = "\nhttps://bulker.databio.org"

    subparser_messages = {
        "init": "Initialize a new bulker config file",
        "inspect": "View name and list of commands for a crate",
        "list": "List available bulker crates",
        "load": "Load a crate from a manifest",
        "activate": "Activate a crate by adding it to PATH",
        "run": "Run a command in a crate"
    }

    parser = _VersionInHelpParser(
            description=banner,
            epilog=additional_description)

    parser.add_argument(
            "-V", "--version",
            action="version",
            version="%(prog)s {v}".format(v=__version__))

    parser.add_argument(
            "--commands",
            action="version",
            version="{}".format(" ".join(subparser_messages.keys())))

    subparsers = parser.add_subparsers(dest="command") 

    def add_subparser(cmd, description):
        return subparsers.add_parser(
            cmd, description=description, help=description)


    sps = {}
    for cmd, desc in subparser_messages.items():
        sps[cmd] = add_subparser(cmd, desc)
        sps[cmd].add_argument(
            "-c", "--config", required=(cmd == "init"),
            help="Bulker configuration file.")

    sps["init"].add_argument(
            "-e", "--engine", choices={"docker", "singularity", }, default=None,
            help="Choose container engine. Default: 'guess'")

    for cmd in ["run", "activate", "load"]:
        sps[cmd].add_argument(
            "crate_registry_paths", metavar="crate-registry-paths", type=str,
            help="One or more comma-separated registry path strings"
            "  that identify crates (e.g. bulker/demo:1.0.0)")

    # optional for inspect
    sps["inspect"].add_argument(
            "crate_registry_paths", metavar="crate-registry-paths", type=str,
            nargs="?", default=os.getenv("BULKERCRATE", ""),
            help="One or more comma-separated registry path strings"
            "  that identify crates (e.g. bulker/demo:1.0.0)")

    for cmd in ["run", "activate"]:
        sps[cmd].add_argument(
            "-s", "--strict", action='store_true', default=False,
            help="Use strict environment (purges PATH of other commands)?")



    sps["load"].add_argument(
            "-f", "--manifest",
            help="File path to manifest. Can be a remote URL or local file.")

    sps["load"].add_argument(
            "-p", "--path",
            help="Destination path for built crate.")

    sps["load"].add_argument(
            "-b", "--build", action='store_true', default=False,
            help="Build/pull the actual containers, in addition to the"
            "executables. Default: False")
    
    sps["load"].add_argument(
            "-r", "--force", action='store_true', default=False,
            help="Force overwrite? Default: False")

    sps["run"].add_argument(
            "cmd", metavar="command", nargs=argparse.REMAINDER, 
            help="Command to run")

    sps["activate"].add_argument(
            "-e", "--echo", action='store_true', default=False,
            help="Echo command instead of running it.")

    sps["activate"].add_argument(
            "-p", "--no-prompt", action='store_false', default=True,
            help="Suppress prompt reset")

    sps["list"].add_argument(
            "-s", "--simple", action='store_true', default=False,
            help="Echo only crate registry paths, not local file paths.")

    return parser



def select_bulker_config(filepath):
    bulkercfg = yacman.select_config(
        filepath,
        "BULKERCFG",
        default_config_filepath=DEFAULT_CONFIG_FILEPATH,
        check_exist=True)
    _LOGGER.debug("Selected bulker config: {}".format(bulkercfg))
    return bulkercfg

# parse_crate_string("abc")
# parse_crate_string("abc:123")
# parse_crate_string("name/abc:123")
# parse_crate_string("http://www.databio.org")

def parse_registry_path(path, default_namespace="bulker"):
    return prp(path, defaults=[
        ("protocol", None),
        ("namespace", default_namespace),
        ("crate", None),
        ("subcrate", None),
        ("tag", "default")])

def parse_registry_path_image(path, default_namespace="docker"):
    return prp(path, defaults=[
        ("protocol", None),
        ("namespace", default_namespace),
        ("image", None),
        ("subimage", None),
        ("tag", "latest")])


def parse_registry_paths(paths, default_namespace="bulker"):
    if "," in paths:
        paths = paths.split(",")
    elif isinstance(paths, str):
        paths = [paths]
    _LOGGER.debug("Split registry paths: {}".format(paths))
    return [parse_registry_path(p, default_namespace) for p in paths]


def _is_writable(folder, check_exist=False, create=False):
    from ubiquerg import is_writable
    return is_writable(folder, check_exist, create)

def bulker_init(config_path, template_config_path, container_engine=None):
    """
    Initialize a config file.
    
    :param str config_path: path to bulker configuration file to 
        create/initialize
    :param str template_config_path: path to bulker configuration file to 
        copy FROM
    """
    if not config_path:
        _LOGGER.error("You must specify a file path to initialize.")
        return

    if not template_config_path:
        _LOGGER.error("You must specify a template config file path.")
        return

    if not container_engine:
        check_engines = ["docker", "singularity"]
        for engine in check_engines:
            if is_command_callable(engine):
                _LOGGER.info("Guessing container engine is {}.".format(engine))
                container_engine = engine
                break  # it's a priority list, stop at the first found engine

    if config_path and not (os.path.exists(config_path) and not query_yes_no("Exists. Overwrite?")):
        # dcc.write(config_path)
        # Init should *also* write the templates.
        dest_folder = os.path.dirname(config_path)
        dest_templates_dir = os.path.join(dest_folder, TEMPLATE_SUBDIR)
        # templates_subdir =  TEMPLATE_SUBDIR
        copy_tree(os.path.dirname(template_config_path), dest_templates_dir)
        new_template = os.path.join(dest_folder, os.path.basename(template_config_path))
        bulker_config = yacman.YacAttMap(filepath=template_config_path, writable=True)
        _LOGGER.debug("Engine used: {}".format(container_engine))
        bulker_config.bulker.container_engine = container_engine
        if bulker_config.bulker.container_engine == "docker":
            bulker_config.bulker.executable_template = os.path.join(TEMPLATE_SUBDIR, DOCKER_EXE_TEMPLATE)
            bulker_config.bulker.shell_template = os.path.join(TEMPLATE_SUBDIR, DOCKER_SHELL_TEMPLATE)
            bulker_config.bulker.build_template = os.path.join(TEMPLATE_SUBDIR, DOCKER_BUILD_TEMPLATE)
        elif bulker_config.bulker.container_engine == "singularity":
            bulker_config.bulker.executable_template = os.path.join(TEMPLATE_SUBDIR, SINGULARITY_EXE_TEMPLATE)
            bulker_config.bulker.shell_template = os.path.join(TEMPLATE_SUBDIR, SINGULARITY_SHELL_TEMPLATE)
            bulker_config.bulker.build_template = os.path.join(TEMPLATE_SUBDIR, SINGULARITY_BUILD_TEMPLATE)
        bulker_config.bulker.rcfile = os.path.join(TEMPLATE_SUBDIR, RCFILE_TEMPLATE)
        bulker_config.bulker.rcfile_strict = os.path.join(TEMPLATE_SUBDIR, RCFILE_STRICT_TEMPLATE)
        bulker_config.write(config_path)
        # copyfile(template_config_path, new_template)
        # os.rename(new_template, config_path)
        _LOGGER.info("Wrote new configuration file: {}".format(config_path))
    else:
        _LOGGER.warning("Can't initialize, file exists: {} ".format(config_path))

def mkdir(path, exist_ok=True):
    """ Replacement of os.makedirs for python 2/3 compatibility """
    if os.path.exists(path):
        if exist_ok:
            pass
        else:
            raise IOError("Path exists: {}".format(path))
    else:
        os.makedirs(path)

def bulker_inspect(bcfg, manifest, cratevars, crate_path=None, 
                build=False, force=False):


    return x

def bulker_load(manifest, cratevars, bcfg, exe_jinja2_template,
                shell_jinja2_template, crate_path=None, 
                build=False, force=False):
    manifest_name = cratevars['crate']
    # We store them in folder: namespace/crate/version
    if not crate_path:
        crate_path = os.path.join(bcfg.bulker.default_crate_folder,
                                  cratevars['namespace'],
                                  manifest_name,
                                  cratevars['tag'])
    if not os.path.isabs(crate_path):
        crate_path = os.path.join(os.path.dirname(bcfg._file_path), crate_path)

    _LOGGER.debug("Crate path: {}".format(crate_path))
    _LOGGER.debug("cratevars: {}".format(cratevars))
    # Update the config file
    if not bcfg.bulker.crates:
        bcfg.bulker.crates = {}
    if not hasattr(bcfg.bulker.crates, cratevars['namespace']):
        bcfg.bulker.crates[cratevars['namespace']] = yacman.YacAttMap({})
    if not hasattr(bcfg.bulker.crates[cratevars['namespace']], cratevars['crate']):
        bcfg.bulker.crates[cratevars['namespace']][cratevars['crate']] = yacman.YacAttMap({})
    if hasattr(bcfg.bulker.crates[cratevars['namespace']][cratevars['crate']], cratevars['tag']):
        _LOGGER.debug(bcfg.bulker.crates[cratevars['namespace']][cratevars['crate']].to_dict())
        if not (force or query_yes_no("That manifest has already been loaded. Overwrite?")):
            return
        else:
            bcfg.bulker.crates[cratevars['namespace']][cratevars['crate']][str(cratevars['tag'])] = crate_path
            _LOGGER.warning("Removing all executables in: {}".format(crate_path))
            try:
                shutil.rmtree(crate_path)
            except:
                _LOGGER.error("Error removing crate at {}. Did your crate path change? Remove it manually.".format(crate_path))
    else:
        bcfg.bulker.crates[cratevars['namespace']][cratevars['crate']][str(cratevars['tag'])] = crate_path


    # Now make the crate

    # First add any imports

    mkdir(crate_path, exist_ok=True)
    if hasattr(manifest.manifest, "imports") and manifest.manifest.imports:
        for imp in manifest.manifest.imports:
            imp_cratevars = parse_registry_path(imp)
            imp_crate_path = os.path.join(bcfg.bulker.default_crate_folder,
                                  imp_cratevars['namespace'],
                                  imp_cratevars['crate'],
                                  imp_cratevars['tag'])
            if not os.path.isabs(imp_crate_path):
                imp_crate_path = os.path.join(os.path.dirname(bcfg._file_path), imp_crate_path)            
            if not os.path.exists(imp_crate_path):
                _LOGGER.error("Can't import crate '{}' from '{}'".format(imp, imp_crate_path))
                # Recursively load any non-existant imported crates.
                imp_manifest, imp_cratevars = load_remote_registry_path(bcfg, 
                                                        imp, None)
                _LOGGER.debug(imp_manifest)
                _LOGGER.debug(imp_cratevars)
                bulker_load(imp_manifest, imp_cratevars, bcfg, exe_jinja2_template,
                shell_jinja2_template, crate_path=None, build=build, force=force)
            _LOGGER.info("Importing crate '{}' from '{}'.".format(imp, imp_crate_path))
            copy_tree(imp_crate_path, crate_path)

    # should put this in a function
    def host_tool_specific_args(bcfg, pkg, hosttool_arg_key):
        _LOGGER.debug("Arg key: '{}'".format(hosttool_arg_key))
        # Here we're parsing the *image*, not the crate registry path.
        imvars = parse_registry_path_image(pkg['docker_image'])
        _LOGGER.debug(imvars)
        try:
            amap = bcfg.bulker.tool_args[imvars['namespace']][imvars['image']]
            if imvars['tag'] != 'default' and hasattr(amap, imvars['tag']):
                string = amap[imvars['tag']][hosttool_arg_key]
            else:
                string = amap.default[hosttool_arg_key]
            _LOGGER.debug(string)
            return string
        except:
            _LOGGER.debug("No host/tool args found.")
            return ""

    cmdlist = []
    cmd_count = 0
    if hasattr(manifest.manifest, "commands") and manifest.manifest.commands:
        for pkg in manifest.manifest.commands:
            _LOGGER.debug(pkg)
            pkg.update(bcfg.bulker) # Add terms from the bulker config
            pkg = copy.deepcopy(yacman.YacAttMap(pkg))  # (otherwise it's just a dict)
            # We have to deepcopy it so that changes we make to pkg aren't reflected in bcfg.

            if pkg.container_engine == "singularity" and "singularity_image_folder" in pkg:
                pkg["singularity_image"] = os.path.basename(pkg["docker_image"])
                pkg["namespace"] = os.path.dirname(pkg["docker_image"])

                if os.path.isabs(pkg["singularity_image_folder"]):
                    sif = pkg["singularity_image_folder"]
                else:
                    sif = os.path.join(os.path.dirname(bcfg._file_path),
                                       pkg["singularity_image_folder"])

                pkg["singularity_fullpath"] = os.path.join(
                                                sif,
                                                pkg["namespace"],
                                                pkg["singularity_image"])

                mkdir(os.path.dirname(pkg["singularity_fullpath"]), exist_ok=True)
            command = pkg["command"]
            path = os.path.join(crate_path, command)
            _LOGGER.debug("Writing {cmd}".format(cmd=path))
            cmdlist.append(command)

            # Add any host-specific tool-specific args
            hosttool_arg_key = "{engine}_args".format(engine=bcfg.bulker.container_engine)
            hts = host_tool_specific_args(bcfg, pkg, hosttool_arg_key)
            _LOGGER.debug("Adding host-tool args: {}".format(hts))
            if hasattr(pkg, hosttool_arg_key):
                pkg[hosttool_arg_key] += " " + hts
            else:
                pkg[hosttool_arg_key] = hts
                

            # Remove any excluded volumes from the package
            exclude_vols = host_tool_specific_args(bcfg, pkg, "exclude_volumes")
            _LOGGER.debug("Volume list: {}".format(pkg["volumes"]))
            _LOGGER.debug("pkg: {}".format(pkg))
            if len(exclude_vols) > 0:
                for item in exclude_vols:
                    _LOGGER.debug("Excluding volume: '{}'".format(item))
                    try:
                        pkg["volumes"].remove(item)
                    except:
                        pass
                _LOGGER.debug("Volume list: {}".format(pkg["volumes"]))
            else:
                _LOGGER.debug("No excluded volumes")


            with open(path, "w") as fh:
                fh.write(exe_jinja2_template.render(pkg=pkg))
                os.chmod(path, 0o755)

            # shell commands
            path_shell = os.path.join(crate_path, "_" + command)
            _LOGGER.debug("Writing shell command: '{cmd}'".format(cmd=path_shell))
            with open(path_shell, "w") as fh:
                fh.write(shell_jinja2_template.render(pkg=pkg))
                os.chmod(path_shell, 0o755)            

            if build:
                buildscript = build.render(pkg=pkg)
                x = os.system(buildscript)
                if x != 0:
                    _LOGGER.error("------ Error building. Build script used: ------")
                    _LOGGER.error(buildscript)
                    _LOGGER.error("------------------------------------------------")
                _LOGGER.info("Container available at: {cmd}".format(cmd=pkg["singularity_fullpath"]))

    # host commands
    host_cmdlist = []
    if hasattr(manifest.manifest, "host_commands") and manifest.manifest.host_commands:
        _LOGGER.info("Populating host commands")
        for cmd in manifest.manifest.host_commands:
            _LOGGER.debug(cmd)
            if not is_command_callable(cmd):
                _LOGGER.warning("Requested host command is not callable and "
                "therefore not created: '{}'".format(cmd))
                continue
            local_exe = find_executable(cmd)
            path = os.path.join(crate_path, cmd)
            host_cmdlist.append(cmd)
            os.symlink(local_exe, path)

            # The old way: TODO: REMOVE THIS
            if False:
                populated_template = LOCAL_EXE_TEMPLATE.format(cmd=local_exe)
                with open(path, "w") as fh:
                    fh.write(populated_template)
                    os.chmod(path, 0o755)

    cmd_count = len(cmdlist)
    host_cmd_count = len(host_cmdlist)
    if cmd_count < 1 and host_cmd_count < 1:
        _LOGGER.error("No commands provided. Crate not created.")
        os.rmdir(crate_path)
        crate_path_parent = os.path.dirname(crate_path)
        if not os.listdir(crate_path_parent):
            os.rmdir(crate_path_parent)
        sys.exit(1)

    rp = "{namespace}/{crate}:{tag}".format(
        namespace=cratevars['namespace'],
        crate=cratevars['crate'],
        tag=cratevars['tag'])

    _LOGGER.info("Loading manifest: '{rp}'."
                " Activate with 'bulker activate {rp}'.".format(rp=rp))
    if cmd_count > 0:
        _LOGGER.info("Commands available: {}".format(", ".join(cmdlist)))
    if host_cmd_count > 0:
        _LOGGER.info("Host commands available: {}".format(", ".join(host_cmdlist)))



    bcfg.write()

def bulker_activate(bulker_config, cratelist, echo=False, strict=False, prompt=True):
    """
    Activates a given crate.

    :param yacman.YacAttMap bulker_config: The bulker configuration object.
    :param list cratelist: a list of cratevars objects, which are dicts with
        values for 'namespace', 'crate', and 'tag'.
    :param bool echo: Should we just echo the new PATH to create? Otherwise, the
        function will create a new shell and replace the current process with
        it.
    :param bool strict: Should we wipe out the PATH, such that the returned
        environment contains strictly only commands listed in the bulker
        manifests?
    """
    # activating is as simple as adding a crate folder to the PATH env var.

    new_env = os.environ


    if hasattr(bulker_config.bulker, "shell_path"):
        shellpath = os.path.expandvars(bulker_config.bulker.shell_path)
    else:
        shellpath = os.path.expandvars("$SHELL")

    if not is_command_callable(shellpath):
        bashpath = "/bin/bash"
        _LOGGER.warning("Specified shell is not callable: '{}'. Using {}.".format(shellpath, bashpath))
        shell_list = [bashpath, bashpath]


    if hasattr(bulker_config.bulker, "shell_rc"):
        shell_rc = os.path.expandvars(bulker_config.bulker.shell_rc)
    else:
        if os.path.basename(shellpath) == "bash":
            shell_rc = "$HOME/.bashrc"
        elif os.path.basename(shellpath) == "zsh":
            shell_rc = "$HOME/.zshrc"
        else:
            _LOGGER.warning("No shell RC specified shell")

    if os.path.basename(shellpath) == "bash":
        shell_list = [shellpath, shellpath, "--noprofile"]
    elif os.path.basename(shellpath) == "zsh":
        shell_list = [shellpath, shellpath]
    else:
        bashpath = "/bin/bash"
        _LOGGER.warning("Shell must be bash or zsh. Specified shell was: '{}'. Using {}.".format(shellpath, bashpath))
        shell_list = [bashpath, bashpath, "--noprofile"]

           
    newpath = get_new_PATH(bulker_config, cratelist, strict)

    # We can use lots of them. use the last one
    name = "{namespace}/{crate}".format(
        namespace=cratelist[-1]["namespace"],
        crate=cratelist[-1]["crate"])


    _LOGGER.debug("Newpath: {}".format(newpath))


    if hasattr(bulker_config.bulker, "shell_prompt"):
        ps1 = bulker_config.bulker.shell_prompt
    else:
        if os.path.basename(shellpath) == "bash":
            ps1 = "\\u@\\b:\\w\\a\\$ "
            # With color:
            ps1 = "\\[\\033[01;93m\\]\\b|\\[\\033[00m\\]\\[\\033[01;34m\\]\\w\\[\\033[00m\\]\\$ "
        elif os.path.basename(shellpath) == "zsh":
            ps1 = "%F{226}%b|%f%F{blue}%~%f %# "
        else:
            _LOGGER.warning("No built-in custom prompt for shells other than bash or zsh")        
    
    # \b is our bulker-specific code that we populate with the crate
    # registry path
    ps1 = ps1.replace("\\b", name)  # for bash
    ps1 = ps1.replace("%b", name)  # for zsh
    _LOGGER.debug(ps1)

    if echo:
        print("export BULKERCRATE=\"{}\"".format(name))
        print("export BULKERPATH=\"{}\"".format(newpath))
        print("export BULKERSHELLRC=\"{}\"".format(shell_rc))
        if prompt:
            print("export BULKERPROMPT=\"{}\"".format(ps1))
            print("export PS1=\"{}\"".format(ps1))
        print("export PATH={}".format(newpath))
        return
    else:
        _LOGGER.debug("Shell list: {}". format(shell_list))

        new_env["BULKERCRATE"] = name
        new_env["BULKERPATH"] = newpath
        if prompt:
            new_env["BULKERPROMPT"] = ps1

        new_env["BULKERSHELLRC"] = shell_rc

        if strict:
            for k in bulker_config.bulker.envvars:
                new_env[k] = os.environ.get(k, "")
        
        if os.path.basename(shellpath) == "bash":    
            if strict:
                rcfile = mkabs(bulker_config.bulker.rcfile_strict,
                                 os.path.dirname(bulker_config._file_path))
            else:
                rcfile = mkabs(bulker_config.bulker.rcfile,
                             os.path.dirname(bulker_config._file_path))

            shell_list.append("--rcfile")
            shell_list.append(rcfile)
            _LOGGER.debug("rcfile: {}".format(rcfile))
            _LOGGER.debug(shell_list)

        if os.path.basename(shellpath) == "zsh":
            if strict:
                rcfolder = mkabs(os.path.join(
                    os.path.dirname(bulker_config.bulker.rcfile_strict),
                    "zsh_start_strict"), os.path.dirname(bulker_config._file_path))     
            else:
                rcfolder = mkabs(os.path.join(
                    os.path.dirname(bulker_config.bulker.rcfile_strict),
                    "zsh_start"), os.path.dirname(bulker_config._file_path))   

            new_env["ZDOTDIR"] = rcfolder
            _LOGGER.debug("ZDOTDIR: {}".format(new_env["ZDOTDIR"]))

        _LOGGER.debug(new_env)
        #os.execv(shell_list[0], shell_list[1:])
        os.execve(shell_list[0], shell_list[1:], env=new_env)

         # The 'v' means 'pass a variable with a list of args' vs. 'l' which is 
        # a list of separate args.
        # The 'e' means add the 'env' to replace any environment variables

def get_local_path(bulker_config, cratevars):
    """
    :param dict cratevars: dict with crate metadata returned from parse_registry_path
    :param YacAttMap bulker_config: bulker config object
    :return str: path to requested crate folder
    """
    _LOGGER.debug(cratevars)
    _LOGGER.debug(bulker_config.bulker.crates[cratevars["namespace"]][cratevars["crate"]].to_dict())

    return bulker_config.bulker.crates[cratevars["namespace"]][cratevars["crate"]][cratevars["tag"]]

def get_new_PATH(bulker_config, cratelist, strict=False):
    """
    Returns local paths to crates

    :: param str crates :: string with a comma-separated list of crate identifiers
    """
    if not bulker_config.bulker.crates:
        raise MissingCrateError("No crates exist")

    cratepaths = ""
    for cratevars in cratelist:
        cratepaths += get_local_path(bulker_config, cratevars) + os.pathsep
    
    if strict:
        newpath = cratepaths
    else:
        newpath = cratepaths + os.environ["PATH"]

    return newpath

def bulker_run(bulker_config, cratelist, command, strict=False):
    _LOGGER.debug("Running.")
    _LOGGER.debug("{}".format(command))
    newpath = get_new_PATH(bulker_config, cratelist, strict)

    def maybe_quote(item):
        if ' ' in item:
            return "\"{}\"".format(item)
        else:
            return item
    
    quoted_command = [maybe_quote(x) for x in command]
    os.environ["PATH"] = newpath  
    export = "export PATH=\"{}\"".format(newpath)
    merged_command = "{export}; {command}".format(export=export, command=" ".join(quoted_command))
    _LOGGER.debug("{}".format(merged_command))
    # os.system(merged_command)
    # os.execlp(command[0], merged_command)
    import subprocess
    import psutil
    signal.signal(signal.SIGINT, _generic_signal_handler)
    signal.signal(signal.SIGTERM, _generic_signal_handler)    
    # process = subprocess.call(merged_command, shell=True)
    global PROC
    PROC = psutil.Popen(merged_command, shell=True, preexec_fn=os.setsid)
    PROC.communicate()
    #command[0:0] = ["export", "PATH=\"{}\"".format(newpath)]
    #subprocess.call(merged_command)

def _generic_signal_handler(sig, frame):
    """
    Function for handling both SIGTERM and SIGINT
    """

    global PROC
    message = "Interrupt received. Bulker (pid: {}) failing gracefully...".format(PROC.pid)
    _LOGGER.info(message)
    sys.stdout.flush()
    try:
        parent_process = psutil.Process(PROC.pid)
        print("children:", [x for x in parent_process.children(recursive=False)])
        for child_proc in parent_process.children(recursive=False):
            _kill_process(child_proc.pid)
    except psutil.NoSuchProcess:
        print("already dead")
        return    
    _kill_process(PROC.pid)
    PROC.wait(timeout=5)
    sys.stdout.flush()
    
    sys.exit(1)


def _attend_process( proc, sleeptime):
    """
    Waits on a process for a given time to see if it finishes, returns True
    if it's still running after the given time or False as soon as it 
    returns.

    :param psutil.Popen proc: Process object opened by psutil.Popen()
    :param float sleeptime: Time to wait
    :return bool: True if process is still running; otherwise false
    """
    # print("attend:{}".format(proc.pid))
    try:
        proc.wait(timeout=sleeptime)
    except psutil.TimeoutExpired:
        return True
    return False

def _kill_process(pid, sig=signal.SIGINT, proc_name=None):
    """
    Pypiper spawns subprocesses. We need to kill them to exit gracefully,
    in the event of a pipeline termination or interrupt signal.
    By default, child processes are not automatically killed when python
    terminates, so Pypiper must clean these up manually.
    Given a process ID, this function just kills it.

    :param int pid: Process id.
    """

    # When we kill process, it turns into a zombie, and we have to reap it.
    # So we can't just kill it and then let it go; we call wait
    import time

    if pid is None:
        return

    try:
        parent_process = psutil.Process(pid)
        sys.stdout.flush()
        time_waiting = 0
        sleeptime = .25
        still_running = _attend_process(psutil.Process(pid), 0)

        while still_running and time_waiting < 3:
            if time_waiting > 2:
                sig = signal.SIGKILL
            elif time_waiting > 1:
                sig = signal.SIGTERM
            else:
                sig = signal.SIGINT

            _LOGGER.debug("Sending sig {} to proc {}".format(sig, pid))
            parent_process.send_signal(sig)

            # Now see if it's still running
            time_waiting = time_waiting + sleeptime
            if not _attend_process(psutil.Process(pid), sleeptime):
                still_running = False

    except OSError:
        # This would happen if the child process ended between the check
        # and the next kill step
        still_running = False
        time_waiting = time_waiting + sleeptime
        print("proc {} already dead 1".format(pid))
    except psutil.NoSuchProcess:
        still_running = False
        time_waiting = time_waiting + sleeptime
        print("proc {} already dead 1".format(pid))

    if proc_name:
        proc_string = " ({proc_name})".format(proc_name=proc_name)
    else:
        proc_string = " "
 
    if still_running:
        # still running!?
        _LOGGER.warning("Bulker child process {pid}{proc_string} never responded"
            "I just can't take it anymore. I don't know what to do...".format(pid=pid,
                proc_string=proc_string))
    else:
        if time_waiting > 0:
            note = "terminated after {time} sec".format(time=int(time_waiting))
        else:
            note = "was already terminated"

        msg = "Bulker child process {pid}{proc_string} {note}.".format(
            pid=pid, proc_string=proc_string, note=note)
        _LOGGER.info(msg)

def load_remote_registry_path(bulker_config, registry_path, filepath=None):
    cratevars = parse_registry_path(registry_path)
    if cratevars:
        # assemble the query string
        if 'registry_url' in bulker_config.bulker:
            base_url = bulker_config.bulker.registry_url
        else:
            # base_url = "http://big.databio.org/bulker/"
            base_url = DEFAULT_BASE_URL
        query = cratevars["crate"]
        if cratevars["tag"] != "default":
            query = query + "_" + cratevars["tag"]
        if not cratevars["namespace"]:
            cratevars["namespace"] = "bulker"  # default namespace
        query = cratevars["namespace"] + "/" + query
        # Until we have an API:
        query = query + ".yaml"

        if not filepath:
            filepath = os.path.join(base_url, query)
    else: 
        _LOGGER.error("Unable to parse registry path: {}".format(registry_path))
        sys.exit(1)

    if is_url(filepath):
        _LOGGER.debug("Got URL: {}".format(filepath))
        try: #python3
            from urllib.request import urlopen
            from urllib.error import HTTPError
        except: #python2
            from urllib2 import urlopen       
            from urllib2 import URLError as HTTPError
        try:
            response = urlopen(filepath)
        except HTTPError as e:
            if cratevars:
                _LOGGER.error("The requested remote manifest '{}' is not found.".format(
                    filepath))
                sys.exit(1)
            else:
                raise e
        data = response.read()      # a `bytes` object
        text = data.decode('utf-8')
        manifest_lines = yacman.YacAttMap(yamldata=text)
    else:
        manifest_lines = yacman.YacAttMap(filepath=filepath)

    return manifest_lines, cratevars


def mkabs(path, reldir=None):
    """
    Makes sure a path is absolute; if not already absolute, it's made absolute
    relative to a given directory. Also expands ~ and environment variables for
    kicks.

    :param str path: Path to make absolute
    :param str reldir: Relative directory to make path absolute from if it's
        not already absolute

    :return str: Absolute path
    """
    def xpand(path):
        return os.path.expandvars(os.path.expanduser(path))

    if os.path.isabs(xpand(path)):
        return xpand(path)

    if not reldir:
        return os.path.abspath(xpand(path))

    return os.path.join(xpand(reldir), xpand(path))


def main():
    """ Primary workflow """

    parser = logmuse.add_logging_options(build_argparser())
    args, remaining_args = parser.parse_known_args()
    logger_kwargs = {"level": args.verbosity, "devmode": args.logdev}
    logmuse.init_logger(name="yacman", **logger_kwargs)
    global _LOGGER
    _LOGGER = logmuse.logger_via_cli(args)

    _LOGGER.debug("Command given: {}".format(args.command))

    if not args.command:
        parser.print_help()
        _LOGGER.error("No command given")
        sys.exit(1)

    if args.command == "init":
        bulkercfg = args.config
        _LOGGER.debug("Initializing bulker configuration")
        _is_writable(os.path.dirname(bulkercfg), check_exist=False)
        bulker_init(bulkercfg, DEFAULT_CONFIG_FILEPATH, args.engine)
        sys.exit(0)      

    bulkercfg = select_bulker_config(args.config)
    bulker_config = yacman.YacAttMap(filepath=bulkercfg, writable=False)


    if args.command == "list":
        # Output header via logger and content via print so the user can
        # redirect the list from stdout if desired without the header as clutter

        if args.simple:
            fmt = "{namespace}/{crate}:{tag}"
        else:
            _LOGGER.info("Available crates:")
            fmt = "{namespace}/{crate}:{tag} -- {path}"

        if bulker_config.bulker.crates:
            for namespace, crates in bulker_config.bulker.crates.items():
                for crate, tags in crates.items():
                    for tag, path in tags.items():
                        print(fmt.format(namespace=namespace, crate=crate, 
                                         tag=tag, path=path))
        else:
            _LOGGER.info("No crates available. Use 'bulker load' to load a crate.")
        sys.exit(1)

    # For all remaining commands we need a crate identifier

    _LOGGER.info("Bulker config: {}".format(bulkercfg))
    if args.command == "activate":
        try:
            cratelist = parse_registry_paths(args.crate_registry_paths,
                                             bulker_config.bulker.default_namespace)
            _LOGGER.debug(cratelist)
            _LOGGER.info("Activating bulker crate: {}{}".format(args.crate_registry_paths, " (Strict)" if args.strict else ""))
            bulker_activate(bulker_config, cratelist, echo=args.echo, strict=args.strict, prompt=args.no_prompt)
        except KeyError as e:
            parser.print_help(sys.stderr)
            _LOGGER.error("{} is not an available crate".format(e))
            sys.exit(1)
        except MissingCrateError as e:
            _LOGGER.error("Missing crate: {}".format(e))
            sys.exit(1)
        except AttributeError as e:
            _LOGGER.error("Your bulker config file is outdated, you need to re-initialize it: {}".format(e))
            sys.exit(1)

    if args.command == "run":
        try:
            cratelist = parse_registry_paths(args.crate_registry_paths)
            _LOGGER.info("Activating crate: {}\n".format(args.crate_registry_paths))
            bulker_run(bulker_config, cratelist, args.cmd, strict=args.strict)
        except KeyError as e:
            parser.print_help(sys.stderr)
            _LOGGER.error("{} is not an available crate".format(e))
            sys.exit(1)
        except MissingCrateError as e:
            _LOGGER.error("Missing crate: {}".format(e))
            sys.exit(1)        

    if args.command == "load":
        bulker_config.make_writable()
        manifest, cratevars = load_remote_registry_path(bulker_config, 
                                                        args.crate_registry_paths,
                                                        args.manifest)
        exe_template_jinja = None
        build_template_jinja = None
        shell_template_jinja = None

        exe_template = mkabs(bulker_config.bulker.executable_template,
                             os.path.dirname(bulker_config._file_path))
        build_template = mkabs(bulker_config.bulker.build_template, 
                               os.path.dirname(bulker_config._file_path))        
        try:
            shell_template = mkabs(bulker_config.bulker.shell_template,
                             os.path.dirname(bulker_config._file_path))        
        except AttributeError:
            _LOGGER.error("You need to re-initialize your bulker config or add a 'shell_template' attribute.")
            sys.exit(1)


        try:
            assert(os.path.exists(exe_template))
        except AssertionError:
            _LOGGER.error("Bulker config points to a missing executable template: {}".format(exe_template))
            sys.exit(1)

        with open(exe_template, 'r') as f:
        # with open(DOCKER_TEMPLATE, 'r') as f:
            contents = f.read()
            exe_template_jinja = jinja2.Template(contents)

        try:
            assert(os.path.exists(shell_template))
        except AssertionError:
            _LOGGER.error("Bulker config points to a missing shell template: {}".format(shell_template))
            sys.exit(1)

        with open(shell_template, 'r') as f:
        # with open(DOCKER_TEMPLATE, 'r') as f:
            contents = f.read()
            shell_template_jinja = jinja2.Template(contents)




        if args.build:
            try:
                assert(os.path.exists(build_template))
            except AssertionError:
                _LOGGER.error("Bulker config points to a missing build template: {}".format(build_template))
                sys.exit(1)

            _LOGGER.info("Building images with template: {}".format(build_template))
            with open(build_template, 'r') as f:
                contents = f.read()
                build_template_jinja = jinja2.Template(contents)

        bulker_load(manifest, cratevars, bulker_config, 
                    exe_jinja2_template=exe_template_jinja, 
                    shell_jinja2_template=shell_template_jinja, 
                    crate_path=args.path,
                    build=build_template_jinja,
                    force=args.force)

    if args.command == "inspect":
        if args.crate_registry_paths == "":
            _LOGGER.error("No active create. Inspect requires a provided crate, or a currently active create.")
            sys.exit(1)
        manifest, cratevars = load_remote_registry_path(bulker_config, 
                                                    args.crate_registry_paths,
                                                    None)
        manifest_name = cratevars['crate']

        
        print("Bulker manifest: {}".format(args.crate_registry_paths))
        crate_path = os.path.join(bulker_config.bulker.default_crate_folder,
                                  cratevars['namespace'],
                                  manifest_name,
                                  cratevars['tag'])
        if not os.path.isabs(crate_path):
            crate_path = os.path.join(os.path.dirname(bcfg._file_path), crate_path)
        print("Crate path: {}".format(crate_path))
        import glob
        filenames = glob.glob(os.path.join(crate_path, "*"))
        available_commands = [x for x in [os.path.basename(x) for x in filenames] if x[0] != "_"]
        print("Available commands: {}".format(available_commands))

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        _LOGGER.error("Program canceled by user!")
        sys.exit(1)