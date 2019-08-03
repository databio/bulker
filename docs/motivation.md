# What's the point of bulker?

Container systems like `docker` and `singularity` are really useful, but there are two use cases that I've struggled to find a really simple solution for. `Bulker` is a general framework that really nicely solves these two niche problems:

## How to containerize a workflow

There's a lot of existing tooling around individual containers or sets of containers running simultaneously (like `kubernetes` or `docker swarm`). But what about containers for workflows that will run a series of commands sequentially? In a workflow, we're only running 1 container at a time, so we don't need the complexity of a container swarm. But going one-by-one is a pain when your workflow needs 15 different tools.

One solution is to build a mega-image with all 15 command-line tools required for the entire workflow. This is pretty common, and what I've done in the past. But this is inefficient because different workflows that use the same software will not be able to share it. It also makes it hard to update individual components, makes images huge, and goes against the modular philosophy of image where each individual tool has its own image. This promotes reusability, reduces resource usage, and is easier to maintain.

So, if not mega-images, how should we containerize a workflow? Using individual images sounds nice, but there are a few challenges with the individual image approach:

1. *Distribution*.  It would be nice to be able to distribute a *collection* of images somehow, but there isn't a way to do this easily. 

2. *Portability*. It's kind of counter-intuitive, but in a way, using individual images *reduces* portability... For instance, do I make it so that every command in my workflow starts with `docker run ...` or `singularity run...`? In that case, the workflow *requires* a specific container engine. Or, if I make it flexible, that seems like a lot of work to build and maintain. How can I easily make the workflow independent of any one container system, and also make it work for users who don't want to use containers at all?

## How to use one installation across computing environments

The second use case is also a problem of portability. I use a lot of different computing environments: my desktop at work, one or more remote servers, my laptop, etc. I want a set of common commands and tools installed on all of these systems, but I really don't want to install and maintain all this software 5 times. This seems like the perfect use-case for containers, but I struggled for years to figure out how to do it right. Plus, the HPC at work runs singularity, but I use docker at home, so that adds additional complexity. What I want is to be able to just clone a git repository on each computer, and then automatically have `pandoc` and `samtools` and `latex` and `R` and ... available without doing anything else. I need these commands to just run in a container, so that I don't have to install it... and I want that to *just work* on all my computers, without having to do anything. 

Eventually I refined my own little [docker system](http://github.com/nsheff/docker) that allows me to install a command-line tool one time, and then use it on all my computers. My system combined a series of shell scripts that can be populated with a few variables, and then individual, manually created shell scripts for each executable that I store in a folder in a git repository. By just cloning that repository and including a bin folder in my `PATH` I get access to these containerized executables. The problem I faced is that the volumes and environment variables I want to automatically mount on all these containers is not the same in every computing environment. On the HPC I need to mount a particular filesystem that doesn't exist on my laptop, for example.

## How bulker solves these problems

`Bulker` solves both of these problems in a really simple and elegant way. For distribution, `bulker` introduces the concept of a `crate`, which is a *collection of containerized executables*. A workflow developer just creates a list of commands and images that run them, which we call a *manifest*. `Bulker` uses this manifest to automatically create a folder of executables. Users can install all the software in a single line of code, making every tool available in the `PATH`. This solves the portability challenge, too. The workflow itself doesn't actually change -- it is completely unaware of containers. Because the containers are completely codified by drop-in replacement executables, it is by default smart enough to run each command in its appropriate container with no additional work. Bulker essentially makes it dead simple to containerize a workflow by outsourcing all the command-wrapping tasks to bulker.

`Bulker` decouples the tool-specific settings for each image from the environment settings that vary by computer system. The environment-specific config file (the `bulker_config.yaml` file) keeps track of the environment-specific settings, like volumes, environment variables, etc. Then, I use a template-driven automatic executable builder to create all the executables I need, which vary by system.

Here's an example of my manifest that I use to create my own containerized executables I use across all my desktops/laptops/workstations: [nsheff_bulker_manifest.yaml](https://github.com/nsheff/docker/blob/master/nsheff_bulker_manifest.yaml).

Essentially, I just create this one manifest, which is container-system and computing-environment agnostic. Bulker pairs this information with the local configuration I set up for each computing environment, and that's it. To install a new package across all my systems is as simple as updating the manifest and then running a `bulker` update. With almost no maintenance, I keep my computing systems in sync, even across different container systems.
