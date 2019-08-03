# Bulker

Bulker is a command-line manager of containerized executables. It produces drop-in replacements to command line tools so that they can be run in a container without any additional user effort. It also will manage collections of tools that can be activated or deactivated.

## Example

### 1 Install bulker

```
pip install --user bulker
```

### 2 Load a crate

```
bulker load https://raw.githubusercontent.com/databio/bulker/master/demo/demo_manifest.yaml
```

### 3 Activate your new crate:

Activate a crate with `bulker activate`:

```
bulker activate demo
```

Now run any executables in the crate as if they were installed natively:

```
cowsay Hello World!
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

For details, see the [bulker documentation](https://bulker.databio.org).