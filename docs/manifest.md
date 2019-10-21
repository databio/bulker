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
    docker_args: "-i"
  - command: fortune
    docker_image: nsheff/fortune
    docker_command: fortune
```
1. *command* is the executable name; this is what the user will type in to run the command (*e.g.* `cowsay`).

2. *docker_args* is any additional arguments required by this tool. You should add `-i` for tools that need to read/write piped output to/from stdin and stdout, and add `-t` for commands like `python` or `R` that allocate a user interface.

3. *docker_image* is the location of the image.

4. *docker_command* is the command that will be executed inside the container. This is often the same as the `command` itself for the user, but it doesn't have to be. If you leave this out, `bulker` will use the value of the `command` attribute by default.

That's it. If you want your manifest to specify specific versions of images, make sure you include the tags in your `docker_image` strings.

## Examples

Check out these examples at [http://hub.bulker.io](http://hub.bulker.io):


Demos:

- [demo manifest](http://hub.bulker.io/bulker/demo.yaml) - Cowsay and fortune example
- [pi manifest](http://hub.bulker.io/bulker/pi.yaml) - Example of the `pi` command.

Real-life manifests:

- [my personal manifest](http://hub.bulker.io/databio/nsheff.yaml) - My manifest for everyday computing
- [peppro pipeline manifest](http://hub.bulker.io/databio/peppro.yaml) - pipeline manifest for PEPPRO.
