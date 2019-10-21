# How to start an exploratory shell

For debugging purposes, it can be useful to enter a shell within a container. Since bulker provides command-line executable scripts, it's not necessarily immediately clear how to get in to a container that will be used to execute a specific command.

One way to do this is to write (after activating a crate):

```
cat `which COMMAND`
```

This will print out the containerized executable that will be used `COMMAND`. What we'd like to do is edit this file so that instead of running `COMMAND`, it gives us an interactive shell we can use to explore. This is exactly what bulker does with the *underscore command*:

## Use underscore commands for interactive shells

For every command made available by bulker, it will also produce a command that can be executed with `_COMMAND` (where `COMMAND` is any command provided in the manifest). For example, in the demo manifest that provides the `cowsay` and `fortune` commands, bulker will also create executables named `_cowsay` and `_fortune`. If you execute one of these *underscore* commands, you will *not* run the actual command, but will instead enter a shell within a container of whatever image *is used to run the given command*.

This provides a simple way to enter a container in the exact same way that bulker will use to run the command, allowing you to debug the container interactively.