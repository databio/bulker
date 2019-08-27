jupyter:True
# Tutorial

I assume you've already gone through the [install and configure](install.md) instructions. Let's initialize a bulker config file for this tutorial:


```bash
rm "bulker_config.yaml"
export BULKERCFG="bulker_config.yaml"
bulker init -c $BULKERCFG
```

```.output
Guessing container engine is docker.
Wrote new configuration file: bulker_config.yaml

```

## Terminology

Let's start with a few terms:

1. **crate**. A collection of containerized executables. A crate is analogous to a docker image (but it provides *multiple* commands by pointing to *multiple* images).

2. **manifest**. A manifest defines a crate. It is a list of commands and images to be included in the crate. A manifest is analogous to a Dockerfile. It could be thought of as a *Cratefile*.

3. **load**. Loading a manifest will create a local folder with executables for each command in the manifest. Loading a manifest is analogous to building or pulling an image.

4. **activate**. Activating a crate is what allows you to run the commands in a crate. Activating is analogous to starting a container. Any loaded crates are available to activate. Activating a crate does nothing more than prepend the crate folder to your `PATH` variable.



## Loading crates

I assume you've followed the instructions to [install and configure](install.md) bulker. Next, type `bulker list` to see what crates you have available. If you've not loaded anything, it should be empty:



```bash
bulker list
```

```.output
Bulker config: bulker_config.yaml
Available crates:
No crates available. Use 'bulker load' to load a crate.

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



```bash
bulker load demo
```

```.output
Bulker config: bulker_config.yaml
Got URL: http://big.databio.org/bulker/bulker/demo.yaml
Executable template: /home/nsheff/.local/lib/python3.5/site-packages/bulker/templates/docker_executable.jinja2
Loading manifest: 'demo'. Activate with 'bulker activate demo'.
Commands available: cowsay, fortune

```

Doing `bulker load bulker/demo:default` would do the same thing. That's how you load any crate, from any namespace, from the registry. 

### Loading crates from a file

You can also load any manifest by pointing to the yaml file with the `-f` argument: 

```
bulker load demo -f http://big.databio.org/bulker/bulker/demo.yaml
```


Here, the registry path ('demo') indicates to bulker what you want to name this crate. You can name it whatever you want, since you're loading it directly from a file and not from the registry...so you can do `bulker load myspace/mycrate -f /path/to/file.yaml`.

Once you've loaded a crate, if you type `bulker list` you should see the `demo` crate available for activation. But first, let's point out the `-b` argument, which you can pass to `bulker load`. By default, all `bulker load` does is create a folder of executables. *It does not actually pull or build any images*. Docker will automatically pull these by default as soon as you use them, which is nice, but you might rather just grab them all now instead of waiting for that. In this case, just pass `-b` to your `bulker load` command:



```bash
bulker load demo -b -r
```

```.output
Bulker config: bulker_config.yaml
Got URL: http://big.databio.org/bulker/bulker/demo.yaml
Executable template: /home/nsheff/.local/lib/python3.5/site-packages/bulker/templates/docker_executable.jinja2
Building images with template: /home/nsheff/.local/lib/python3.5/site-packages/bulker/templates/docker_build.jinja2
Removing all executables in: /home/nsheff/bulker_crates/bulker/demo/default
Using default tag: latest
latest: Pulling from nsheff/cowsay
Digest: sha256:14fa1f533678750afd09536872e068e732ae4f735c52473450495d5af760c2e3
Status: Image is up to date for nsheff/cowsay:latest
Container available at: /home/nsheff/simages/nsheff/cowsay
Using default tag: latest
latest: Pulling from nsheff/fortune
Digest: sha256:a980b4b333a8b89acf4c2fe90dde5da93898ab574a6d2e88152398724667957b
Status: Image is up to date for nsheff/fortune:latest
Container available at: /home/nsheff/simages/nsheff/fortune
Loading manifest: 'demo'. Activate with 'bulker activate demo'.
Commands available: cowsay, fortune

```

Now, bulker will instruct docker (or singularity) to pull all the images required for all the executables in this crate. (The `-r` just forces an overwrite without prompting). Now we can see it in our available local crates: 


```bash
bulker list
```

```.output
Bulker config: bulker_config.yaml
Available crates:
bulker/demo:default -- /home/nsheff/bulker_crates/bulker/demo/default

```





## Running commands using bulker crates

Once you have loaded a crate, all it means is there's a folder somewhere on your computer with a bunch of executables. You can use it like that if you like, by just running these commands directly. For example, the demo crate by default will create the following path: '$HOME/bulker_crates/bulker/demo/default/cowsay'. You can execute this by including the full path:


```bash
$HOME/bulker_crates/bulker/demo/default/cowsay boo
```

```.output
 _____
< boo >
 -----
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||

```


This example demonstrates how simple and flexible bulker is under the hood. But using commands like this is cumbersome. It simplifies things if you add these commands to your `PATH`, plus, then you can more easily use *sets* of commands as a kind of controlled computational environment. Bulker provides two ways to do this conveniently, depending on your use case: `bulker activate`, and `bulker run`.

- *activate*. This will add all commands from a given crate to your PATH and give you a terminal where you can use them. You want to use activate if you want to manage crates like namespaces that you can turn on or off. This is useful for controlling which software versions are used for which tasks, because the manifest controls the versions of software included in a crate.

- *run*. This will run a single command in a new environment that has a crate prepended to the PATH.

Try it out with this command:



```bash
bulker run demo "fortune | cowsay"
```

```.output
Bulker config: bulker_config.yaml
Activating crate: demo

 _________________________________________
/ You are deeply attached to your friends \
\ and acquaintances.                      /
 -----------------------------------------
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



```bash
bulker load pi -b -r
```

```.output
Bulker config: bulker_config.yaml
Got URL: http://big.databio.org/bulker/bulker/pi.yaml
Executable template: /home/nsheff/.local/lib/python3.5/site-packages/bulker/templates/docker_executable.jinja2
Building images with template: /home/nsheff/.local/lib/python3.5/site-packages/bulker/templates/docker_build.jinja2
Using default tag: latest
latest: Pulling from nsheff/pi
Digest: sha256:6187416a85719fb42bcd4e4c62ffce3b5757c2d17813090cadbd9f4eeb9c9425
Status: Image is up to date for nsheff/pi:latest
Container available at: /home/nsheff/simages/nsheff/pi
Loading manifest: 'pi'. Activate with 'bulker activate pi'.
Commands available: pi

```

Now try running a command that requires commands from two different crates:


```bash
bulker run pi,demo "pi | cowsay"
```

```.output
Bulker config: bulker_config.yaml
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

Just to make sure you realize what's happening here and why this is so cool: this is *not* a command running in a single container. In fact, the command itself is running in the host shell, and the pipe (`|`) is handled by the host shell. The two executables, `pi` and `cowsay`, are each being run within their own modular containers that do only one thing. And, each of these commands are located in different crates, which are activated simultaneously.


## Conclusion

That's basically it. If you're a workflow developer, all you need to do is [write your own manifest](manifest.md) and distribute it with your workflow; in 3 lines of code, users will be able to run your workflow using modular containers, using the container engine of their choice.


