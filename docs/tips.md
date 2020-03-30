# Tips and FAQ

## Why doesn't bulker activate preserve history?

One mildly annoying thing I've found using bulker is that when you `bulker activate` a crate, you get a new shell, which messes with the history; commands typed before the activate are not available in the history, and commands typed within the shell may not be saved. This is because when you activate a bulker environment, it starts a new shell. The old shell won't have recorded its history for viewing by the new shell. Then, when the close the shell and go back to the calling environment, the previous history is restored. 

You can change this behavior by adding a function like this to your `.bashrc`:

```
ba() {
  history -a
  if [ $# -eq 0 ]; then
    echo "Initializing bulker crate: bulker/demo"
    bulker activate bulker/demo
  else
  bulker activate $@
  fi
  history -r
}
```

Then, use `ba` instead of `bulker activate`. This just calls `history -a` first, which writes the parent shell's history to file, then activates the crate, which will write its history to file by default when it closes; after it's closed, control passes back to the calling shell, which then runs `history -r`, which reloads the history file that has now been written by the child shell with the bulker environment. This has the effect of making the histories appear seemless between the parent environment and the bulker shells.

## How can I prevent `bulker activate` from creating a new shell?

In earlier versions of bulker, I recommneded using an `--echo` command to load the bulker environment into the current shell to avoid creating a new one. This is still possible, but no longer recommended, since I came up with a better way to control things using the shell rcfiles. But if you have other reasons, it's still possible to prevent bulker from creating a new shell -- we just need the bulker process to communicate with its parent shell. All the `activate` command really does is prepend a folder to your PATH environment variable. So, we set up a `-e` (echo) argument to `bulker activate` which allows you to retrieve this information in your current shell. This does require adding something to your `.bashrc` so that the calling shell can retrieve the paths returned by bulker.

To do this, just add this to your `.bashrc`:

```shell
bulker-activate() {
  eval "$(bulker activate -e $@)"
}

```

Restart your shell, and from now on use `bulker-activate` instead of `bulker activate`.

## Help! Bulker can't find my config file.

If bulker is giving an error like "No config found in env var: BULKERCFG", this means that the value of $BULKERCFG is not pointing to a file. Make sure you use `export` when defining that shell variable so that it is available to the bulker subprocess. If you don't, you may be able to `echo $BULKERCFG`, but if the value is not exported in the shell, bulker will not be able to read it.

