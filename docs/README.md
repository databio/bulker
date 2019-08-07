# <img src="img/bulker_logo.svg" class="img-header"> containers made easy

[![PEP compatible](https://pepkit.github.io/img/PEP-compatible-green.svg)](http://pepkit.github.io)

## What is `bulker`?

`Bulker` manages collections of containerized executables. It builds drop-in replacements to command line-tools that act just like native tools, but are run in a container. Think of `bulker` as a lightweight wrapper on top of `docker`/`singularity` to simplify sharing and using compute environments that run containers.

## What makes `bulker` useful?

1. **It produces containerized drop-in replacement executables**. If you load `pandoc` with bulker, you'll invoke it in a shell by typing just "`pandoc`". Bulker wraps the container details like "`docker run -it --volume ...`", so native workflows become immediately containerized. *You'll be using containers without knowing it*. 

2. **It improves portability by decoupling environment from tool settings**. Running a container integrates variables from the environment (*e.g.* volumes to mount) with tool specifics (*e.g.* command, image source). Bulker decouples these, making the container manifest portable.

3. **It distributes collections of containers**. Bulker simplifies distributing a set of related container executables in a *crate*, like all the tools needed to run a workflow. Install a whole set with one command: `bulker load crate_manifest.yaml`. Workflow authors need only provide a manifest to containerize a workflow.

For more, read [my motivation](motivation.md).

## Is `bulker` a package manager? How is it different?

`Bulker` is not a package manager, but it *can* replace some package manager tasks. For example, instead of installing software natively using your package manager, you could load it using bulker. 

Old way:

```console
sudo apt install cowsay
sudo apt install fortune
cowsay | fortune
```

New way:
```console
bulker load http://big.databio.org/bulker/cowsay_fortune.yaml
bulker run demo "cowsay | fortune"
```


The difference is: 

- **Bulker uses containers**. Package managers install packages/tools natively, but bulker does not. Bulker tools are *all containerized*, so bulker relies on existing infrastructure from docker. 

- **Bulker is 'collection first'**. Most package managers operate on tools (*e.g.* `pip install tool`, `conda install tool`, or `apt install tool`). Bulker operates on *collections*: `bulker load set`.

With these two features, `bulker` makes it easier than a traditional package manager to distribute and use a standard, version-controlled computing environment. 

## Quick start

### 1 Install bulker

```console
pip install --user bulker
```

### 2 Load a crate

A bulker crate is a collection of executables that run inside containers. To load a bulker crate, you need a manifest, which lists the commands and images included in this crate. Use [cowsay_fortune.yaml](http://big.databio.org/bulker/cowsay_fortune.yaml) for example:

```console
bulker load http://big.databio.org/bulker/cowsay_fortune.yaml
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