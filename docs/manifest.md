# How to create a manifest

Writing a manifest is really simple...just take a look at these examples. You just write a `yaml` file which includes a `manifest_name` (which is the activation key for `bulker activate MANIFEST_NAME`, and also the default name of the folder where the executables will be saved). Then you add a `commands` section which lists the commands in a few attributes:

1. *command* is the executable name; this is what the user will type in to run the command (*e.g.* `pandoc`).

2. *dockerargs* is any additional arguments required by this tool. You should add `-i` for tools that need to read/write piped output to/from stdin and stdout, and add `-t` for commands like `python` or `R` that allocate a user interface.

3. *docker_image* is the location of the image.

4. *docker_command* is the command that will be executed inside the container. This is often the same as the `command` itself for the user, but it doesn't have to be. If you leave this out, `bulker` will use the value of the `command` attribute by default.

That's it. If you want your manifest to specify specific versions of images, make sure you include the tags in your `docker_image` strings.

For now, check out these examples:

- [demo manifest](https://github.com/databio/bulker/blob/master/demo/demo_manifest.yaml)
- [my personal manifest](https://github.com/nsheff/docker/blob/master/nsheff_bulker_manifest.yaml)
- [peppro pipeline manifest](https://github.com/databio/peppro/blob/dev/peppro_bulker_manifest.yaml)