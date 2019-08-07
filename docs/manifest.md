# How to create a manifest

Writing a manifest is really simple. It's just a list of commands you want to be able to run, and the containers that can run them. A manifest is a `yaml` file which includes a `manifest_name` (which is the activation key for `bulker activate MANIFEST_NAME`, and also the default name of the folder where the executables will be saved). Then you add a `commands` section which lists the commands and a few attributes.

```
manifest:
  name: demo
  version: 1.0.0
  commands:
  - command: cowsay
    docker_image: nsheff/cowsay
    docker_command: cowsay
    dockerargs: "-i"
  - command: fortune
    docker_image: nsheff/fortune
    docker_command: fortune
```
1. *command* is the executable name; this is what the user will type in to run the command (*e.g.* `cowsay`).

2. *dockerargs* is any additional arguments required by this tool. You should add `-i` for tools that need to read/write piped output to/from stdin and stdout, and add `-t` for commands like `python` or `R` that allocate a user interface.

3. *docker_image* is the location of the image.

4. *docker_command* is the command that will be executed inside the container. This is often the same as the `command` itself for the user, but it doesn't have to be. If you leave this out, `bulker` will use the value of the `command` attribute by default.

That's it. If you want your manifest to specify specific versions of images, make sure you include the tags in your `docker_image` strings.

For now, check out these examples at [big.databio.org/bulker](http://big.databio.org/bulker):

Demos:

- [demo manifest](http://big.databio.org/bulker/demo_manifest.yaml)
- [pi manifest](http://big.databio.org/bulker/demo_manifest.yaml)
- [cowsay+fortune](http://big.databio.org/bulker/cowsay_fortune.yaml)

Real-life manifests:

- [my personal manifest](http://big.databio.org/bulker/nsheff_bulker_manifest.yaml)
- [peppro pipeline manifest](http://big.databio.org/bulker/peppro_bulker_manifest.yaml)
