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

from ubiquerg import is_url

import yacman
from collections import OrderedDict
from . import __version__

DEFAULT_CONFIG_FILEPATH =  os.path.join(
        os.path.dirname(__file__),
        "templates",
        "bulker_config.yaml")

DOCKER_TEMPLATE =  os.path.join(
        os.path.dirname(__file__),
        "templates",
        "docker_executable.jinja2")

_LOGGER = logging.getLogger(__name__)

def select_bulker_config(filepath):
    bulkercfg = yacman.select_config(
        filepath,
        COMPUTE_SETTINGS_VARNAME,
        default_config_filepath=DEFAULT_CONFIG_FILEPATH,
        check_exist=True)
    _LOGGER.debug("Selected divvy config: {}".format(bulkercfg))
    return bulkercfg


class _VersionInHelpParser(argparse.ArgumentParser):
    def format_help(self):
        """ Add version information to help text. """
        return "version: {}\n".format(__version__) + \
               super(_VersionInHelpParser, self).format_help()


def bulker_init(config_path, template_config_path):
    """
    Initialize a config file.
    
    :param str config_path: path to divvy configuration file to 
        create/initialize
    :param str template_config_path: path to divvy configuration file to 
        copy FROM
    """
    if not config_path:
        _LOGGER.error("You must specify a file path to initialize.")
        return

    if not template_config_path:
        _LOGGER.error("You must specify a template config file path.")
        return

    if config_path and not os.path.exists(config_path):
        # dcc.write(config_path)
        # Init should *also* write the templates.
        dest_folder = os.path.dirname(config_path)
        # copy_tree(os.path.dirname(template_config_path), dest_folder)
        new_template = os.path.join(os.path.dirname(config_path), os.path.basename(template_config_path))
        copyfile(template_config_path, new_template)
        os.rename(new_template, config_path)
        _LOGGER.info("Wrote new configuration file: {}".format(config_path))
    else:
        _LOGGER.warning("Can't initialize, file exists: {} ".format(config_path))


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
        "activate": "Activate a bulker crate by adding it to your PATH"
    }

    sps = {}
    for cmd, desc in subparser_messages.items():
        sps[cmd] = add_subparser(cmd, desc)
        sps[cmd].add_argument(
            "-c", "--config", required=(cmd == "init"),
            help="Divvy configuration file.")

    sps["load"].add_argument(
            "-m", "--manifest", required=True,
            help="YAML file with executables to populate a crate.")    

    sps["load"].add_argument(
            "-p", "--path",
            help="Path to crate you will build.")

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

def load(manifest, bulker_config, jinja2_template, crate_path=None):
    manifest_name = manifest.manifest.name
    if not crate_path:
        crate_path = os.path.join(bulker_config.bulker.default_crate_folder, manifest_name)
    os.makedirs(crate_path, exist_ok=True) 
    _LOGGER.info("Loading manifest: '{m}'. Activate with 'bulker activate {m}'.".format(m=manifest_name))
    cmdlist = []
    for pkg in manifest.manifest.commands:
        pkg.update(bulker_config.bulker)
        command = pkg["command"]
        path = os.path.join(crate_path, command)
        _LOGGER.debug("Writing {cmd}".format(cmd=path))
        cmdlist.append(command)
        with open(path, "w") as fh:
            fh.write(jinja2_template.render(pkg=pkg))
            os.chmod(path, 0o755)
    _LOGGER.info("Commands available: {}".format(", ".join(cmdlist)))


    # Update the config file
    bulker_config.bulker.crates[manifest_name] = crate_path
    bulker_config.write()

def activate(bulker_config, crate):
    # activating is as simple as adding a crate folder to the PATH env var.
    newpath = bulker_config.bulker.crates[crate] + os.pathsep + os.environ["PATH"]
    os.environ["PATH"] = newpath
    os.system("bash")

def main():
    """ Primary workflow """

    parser = logmuse.add_logging_options(build_argparser())
    args, remaining_args = parser.parse_known_args()
    logger_kwargs = {"level": args.verbosity, "devmode": args.logdev}
    logmuse.init_logger(name="yacman", **logger_kwargs)
    global _LOGGER
    _LOGGER = logmuse.logger_via_cli(args)

    if not args.command:
        parser.print_help()
        _LOGGER.error("No command given")
        sys.exit(1)

    if args.command == "init":
        bulkercfg = args.config
        _LOGGER.debug("Initializing divvy configuration")
        _is_writable(os.path.dirname(bulkercfg), check_exist=False)
        bulker_init(bulkercfg, DEFAULT_CONFIG_FILEPATH)
        sys.exit(0)      

    bulkercfg = select_bulker_config(args.config)
    _LOGGER.info("Bulker config: {}".format(bulkercfg))
    bulker_config = yacman.YacAttMap(filepath=bulkercfg)

    if args.command == "list":
        # Output header via logger and content via print so the user can
        # redirect the list from stdout if desired without the header as clutter
        _LOGGER.info("Available crates:")
        for crate, path in bulker_config.bulker.crates.items():
            print("{}: {}".format(crate, path))
        sys.exit(1)

    if args.command == "activate":
        try:
            _LOGGER.info("Activating crate: {}\n".format(args.crate))
            activate(bulker_config, args.crate)
        except KeyError:
            parser.print_help(sys.stderr)
            _LOGGER.error("{} is not an available crate".format(args.crate))
            sys.exit(1)

    if args.command == "load":
        j2t = None
        with open(DOCKER_TEMPLATE, 'r') as f:
            contents = f.read()
            j2t = jinja2.Template(contents)

        if is_url(args.manifest):
            _LOGGER.info("Got URL.")
            import urllib.request
            response = urllib.request.urlopen(args.manifest)
            data = response.read()      # a `bytes` object
            text = data.decode('utf-8')
            manifest = yacman.YacAttMap(yamldata=text)
        else:
            manifest = yacman.YacAttMap(filepath=args.manifest)
        load(manifest, bulker_config, j2t, args.path)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        _LOGGER.error("Program canceled by user!")
        sys.exit(1)