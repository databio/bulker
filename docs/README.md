# <img src="img/bulker_logo.svg" class="img-header"> container executable manager

[![PEP compatible](http://pepkit.github.io/img/PEP-compatible-green.svg)](http://pepkit.github.io)

## What is `bulker`?

`Bulker` is a command-line manager of containerized executables. It produces drop-in replacements to command line tools so that they can be run in a container without any additional user effort. Together with a repository of images, this makes it simple to distribute and use modular containers.


## What makes `bulker` useful?

Instead of typing `docker run ... blah blah blah` and making all your user settings and volumes and environment varibles match, bulker does it for you.

It also makes it easy to distribute, because those things are not universal.


## Quick start

### 1 Install bulker

```console
pip install --user bulker
```

### 2 Load a crate

A bulker crate is a collection of executables that run inside containers. To load a bulker crate, you need a manifest, which lists the commands and images included in this crate. Use `demo_manifest.txt` for example:

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
