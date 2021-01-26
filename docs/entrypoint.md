# How to use a container with an entrypoint

Dockerfiles may contain `CMD` or `ENTRYPOINT` directives that make the image run a command by default. These types of containers don't fit into the default bulker templates, which issue the command name as the default command. We can still get around it, but we have to do one additional thing in the bulker manifest: blank out the docker command to override the bulker default. To do this is as easy as adding a `docker_command` attribute with a blank space as its value under the image entry in the manifest, like this example:

```
  - command: pdftk
    docker_image: mnuessler/pdftk
    docker_args: -v $(pwd):/work
    docker_command: " "
```

Here, the pdftk image specifies an entrypoint, so we have to specify that `docker_command: ' '` to blank out the bulker template. Otherwise, bulker will say something like `docker run mnuessler/pdftk pdftk`, and the `pdftk` argument will not be treated as a command, but as an argument to be passed to the image-specified entrypoint command. 

## For singularity

What if you need to pass an entrypoint to the container? In this case, the container wants to be run with `--entrypoint` instead of calling the command directly. So, we blank out the `docker_command`, and add the `--entrypoint` argument to `docker_args`:

```
  - command: xq
    docker_command: " "
    singularity_command: "xq"
    docker_image: linuxserver/yq
    docker_args: "-i --entrypoint xq"
```

We have to add in the new `singularity_command` to ensure that this manifest will also work with singularity, which doesn't follow the entrypoint framework used by docker.
