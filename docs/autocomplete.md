# How to enable bash autocompletion

Bulker provides bash autocompletion. The autocompletion script can be found in [bash_complete.sh](https://github.com/databio/bulker/blob/master/bash_complete.sh). Add the contents of this file to your `.bashrc` or `.profile` so that it runs whenever the shell starts.

After reloading the shell, when you type `bulker` and hit `<tab><tab>`, it will populate the list of bulker commands. When you type `bulker run` or `bulker activate` and hit `<tab><tab>`, it will list your available crates.
	