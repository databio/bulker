""" Computing configuration representation """


import argparse
import jinja2
import logging
import logmuse
import os
import sys
import shutil
import yaml
from yaml import SafeLoader
# from distutils.dir_util import copy_tree
from shutil import copyfile

from ubiquerg import is_url, is_command_callable

import yacman
from collections import OrderedDict
from . import __version__

DEFAULT_CONFIG_FILEPATH =  os.path.join(
        os.path.dirname(__file__),
        "templates",
        "bulker_config.yaml")

TEMPLATE_FOLDER = os.path.join(
        os.path.dirname(__file__),
        "templates")

DOCKER_EXE_TEMPLATE = os.path.join(TEMPLATE_FOLDER, "docker_executable.jinja2")
DOCKER_BUILD_TEMPLATE = os.path.join(TEMPLATE_FOLDER, "docker_build.jinja2")
SINGULARITY_EXE_TEMPLATE =  os.path.join(TEMPLATE_FOLDER, "singularity_executable.jinja2")
SINGULARITY_BUILD_TEMPLATE =  os.path.join(TEMPLATE_FOLDER, "singularity_build.jinja2")

_LOGGER = logging.getLogger(__name__)

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

    parser = _VersionInHelpParser(
            description=banner,
            epilog=additional_description)

    parser.add_argument(
            "-V", "--version",
            action="version",
            version="%(prog)s {v}".format(v=__version__))

    subparsers = parser.add_subparsers(dest="command") 

    def add_subparser(cmd, description):
        return subparsers.add_parser(
            cmd, description=description, help=description)

    subparser_messages = {
        "init": "Initialize a new bulker config file",
        "list": "List available bulker crates",
        "load": "Create a new bulker crate from a container manifest",
        "activate": "Activate a bulker crate by adding it to your PATH",
        "run": "Run a command in a crate"
    }

    sps = {}
    for cmd, desc in subparser_messages.items():
        sps[cmd] = add_subparser(cmd, desc)
        sps[cmd].add_argument(
            "-c", "--config", required=(cmd == "init"),
            help="Bulker configuration file.")

    sps["init"].add_argument(
            "-e", "--engine", choices={"docker", "singularity", }, default=None,
            help="Choose container engine. Default: 'guess'")

    sps["load"].add_argument(
            "manifest",
            help="YAML file with executables to populate a crate.")    

    sps["run"].add_argument(
            "crate",
            help="Choose the crate to activate before running")
    
    sps["run"].add_argument(
            "cmd", metavar="command", nargs='*', 
            help="Command to run")

    sps["load"].add_argument(
            "-p", "--path",
            help="Path to crate you will build.")

    sps["load"].add_argument(
            "-b", "--build", action='store_true', default=False,
            help="Build/pull the actual containers, in addition to the"
            "executables. Default: False")    

    sps["activate"].add_argument(
            "crate",
            help="Crate to activate.")

    return parser


def select_bulker_config(filepath):
    bulkercfg = yacman.select_config(
        filepath,
        "BULKERCFG",
        default_config_filepath=DEFAULT_CONFIG_FILEPATH,
        check_exist=True)
    _LOGGER.debug("Selected bulker config: {}".format(bulkercfg))
    return bulkercfg


def _is_writable(folder, check_exist=False, create=False):
    """
    Make sure a folder is writable.

    Given a folder, check that it exists and is writable. Errors if requested on
    a non-existent folder. Otherwise, make sure the first existing parent folder
    is writable such that this folder could be created.

    :param str folder: Folder to check for writeability.
    :param bool check_exist: Throw an error if it doesn't exist?
    :param bool create: Create the folder if it doesn't exist?
    """
    folder = folder or "."

    if os.path.exists(folder):
        return os.access(folder, os.W_OK) and os.access(folder, os.X_OK)
    elif create_folder:
        os.mkdir(folder)
    elif check_exist:
        raise OSError("Folder not found: {}".format(folder))
    else:
        _LOGGER.debug("Folder not found: {}".format(folder))
        # The folder didn't exist. Recurse up the folder hierarchy to make sure
        # all paths are writable
        return _is_writable(os.path.dirname(folder), strict_exists)


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

    if config_path and not os.path.exists(config_path):
        # dcc.write(config_path)
        # Init should *also* write the templates.
        dest_folder = os.path.dirname(config_path)
        # copy_tree(os.path.dirname(template_config_path), dest_folder)
        new_template = os.path.join(os.path.dirname(config_path), os.path.basename(template_config_path))
        bulker_config = yacman.YacAttMap(filepath=template_config_path)
        _LOGGER.debug("Engine used: {}".format(container_engine))
        bulker_config.bulker.container_engine = container_engine
        bulker_config.write(config_path)
        # copyfile(template_config_path, new_template)
        # os.rename(new_template, config_path)
        _LOGGER.info("Wrote new configuration file: {}".format(config_path))
    else:
        _LOGGER.warning("Can't initialize, file exists: {} ".format(config_path))


