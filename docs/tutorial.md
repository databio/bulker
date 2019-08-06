# Tutorial

## Terminology

Let's start with a few terms:

1. **crate**. A collection of containerized executables. A crate is loaded from a manifest.

2. **manifest**. A list of commands to be included in a crate.

3. **load**. Loading a manifest will create a folder with executables for each command in the manifest. The folder is named after the manifest.

4. **activate**. Any loaded crates are available to activate. Activiating a crate does nothing more than prepend the crate folder to your `PATH` variable, giving you easy access to the executables.


## Loading crates

I assume you've followed the instructions to [install and configure](install.md) bulker. Next, type `bulker list` to see what crates you have available. If you've not loaded anything, it should be empty:

```
bulker list
```

Let's load a demo crate:

```
bulker load https://raw.githubusercontent.com/databio/bulker/master/demo/demo_manifest.yaml
```

Now if you type `bulker list` you should see the `demo` crate available for activation. But first, let's point out the `-b` argument, which you can pass to `bulker load`. By default, all `bulker load` does is create a folder of executables (the crate). *it does not actually pull or build any images*. Docker will automatically pull these by default as soon as you use them, which is nice, but you might rather just grab them all now instead of waiting for that. In this case, just pass `-b` to your `bulker load` command:

```
bulker load https://raw.githubusercontent.com/databio/bulker/master/demo/demo_manifest.yaml -b
```

Now, bulker will instruct docker (or singularity) to pull all the images required for all the executables in this crate.


## Running commands using bulker crates

Once you have loaded a crate, all it means is there's a folder somewhere on your computer with a bunch of executables. You can use it like that if you like, but it simplifies things if you add these commands to your `PATH`.  Of course, you could do it manually...

```
export PATH="$HOME/bulker_crates/demo/:$PATH"
```

You could even make this to be permanent, by adding this line in your `.bashrc`. And that's it; you don't need to use bulker any more. But `bulker` also provides two ways to make it more convenient, depending on your use case: `bulker activate`, and `bulker run`.

- *activate*. This will add all commands from a given crate to your PATH and give you a terminal where you can use them.  If you want to manage these crates like namespaces that you can turn on or off, then `bulker activate demo`. This is useful for controlling which software versions are used for which tasks, because the manifest controls the versions of software included in a crate.

- *run*. This will run a single command in a new environment that has a crate prepended to the PATH.



## Conclusion

That's basically it. If you're a workflow developer, all you need to do is [write your own manifest](manifest.md) and distribute it with your workflow; in 3 lines of code, users will be able to run your workflow using modular containers, using the container engine of their choice.

