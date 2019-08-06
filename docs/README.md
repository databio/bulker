# <img src="img/bulker_logo.svg" class="img-header"> container executable manager

[![PEP compatible](https://pepkit.github.io/img/PEP-compatible-green.svg)](http://pepkit.github.io)

## What is `bulker`?

`Bulker` is a command-line manager of containerized executables. It produces drop-in replacements to command line tools so that they can be run in a container without any additional user effort. Together with a repository of images, this makes it simple to distribute and use modular containers.

## What makes `bulker` useful?

1. **It produces containerized drop-in replacement executables**. After loading `pandoc`, you'll invoke it with nothing more than `pandoc` on the command line. Bulker wraps the container details `docker run -it --volume ...`, so native workflows become immediately containerized. *You'll be using containers without knowing it*. 

2. **It improves portability by decoupling environment from tool settings**. Running a container integrates variables from the environment (*e.g.* volumes to mount) with tool specifics (*e.g.* command, image source). Bulker decouples these, making the container manifest portable.

3. **It distributes collections of containers**. Bulker simplifies distributing a set of related container executables in a *crate*, like all the tools needed to run a workflow. Install a whole set with one command: `bulker load -m crate_manifest.yaml`. Workflow authors need only provide a manifest to containerize a workflow.


For more, read [my motivation](motivation.md).

## Quick start

### 1 Install bulker

```console
pip install --user bulker
```

### 2 Load a crate

A bulker crate is a collection of executables that run inside containers. To load a bulker crate, you need a manifest, which lists the commands and images included in this crate. Use [demo_manifest.txt](https://raw.githubusercontent.com/databio/bulker/master/demo/demo_manifest.yaml) for example:

```console
bulker load https://raw.githubusercontent.com/databio/bulker/master/demo/demo_manifest.yaml
```

Loading this crate will give you drop-in replacement command-line executables for any commands in the manifest.

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
    \
     \
      \     
                    ##        .            
              ## ## ##       ==            
           ## ## ## ##      ===            
       /""""""""""""""""___/ ===        
  ~~~ {~~ ~~~~ ~~~ ~~~~ ~~ ~ /  ===- ~~~   
       \______ o          __/            
        \    \        __/             
          \____\______/   

```

### 4 Or, run commands directly

You can also just run commands without activating a crate:

```console
bulker run CRATE cowsay Hello world!
```

Where CRATE is the bulker crate you wish to execute the command in. For more details, check out the [tutorial](tutorial.md).


<!-- Then, you produce collections of containers, which we call `crates` (really just a list of containers). Bulker automatically builds executable scripts so that you can run these tools on the command line like drop-in replacements for any command-line tool -- except now, they're running in a container and you didn't have to install them. Because the environment-specific settings are decoupled from the container manifest, the manifest is portable, making it dead easy to distribute modular, containerized software. -->