def bulker_load(manifest, bulker_config, jinja2_template, crate_path=None, build=False):
    manifest_name = manifest.manifest.name
    if not crate_path:
        crate_path = os.path.join(bulker_config.bulker.default_crate_folder, manifest_name)
    _LOGGER.debug("Crate path: {}".format(crate_path))
    os.makedirs(crate_path, exist_ok=True)
    cmdlist = []
    for pkg in manifest.manifest.commands:
        _LOGGER.debug(pkg)
        pkg = yacman.YacAttMap(pkg)  # (otherwise it's just a dict)
        pkg.update(bulker_config.bulker)
        if "singularity_image_folder" in pkg:
            pkg["singularity_image"] = os.path.basename(pkg["docker_image"])
            pkg["namespace"] = os.path.dirname(pkg["docker_image"])
            pkg["singularity_fullpath"] = os.path.join(pkg["singularity_image_folder"], pkg["namespace"], pkg["singularity_image"])
            os.makedirs(os.path.dirname(pkg["singularity_fullpath"]), exist_ok=True)
        command = pkg["command"]
        path = os.path.join(crate_path, command)
        _LOGGER.debug("Writing {cmd}".format(cmd=path))
        cmdlist.append(command)
        with open(path, "w") as fh:
            fh.write(jinja2_template.render(pkg=pkg))
            os.chmod(path, 0o755)
        if build:
            buildscript = build.render(pkg=pkg)
            x = os.system(buildscript)
            if x != 0:
                _LOGGER.error("------ Error building. Build script used: ------")
                _LOGGER.error(buildscript)
                _LOGGER.error("------------------------------------------------")
            _LOGGER.info("Container available at: {cmd}".format(cmd=pkg["singularity_fullpath"]))

    _LOGGER.info("Loading manifest: '{m}'. Activate with 'bulker activate {m}'.".format(m=manifest_name))
    _LOGGER.info("Commands available: {}".format(", ".join(cmdlist)))


    # Update the config file
    if not bulker_config.bulker.crates:
        bulker_config.bulker.crates = {}
    bulker_config.bulker.crates[manifest_name] = crate_path
    bulker_config.write()

def bulker_activate(bulker_config, crate):
    # activating is as simple as adding a crate folder to the PATH env var.
    newpath = cratepaths(crate, bulker_config)
    os.environ["PATH"] = newpath

    # os.system("bash")
    os.execlp("bash", "bulker")
    os._exit(-1)

def cratepaths(crates, bulker_config):
    if "," in crates:
        crates = crates.split(",")
    elif isinstance(crates, str):
        crates = [crates]
    
    cratepaths = ""
    for crate in crates:
        cratepaths += bulker_config.bulker.crates[crate] + os.pathsep
    newpath = cratepaths + os.pathsep + os.environ["PATH"]
    return newpath

def bulker_run(bulker_config, crate, command):
    _LOGGER.debug("Running.")
    _LOGGER.debug("{}".format(command))
    newpath = cratepaths(crate, bulker_config)
    os.environ["PATH"] = newpath  
    export = "export PATH=\"{}\"".format(newpath)
    merged_command = "{export}; {command}".format(export=export, command=" ".join(command))
    _LOGGER.debug("{}".format(merged_command))
    # os.system(merged_command)
    # os.execlp(command[0], merged_command)
    import subprocess
    subprocess.call(merged_command, shell=True)


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
    _LOGGER.info("Bulker config: {}".format(bulkercfg))
    bulker_config = yacman.YacAttMap(filepath=bulkercfg)
    if bulker_config.bulker.container_engine == "docker":
        bulker_config.bulker.executable_template = DOCKER_EXE_TEMPLATE
        bulker_config.bulker.build_template = DOCKER_BUILD_TEMPLATE
    elif bulker_config.bulker.container_engine == "singularity":
        bulker_config.bulker.executable_template = SINGULARITY_EXE_TEMPLATE
        bulker_config.bulker.build_template = SINGULARITY_BUILD_TEMPLATE

    if args.command == "list":
        # Output header via logger and content via print so the user can
        # redirect the list from stdout if desired without the header as clutter
        _LOGGER.info("Available crates:")
        if bulker_config.bulker.crates:
            for crate, path in bulker_config.bulker.crates.items():
                print("{}: {}".format(crate, path))
        else:
            _LOGGER.info("No crates available. Use 'bulker load' to load a crate.")
        sys.exit(1)

    if args.command == "activate":
        try:
            _LOGGER.info("Activating crate: {}\n".format(args.crate))
            bulker_activate(bulker_config, args.crate)
        except KeyError:
            parser.print_help(sys.stderr)
            _LOGGER.error("{} is not an available crate".format(args.crate))
            sys.exit(1)

    if args.command == "run":
        try:
            _LOGGER.info("Activating crate: {}\n".format(args.crate))
            bulker_run(bulker_config, args.crate, args.cmd)
        except KeyError:
            parser.print_help(sys.stderr)
            _LOGGER.error("{} is not an available crate".format(args.crate))
            sys.exit(1)

    if args.command == "load":
        exe_template_jinja = None
        build_template_jinja = None
        exe_template = os.path.join(TEMPLATE_FOLDER, bulker_config.bulker.executable_template)
        build_template = os.path.join(TEMPLATE_FOLDER, bulker_config.bulker.build_template)
        assert(os.path.exists(exe_template))
        with open(exe_template, 'r') as f:
        # with open(DOCKER_TEMPLATE, 'r') as f:
            contents = f.read()
            exe_template_jinja = jinja2.Template(contents)

        if is_url(args.manifest):
            _LOGGER.info("Got URL.")
            import urllib.request
            response = urllib.request.urlopen(args.manifest)
            data = response.read()      # a `bytes` object
            text = data.decode('utf-8')
            manifest = yacman.YacAttMap(yamldata=text)
        else:
            manifest = yacman.YacAttMap(filepath=args.manifest)
        _LOGGER.info("Executable template: {}".format(exe_template))

        if args.build:
            _LOGGER.info("Building images with template: {}".format(build_template))
            with open(build_template, 'r') as f:
                contents = f.read()
                build_template_jinja = jinja2.Template(contents)

        bulker_load(manifest, bulker_config, exe_template_jinja, args.path, build_template_jinja)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        _LOGGER.error("Program canceled by user!")
        sys.exit(1)