
## Loading crates

I assume you've followed the instructions to [install and configure](install.md) bulker. Next, type `bulker list` to see what crates you have available. If you've not loaded anything, it should be empty:

```console
bulker list
```

Let's load a demo crate. There are a few ways to load a manifest: either from a bulker registry, or directly from a file.

### Using a bulker registry

Here's a [manifest](http://big.databio.org/bulker/bulker/demo.yaml) that describes 2 commands:

```yaml
manifest:
  name: demo
  version: 1.0.0
  commands:
  - command: cowsay
    docker_image: nsheff/cowsay
    docker_command: cowsay
    dockerargs: "-i"
  - command: fortune
    docker_image: nsheff/fortune
    docker_command: fortune
```

This manifest is located in the bulker registry, under the name `bulker/demo`. Here 'bulker' is the namespace (think of it as the group name) and 'demo' is the name of the crate to load. Since 'bulker' is the default namespace, you can load it like this: 

```console
bulker load demo
```

Doing `bulker load bulker/demo:default` would do the same thing. That's how you load any crate, from any namespace, from the registry.

### Loading crates from a file

You can also load any manifest by pointing to the yaml file with the `-f` argument:

```console
bulker load demo -f http://big.databio.org/bulker/bulker/demo.yaml
bulker load demo -f local/path/to/demo.yaml
```

Here, the registry path ('demo') indicates to bulker what you want to name this crate. You can name it whatever you want, since you're loading it directly from a file and not from the registry...so you can do `bulker load myspace/mycrate -f /path/to/file.yaml`.

Once you've loaded a crate, if you type `bulker list` you should see the `demo` crate available for activation. But first, let's point out the `-b` argument, which you can pass to `bulker load`. By default, all `bulker load` does is create a folder of executables. *It does not actually pull or build any images*. Docker will automatically pull these by default as soon as you use them, which is nice, but you might rather just grab them all now instead of waiting for that. In this case, just pass `-b` to your `bulker load` command:

```console
bulker load demo -b
```

Now, bulker will instruct docker (or singularity) to pull all the images required for all the executables in this crate.


## Running commands using bulker crates

Once you have loaded a crate, all it means is there's a folder somewhere on your computer with a bunch of executables. You can use it like that if you like, by just running these commands directly. For example, the demo crate by default will create the following path: '$HOME/bulker_crates/bulker/demo/default/cowsay'. You can execute this by including the full path:

```
$HOME/bulker_crates/bulker/demo/default/cowsay boo
```

This example demonstrates how simple and flexible bulker is under the hood. But using commands like this is cumbersome. It simplifies things if you add these commands to your `PATH`, plus, then you can more easily use *sets* of commands as a kind of controlled computational environment. Bulker provides two ways to do this conveniently, depending on your use case: `bulker activate`, and `bulker run`.

- *activate*. This will add all commands from a given crate to your PATH and give you a terminal where you can use them. You want to use activate if you want to manage crates like namespaces that you can turn on or off. This is useful for controlling which software versions are used for which tasks, because the manifest controls the versions of software included in a crate.

- *run*. This will run a single command in a new environment that has a crate prepended to the PATH.

Try it out with this command:

```console
bulker run demo "fortune | cowsay"
```

The response is:
```console
Bulker config: /bulker_config.yaml
Activating crate: demo

 ____________________________________
/ It's lucky you're going so slowly, \
| because you're going in the wrong  |
\ direction.                         /
 ------------------------------------
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||
```

## The advantage of bulker over vanilla containers

On the surface, this seems the same as running this command in a container that includes both fortune and cowsay. Indeed, the user experience is pretty similar. What separates this process from a typical container use is that our command is actually not running in a container, but in the host shell, and using *two commands that each run in separate containers*. There is no container that contains both `fortune` and `cowsay`; instead, we have individual containers for each command, and then wrapped each command in an executable. Both of these commands are in our PATH because they're both included in the crate.

## Activating multiple crates

You can also pass a comma-separated list of crates to either `run` or `activate`, which will merge executables from two different crates. This is not practical using vanilla containers because it requires you to build a new container that contained the software from both containers, which would eliminate the advantages of modularity and increase container bloat and disk use. 

As an example, let's load another demo crate that adds a new command `pi`, which prints out `pi` to many digits. We can get our cow to quote these pi definitions by activating both of these crates.

```console
bulker load pi -b
```

Now try running a command that requires commands from two different crates:

```console
bulker run pi,demo "pi | cowsay"
```

Response:
```
Bulker config: /bulker_config.yaml
Activating crate: pi,demo

 _________________________________________
/ 3.1415926535897932384626433832795028841 \
| 971693993751058209749445923078164062862 |
\ 08998628034825342117067                 /
 -----------------------------------------
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||
```

You can get the same result using the `activate` method:

```
bulker activate pi,demo
pi | cowsay
```

## Conclusion

That's basically it. If you're a workflow developer, all you need to do is [write your own manifest](manifest.md) and distribute it with your workflow; in 3 lines of code, users will be able to run your workflow using modular containers, using the container engine of their choice.

