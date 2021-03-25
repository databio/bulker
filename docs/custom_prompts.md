# Customizing bulker prompts

By default, when you activate a crate, bulker will change your prompt. You can customize it by specifying the `shell_prompt` attribute in your bulker config. *Make sure you enclose the value in single quotes*; if you use double-quotes the parser will re-escape your prompt escape sequences and break stuff. Here are some examples:

In these examples we'll activate the crate like this:

```console
bulker activate databio/lab
```

The variables that could be displayed are these:

- namespace: `databio`
- crate name: `lab`
- username: `nsheff`
- host: `zither`
- working directory: `code`

# Default prompt

The default bulker prompt shows you the name of the crate you've activated, colored in yellow. Bulker uses `\b` to indicate the name of the bulker namespace and crate. The default prompt is the equivalent of putting this in your config:

```yaml
  shell_prompt: '\[\033[01;93m\]\b|\[\033[00m\]\[\033[01;34m\]\w\[\033[00m\]\$ '
```

![](img/prompts/default.png)


## Include username and hostname

In addition the bulker-provided `\b`, there are lots of other shell-provided variables you can use, like `\u` for username and `\h` for hostname, and `\W` for working directory path. You can look up lists of these by searching for *customizing bash PS1 prompt*. Here's a simple sample using *username* and *hostname*:

```yaml
  shell_prompt: '[\u@\h(\b) \W] $ '
```

![](img/prompts/prompt1.png)

## Change colors

You can al;so use any terminal colors compatible with your terminal. 


```yaml
  shell_prompt: '\u@\h|\e[94m\b\[\e[00m\]:\e[90m\W\e[39m $ '
```

![](img/prompts/prompt2.png)


## Emoji

Yes, you can even put emoji in your prompt, if that's your thing:

```yaml
  shell_prompt: '⚓ \e[94m\b\[\e[00m\]:\e[90m\W\e[39m $ '
```

![](img/prompts/prompt3.png)


## Date/time

This example uses a custom date/time format along with 256-color codes:

```yaml
  shell_prompt: '\D{%y/%m/%d %H:%M}⚓ \e[38;5;141m\b\[\e[00m\]:\e[38;5;29m\W\e[39m $ '
```

![](img/prompts/prompt4.png)
