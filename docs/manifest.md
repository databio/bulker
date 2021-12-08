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

2. *docker_args* is any additional arguments required by this tool. You should add `-i` for tools that need to read/write piped output to/from stdin and stdout, and add `-t` for commands like `python` or `R` that allocate a user interface. For singularity, these additions aren't usually necessary, but you could adjust a singularity argument with `singularity_args` if you really needed to.

3. *docker_image* is the location of the image.

4. *docker_command* is the command that will be executed inside the container. This is often the same as the `command` itself for the user, but it doesn't have to be. If you leave this out, `bulker` will use the value of the `command` attribute by default.

That's it. If you want your manifest to specify specific versions of images, make sure you include the tags in your `docker_image` strings.

## Manifests and singularity

The examples above are docker-centric, but if you're using singularity, you may wonder if you have to do anything different in your manifest. The answer is *not really* -- one of the goals of bulker is to be able to work with a single manifest, and have that manifest work with either docker *or* singularity. So the idea is to create a single manifest, and it should just work with both.

That said, there is some potential for confusion. First, the bulker manifest points at docker images. When you're using singularity, bulker will use singularity to convert these into singularity images -- but they have to be docker images to begin with. This is how bulker manages to use a single manifest for either system. If I allowed you to use singularity images instead of docker images in the bulker manifest, then I'd need to convert those into docker images for the manifest to work with docker. It's just easier the other way around, because singularity has easy built-in methods to use docker containers, so that's what bulker uses.

Second, the `docker_args` argument is only used with docker. In my use cases, I've never had a need to do something like this with singularity, because the nuances of the docker flags I use like `-i` and `-t` aren't relevant in a singularity command. Nevertheless, there is an analogous `singularity_args` argument if you find there are some singularity-specific flags you need to pass.

Similarly, in an ideal world, you'd never need to use `docker_command` because the `command` would be the same. But for some containers, depending on how it uses a docker ENTRYPOINT, it might be required to tweak the `command` that is sent to docker. For singularity, bulker will try to use the same command specified under `docker_command`, but if you really have a situation where you need the command to differ between docker and singularity, the you can use `singularity_command` to specify the difference. I don't believe I've ever had to use this, though.

In conclusion, all these example manifests should work in the exact same way with either docker or singularity. The reason the manifests appear docker-centric is that bulker considers the docker image the ground truth, and then uses singularity to build from that image, rather than the other way around -- but in no way does this mean you can't use singularity with bulker; as mentioned, that's one of the main strengths of bulker.

## Examples

Check out these examples at [http://hub.bulker.io](http://hub.bulker.io):

Demos:

- [demo manifest](http://hub.bulker.io/bulker/demo.yaml) - Cowsay and fortune example
- [pi manifest](http://hub.bulker.io/bulker/pi.yaml) - Example of the `pi` command.

Real-life manifests:

- [my personal manifest](http://hub.bulker.io/databio/nsheff.yaml) - My manifest for everyday computing
- [peppro pipeline manifest](http://hub.bulker.io/databio/peppro.yaml) - pipeline manifest for PEPPRO.
