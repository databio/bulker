# <img src="img/bulker_logo.svg" class="img-header"> container executable manager

[![PEP compatible](http://pepkit.github.io/img/PEP-compatible-green.svg)](http://pepkit.github.io)

## What is `bulker`?

`Bulker` is a command-line manager of containerized executables. It produces drop-in replacements to command line tools so that they can be run in a container without any additional user effort. Together with a repository of images, this makes it simple to distribute and use modular containers.

## What makes `bulker` useful?

Instead of typing `docker run ... blah blah blah` and having to type user settings and volumes and environment variables and so on, bulker does it for you. You just keep this in a central configuration file (the `bulker_config.yaml`), which is unique for each computing environment. Then, you produce collections of containers, which we call `crates` (really just a list of containers). Bulker automatically builds executable scripts so that you can run these tools on the command line like drop-in replacements for any command-line tool -- except now, they're running in a container and you didn't have to install them. Because the environment-specific settings are decoupled from the container manifest, the manifest is portable, making it dead easy to distribute modular, containerized software. For more, read [my motivation](motivation.md).

## Quick start

### 1 Install bulker

```console
pip install --user bulker
```

### 2 Load a crate

A bulker crate is a collection of executables that run inside containers. To load a bulker crate, you need a manifest, which lists the commands and images included in this crate. Use [demo_manifest.txt](https://raw.githubusercontent.com/databio/bulker/master/demo/demo_manifest.yaml) for example:

```console
bulker load -m https://raw.githubusercontent.com/databio/bulker/master/demo/demo_manifest.yaml
```

Loading this crate will give you drop-in replacement command-line executables for any commands in the manifest.

### 3 Activate your new crate:

Activate a crate with `bulker activate`:

```console
bulker activate demo
```

Now run any executables in the crate as if they were installed natively:

```console
cowsay Hello world!
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

For more details, check out the [tutorial](tutorial.md).
