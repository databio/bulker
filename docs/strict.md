# How to create strict environments

The activate and run commands are quite simple: to construct the computing environment, they simply prepend the appropriate folder to the user's PATH variable, providing a shell execution environment in which all the manifest commands are available for direct execution. By prepending to the PATH variable, these commands have the effect of *overlaying* the commands on the current environment. In other words, any commands included in the crate will mask existing commands, but any unmasked host commands will be also be available. This feature is desirable in some cases, such as interactive analysis, but may be problematic if strict reproducibility is required. In this case, bulker also provides a `--strict` flag that provides an environment in which no host commands are directly accessible, so that only commands included in the crate will be available. This is accomplished by overwriting rather than prepending the PATH with a crate path.

If you're interested in strict environments, you'll also want to be aware of the `host_commands` section of the manifest file. Because completely wiping out your `PATH` will remove *all* the executables, this actually breaks docker. So, we do need a few host commands still available, and these can be specified in the manifest under `host_commands`, like this, here's the `alpine` manifest:

```{console}
manifest:
  name: alpine
  commands: null
  description: A minimal set of host commands required for docker/bulker to run.
  host_commands:
  - id
  - ls
  - lesspipe
  - dircolors
  - basename
  - dirname
  - which
  - docker
  - singularity
```

These commands will just be copied over with links into the bulker crate, so that they will run the host commands. This manifest demos how `host_commands` work, but also serves another purpose: this is the minimal set of commands that are necessary for docker, to create a `strict` environment. 

So, if you're interested in making your manifest available to be operated in `strict` mode, the best thing to do is make sure the manifest imports this alpine manifest. This is explained in more detail in [how to import manifests](import.md).