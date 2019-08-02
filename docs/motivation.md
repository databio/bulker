# What's the point of bulker?

Container systems like `docker` and `singularity` are really useful, but there are two use cases that I've struggled to find a really simple solution for. `Bulker` is a general framework that really nicely solves these two niche problems:

## Workflow systems

There's a lot of existing tooling around individual containers, or around collections of containers running simultaneously (like `kubernetes` or `docker swarm`). A specialized use case is a workflow system that will run a series of commands sequentially. Here, we're only running 1 container at a time, so we don't need the complexity of a container swarm. But just dealing with containers one-by-one is a pain when your workflow needs 15 different tools. It would be nice to be able to distribute a *collection* of containers somehow.

Right now, it's common for people to build mega-images with all the software for the entire workflow. This is inefficient because different workflows that use the same software will not be able to share it. The container system is really designed to be more modular, where each individual tool has its own container. Projects like [biocontainers](http://biocontainers.pro) make a lot of these individual, modular containers available, but this doesn't solve the problem of making them easily useable by a workflow system.

`Bulker` introduces the concept of a `crate`, which is a *collection of containerized executables*. Given a list of commands, and containers that can run them (which we call a *manifest*), `bulker` can automatically create a folder of executables. This allows a workflow developer to simply provide a manifest, and users can install all the software in a single line of code, making every tool available in the `PATH`.

## Drop-in executable replacements

For years I've been refining my own little [docker system](http://github.com/nsheff/docker) that allows me to install a command-line tool one time, and then use it on all my computers. What I want is to be able to just type `pandoc`, for example, and have it run in a docker container, so that I don't have to install it... and I want that to *just work* on all my computers, without having to do anything. My system combined a series of shell scripts that can be populated with a few variables, and then individual, manually created shell scripts for each executable that I store in a folder in a git repository. By just cloning that repository and including a bin folder in my `PATH` I get access to these containerized executables.

The problem is that the volumes and environment variables I want to automatically mount on all these containers is not the same in every computing environment. `Bulker` extends this so that a separate, environment-specific config file (the `bulker_config.yaml` file) keeps track of the environment-specific settings, like volumes, environment variables, etc. Then, I use a template-driven automatic executable builder to create all the executables I need.

Here's an example of my manifest that I use to create my own containerized executables I use across all my desktops/laptops/workstations: [nsheff_bulker_manifest.yaml](https://github.com/nsheff/docker/blob/master/nsheff_bulker_manifest.yaml).