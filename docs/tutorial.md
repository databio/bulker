# Tutorial

I assume you've already gone through the [install and configure](install.md) instructions.

## Terminology

Let's start with a few terms:

1. **crate**. A collection of containerized executables. A crate is loaded from a manifest. A crate is analogous to a docker image (but it points to *multiple* images).

2. **manifest**. A manifest defines a crate. It is a list of commands and images to be included in the crate. A manifest is analogous to a Dockerfile.

3. **load**. Loading a manifest will create a folder with executables for each command in the manifest. The folder is named after the manifest. Loading a manifest is analogous to building or pulling an image.

4. **activate**. Any loaded crates are available to activate. Activating a crate does nothing more than prepend the crate folder to your `PATH` variable, giving you easy access to the executables. Activating is analogous to starting a container.


## Loading crates

I assume you've followed the instructions to [install and configure](install.md) bulker. Next, type `bulker list` to see what crates you have available. If you've not loaded anything, it should be empty:

```console
bulker list
```

Let's load a demo crate. Here's a [manifest](http://big.databio.org/bulker/bulker/demo.yaml) that describes 2 commands:

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

There are a few ways to load a manifest. This one is easy because it's already included in the bulker registry, so you can load it like this: 

```console
bulker load demo
```

You could also load any manifest, either local or remote, by just pointing to the yaml file and using the `-f` argument to point to the manifest file (aka cratefile):

```console
bulker load demo -f http://big.databio.org/bulker/bulker/demo.yaml
bulker load demo -f local/path/to/demo.yaml
```

Now if you type `bulker list` you should see the `demo` crate available for activation. But first, let's point out the `-b` argument, which you can pass to `bulker load`. By default, all `bulker load` does is create a folder of executables. *It does not actually pull or build any images*. Docker will automatically pull these by default as soon as you use them, which is nice, but you might rather just grab them all now instead of waiting for that. In this case, just pass `-b` to your `bulker load` command:

```console
bulker load demo -b
```

Now, bulker will instruct docker (or singularity) to pull all the images required for all the executables in this crate.


## Running commands using bulker crates

Once you have loaded a crate, all it means is there's a folder somewhere on your computer with a bunch of executables. You can use it like that if you like, but it simplifies things if you add these commands to your `PATH`. Bulker provides two ways to do this conveniently, depending on your use case: `bulker activate`, and `bulker run`.

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

