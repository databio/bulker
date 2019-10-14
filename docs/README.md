# <img src="img/bulker_logo.svg" class="img-header"> containers made easy

[![PEP compatible](https://pepkit.github.io/img/PEP-compatible-green.svg)](http://pepkit.github.io) [![Build Status](https://travis-ci.org/databio/bulker.svg?branch=master)](https://travis-ci.org/databio/bulker)

## What is bulker?

Bulker builds multi-container computing environments that are both **modular** and **interactive**. 
A bulker environment consists of individual container images that can be mixed and matched efficiently. Bulker environments are portable, interactive, and independent of any specific workflow. Bulker simplifies both interactive analysis and workflow development by building drop-in replacements to command-line tools that act like native tools, but run in containers. Think of bulker as a lightweight wrapper on top of docker/singularity to simplify sharing complete compute environments that run containers.

## What makes bulker useful?

1. **It simplifies using containers**. If you load pandoc with bulker, you'll invoke it in a shell by typing just `pandoc`; bulker wraps the details like "`docker run -it --volume ...`". It also spans container engines (docker and singularity), reducing to a single interface.*You'll be using containers without knowing it*. 

2. **It distributes multiple tools all at once**. You can distribute a *set* of images, like all the tools needed to run a workflow, with one command: `bulker load namespace/toolset`. *Bulker loads multiple independent tools as easily as installing just one*.

3. **It makes workflows automatically containerized**. Since bulker commands act like native commands, a bulker environment immediately makes native workflows containerized. Workflow authors need only provide a list of commands. *Bulker automatically containerizes any workflow built with any workflow system.*

4. **It makes environments portable and interactive**. You can move a bulker environment around from host to host easily because bulker decouples environment settings from tool settings. *Bulker environments can be moved independently and activated interactively*.

For more, read [my motivation](motivation.md).

<!-- produces containerized drop-in replacement executables

portability by 

Running a container integrates variables from the environment (*e.g.* volumes to mount) with tool specifics (*e.g.* command, image source). Bulker decouples these, making the environment descriptions portable.



Workflow authors need only provide a list of commands to containerize a workflow.
 -->


## Is bulker a package manager? How is it different?

Bulker is not a package manager, but it *can* replace some package manager tasks. For example, instead of installing software natively using pip or conda, you could load it using bulker. The differences are: 

- **Bulker uses containers**. Package managers install tools natively. Bulker installs *containerized* software. 

- **Bulker is 'collection first'**. Most package managers operate on tools (*e.g.* `pip install tool`, `conda install tool`, or `apt install tool`). Bulker operates on *collections*: `bulker load toolset`.

With these two features, `bulker` makes it easier than a traditional package manager to distribute and use a standard, version-controlled computing environment. 

## Is bulker a workflow manager? How is it different?

Bulker is not a workflow manager, either. But bulker *can* take over the container-management aspect of an existing workflow. The key difference is: 

- **Bulker environments are independent**. Bulker environments are not tied to workflows. In fact, bulker doesn't know anything about your workflow. It only cares about the computing environment.

Just write your workflow without containers and use a bulker environment instead, and you'll get portability, interactivity, and efficiency for free! 

## Quick start

### 1 Install bulker

```console
pip install --user bulker
```

### 2 Load a crate

A bulker crate is a collection of executables that run inside containers. Load the [cowsay fortune example](http://big.databio.org/bulker/bulker/demo.yaml):

```console
bulker load demo
```

Loading this crate will give you drop-in replacement command-line executables for any commands in the crate.

### 3 Activate your new crate:

Activate a crate with `bulker activate`:

```console
bulker activate demo
```

Now run any executables in the crate as if they were installed natively. The first time you run a command, the actual container image will be downloaded automatically by docker:

```console
$ cowsay Hello world!
```
Response: 
```console
 ______________
< Hello world! >
 --------------
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||
```


### 4 Or, run commands directly

You can also just run commands without activating a crate:

```console
bulker run demo cowsay Hello world!
```

You can use a different crate with `bulker run CRATE command --args`, where CRATE is the bulker crate you wish to execute the command in.

So far, seems similar to a vanilla container system, right? It's not. Under the hood, this simple system is using individual, modular multi containers, letting you share complete, multi-tool containerized computing environments easily *and* efficiently. For more details, check out the [tutorial](tutorial.md).


<!-- Then, you produce collections of containers, which we call `crates` (really just a list of containers). Bulker automatically builds executable scripts so that you can run these tools on the command line like drop-in replacements for any command-line tool -- except now, they're running in a container and you didn't have to install them. Because the environment-specific settings are decoupled from the container manifest, the manifest is portable, making it dead easy to distribute modular, containerized software. -->