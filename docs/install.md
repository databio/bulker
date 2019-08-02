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

# Initial configuration

On a fresh install, `bulker` comes pre-loaded with some built-in compute packages, which you can explore by typing `bulker list`. If you need to tweak these or create your own packages, you will need to configure bulker manually. Start by initializing an empty `bulker` config file:

```{console}
export DIVCFG="bulker_config.yaml"
bulker init -c $DIVCFG
```

This `init` command will create a default config file, along with a folder of templates. 


The `bulker write` and `list` commands require knowing where this genome config file is. You can pass it on the command line all the time (using the -c parameter), but this gets old. An alternative is to set up the $DIVCFG environment variable. bulker will automatically use the config file in this environmental variable if it exists. Add this line to your `.bashrc` or `.profile` if you want it to persist for future command-line sessions. You can always specify -c if you want to override the value in the $DIVCFG variable on an ad-hoc basis:

```{console}
export DIVCFG=/path/to/bulker_config.yaml
```

More details can be found in the [configuring bulker how-to guide](configuration.md).