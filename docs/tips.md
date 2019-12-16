# Tips and FAQ

## How can I prevent `bulker activate` from creating a new shell?

One mildly annoying thing I've found using bulker is that when you `bulker activate` a crate, you get a new shell, which messes with the history; commands typed before the activate are not available in the history, and commands typed within the shell may not be saved. 

Luckily, there's a really easy way to solve this problem. We just need the bulker process to communicate with its parent shell. All the `activate` command really does is prepend a folder to your PATH environment variable. So, we set up a `-e` (echo) argument to `bulker activate` which allows you to retrieve this information in your current shell. This does require adding something to your `.bashrc` so that the calling shell can retrieve the paths returned by bulker.

To do this, just add this to your `.bashrc`:

```shell
bulker-activate() {
  eval "$(bulker activate -e $@)"
}

```

Restart your shell, and from now on use `bulker-activate` instead of `bulker activate`.

## Help! Bulker can't find my config file.

If bulker is giving an error like "No config found in env var: BULKERCFG", this means that the value of $BULKERCFG is not pointing to a file. Make sure you use `export` when defining that shell variable so that it is available to the bulker subprocess. If you don't, you may be able to `echo $BULKERCFG`, but if the value is not exported in the shell, bulker will not be able to read it.

