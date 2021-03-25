# Changelog

## [0.7.2] -- 2021-03-25
- Update to yacman 0.8.0, fixing references to internal config attributes.
- Add documentation and clarity for the `shell_prompt` option

## [0.7.1] -- 2021-03-03
- Fixed bug in bulker reload.

## [0.7.0] -- 2021-03-02
- EXPERIMENTAL: Added `bulker cwl2man` to create a bulker manifest from a CWL file.
- BREAKING CHANGE: Renamed the `bulker load` arguments: the `--manifest` short arg changed from `-f` to `-m`; `--force` changed from `-r` to `-f`. This is to be more consistent with the names. Since I doubt many people are using this in script, I don't think this will break much, if anything.
- Added new option for `-r`, `--recurse` to `bulker load`, which recursively re-loads all imported manifests.
- Added new `bulker reload` command, that reloads all manifests.
- Added `bulker envvar`, which allows you to list, add (`-a VAR`), or remove (`-r VAR`) environment variables to the bulker config from the CLI.
- Added `bulker unload` to remove a loaded manifest.

## [0.6.0] -- 2020-07-10
- Allowed `bulker run` to gracefully handle interrupts, passing them to the child process.
- Implemented `-p`, which doesn't update prompts, for compatibility with jupyter notebooks
- Fixed a bug with using the default config
- Added capability to exclude volumes from specific containers
- Fixed a bug with singularity exec template
- Dropped support for Python 2

## [0.5.0] -- 2020-04-08
- Added bulker shell prompts for both normal and strict modes
- Added custom shell prompts (experimental!)
- Added `bulker inspect`
- Added env variables $BULKERCRATE, BULKERPROMPT, and BULKERSHELL.
- Changed the behavior of normal mode to set bulker path *after* calling the rcfile.
- Changed built-in singularity template to accommodate singularity version 3
- Changed method for accommodating zshell.
- Removed support for python 3.4

## [0.4.0] -- 2019-12-16
- Better error message if user tries to activate a crate with *no* crates loaded.
- Uses default shell by default, and can be specified with the `shell_path` in config.
- Singularity will now automatically pull new images without requiring `-b` on load
- Added new attributes to disable user or network maps (`no_user` and `no_network`).
- Revamped the templates to fix a few small convenience issues
- Switch to using symlinks instead of wrapper scripts for host executables
- require latest yacman

## [0.3.0] -- 2019-10-21
- Renamed 'dockerargs' to 'docker_args' and 'singularityargs' to
  'singularity_args', which is more consistent with other attribute styles.
- Implemented prototype container entry system, whereby you may type `_command`
  after activating a crate to enter an interactive shell of the container that
  is used to run that command.
- Initial implementation of 'imports' domain capability.
- Added the `tool_args` bulker config section for host-specific *and*
  image-specific settings

## [0.2.4] -- 2019-10-11
- Fixed a bug with file locks that prevented activating environments
- Relative paths for singularity images in the bulker config are now made
  relative to the config file, rather than to the working directory.

## [0.2.3] -- 2019-10-08
- Upgraded yacman to protect against two bulker processes writing to the config
  file at the same time.

## [0.2.2] -- 2019-09-19
- Fixed a bug with using the built-in config file

## [0.2.1] -- 2019-09-12
- Fix problem with python2 compatibility
- Init now copies over templates, which are relative to the config file. This
  makes it easier to share a bulker configuration in a shared computing
  environment.
- update registry to *hub.bulker.io*.

## [0.2.0] -- 2019-08-20
- Major changes to the registry path treatment to accommodate tags
- Local/remote manifests are now loaded with `-f`
- Full registry paths are now required for load, run, and activate
- Config format includes a new hierarchical level for crate tags
- Add `host_commands` functionality (useful for `--strict` crates)

## [0.1.2] -- 2019-08-14
- Fix a bug with compatibility of load from registry for older pythons
  (2.7/3.4).

## [0.1.1] -- 2019-08-13
- Allows `activate` to return the export command, to enable `bulker-activate`
  shell approach (see tips)
- Implements initial bulker registry (file server version)
- Improved argument parsing for `bulker run`

## [0.1.0] -- 2019-08-07
- Add `bulker run` to execute a command in a crate
- `bulker init` will now guess `docker` or `singularity`
- `activate` and `run` commands now accept a comma-separated list of crates

## [0.0.2] -- 2019-08-01
- No longer require `-m` for `bulker load`
- Add support for singularity
- Allow choosing container engine with `bulker init -e`
- Add `-b` option to build/pull containers with `bulker load`

## [0.0.1] -- 2019-08-01
- First public bulker release
