# Changelog

## [0.3.0] -- Unreleased
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
