# <img src="img/bulker_logo.svg" class="img-header"> distributes containers simply

[![PEP compatible](http://pepkit.github.io/img/PEP-compatible-green.svg)](http://pepkit.github.io)

## What is `bulker`?

`Bulker` is a command-line manager of containerized executables. It produces drop-in replacements to command line tools so that they can be run in a container without any additional user effort. It also will manage collections of tools that can be activated or deactivated.


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
cd bulker
bulker load -m demo/demo_manifest.yaml
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

```

<img src="img/divvy-merge.svg" style="float:right; padding-left: 25px; padding-right: 5px">

Divvy will take variables from a file or the command line, merge these with environment settings to create a specific job script. Write a submission script from the command line:

```{console}
divvy write --package slurm \
	--settings myjob.yaml \
	--sample sample1 \
	--outfile submit_script.txt
```

### Python interface

You can also use `divvy` via python interface, or you can use it to make your own python tools divvy-compatible:

```{python}
import divvy
dcc = divvy.ComputingConfiguration()
dcc.activate_package("slurm")

# write out a submission script
dcc.write_script("test_script.sub", 
	{"code": "bowtie2 input.bam output.bam"})
```

For more details, check out the [tutorial](tutorial).
