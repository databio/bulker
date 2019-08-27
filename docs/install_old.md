# Installing bulker

Install from [GitHub releases](https://github.com/databio/bulker/releases) or from PyPI using `pip`:

- `pip install --user bulker`: install into user space.
- `pip install --user --upgrade bulker`: update in user space.
- `pip install bulker`: install into an active virtual environment.
- `pip install --upgrade bulker`: update in virtual environment.

See if your install worked by calling `bulker -h` on the command line. If the `bulker` executable in not in your `$PATH`, append this to your `.bashrc` or `.profile` (or `.bash_profile` on macOS):

```{console}
export PATH=~/.local/bin:$PATH
```

# Initializing bulker

On a fresh install, bulker comes comes with a locally installed config file, which you can explore by typing `bulker list`. If you want a group-shared bulker config, or if you want to change the volumes, environment variables, or container engine, you will need to configure bulker. Start by initializing an empty bulker config file:

```{console}
export BULKERCFG="bulker_config.yaml"
bulker init -c $BULKERCFG
```

### Docker vs singularity 

This `init` command will create a default config file. The `init` command will guess if your system is set up to use docker or singularity. You can use `-e ENGINE` to force one or the other (where `ENGINE` is `singularity` or `docker`).

The `bulker activate`, `load`, and `list` commands require knowing where this genome config file is. You can pass it on the command line all the time (using the -c parameter), but this gets old. An alternative is to set up the $BULKERCFG environment variable. Bulker will automatically use the config file in this environmental variable if it exists. Add this line to your `.bashrc` or `.profile` if you want it to persist for future command-line sessions:

```{console}
export BULKERCFG=/path/to/bulker_config.yaml
```

 You can always specify `-c` if you want to override the value in the $BULKERCFG variable on an ad-hoc basis:

# Configuring bulker

The bulker config file is where you put the container settings that will determine how your executables behave. Take a look at the config file to see what you can modify:

```console
cat $BULKERCFG
```

Returns:

```yaml
bulker:
  volumes: ['/tmp']
  envvars: ['DISPLAY']
  default_crate_folder: ${HOME}/bulker_crates
  singularity_image_folder: ${HOME}/simages
  container_engine: docker
  default_namespace: bulker
  executable_template: null
  build_template: null
  crates: null
```

Here, you can add any file systems under `volumes` that you need mounted on your containers. You should add any environment variables that your containers may need under `envvars`. The `default_crate_folder` will determine where the crates (folders with executables) are saved. The `crates` section is maintained by bulker -- it will add a new entry into this section whenever you run `bulker load`, and this is what it reads when you request `bulker list` or `bulker activate`.

