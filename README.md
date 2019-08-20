# Bulker

Bulker manages collections of containerized executables. It builds drop-in replacements to command line-tools that act just like native tools, but are run in a container. Think of bulker as a lightweight wrapper on top of docker/singularity to simplify sharing and using compute environments that run containers.

For details, see the [bulker documentation](https://bulker.databio.org).

## Example

```
pip install --user bulker
bulker load demo
bulker activate demo
cowsay Hello World!
```
```
 ____________
< Hello World! >
 --------------
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||
```

