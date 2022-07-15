# How to specify host- and tool-specific settings

Sometimes you need to mount a particular volume, but only to one container. It feels inefficient to mount it to all containers (although you could do that), so you may be tempted to put it into the manifest file. But this violates bulker's principle of making the manifest completely portable by restricting it to only tool-specific settings. So, how can we enable these kind of settings that are specific to both tool *and* host?

## Tool_args to the rescue!

To accomplish this there's an experimental section in the bulker config called `tool_args`. Here, you can specify settings just like you would in a manifest file, but they're stored in your bulker config.

For example:

```
bulker:
  tool_args:
    docker:
      redis:
        default:
          docker_args: -v /project/shefflab/database/redis:/data
    bioconductor:
      bioconductor_docker:
        default:
          docker_args: --volume=${HOME}/.local/lib/R:/usr/local/lib/R/host-site-library
        devel:
          docker_args: --volume=${HOME}/.local/lib/Rdev:/usr/local/lib/R/host-site-library
```

For the `redis` example, we're mounting a custom folder to `/data`, but only on `docker:redis` containers. 

For the bioconductor example, we're showing how you can mount different host folders to the same container spot, depending on the *tag* (version) of the image being used. This is useful for separating your development vs. stable R packages, for example.
