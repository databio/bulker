# How to inspect a crate

When you activate a crate, sometimes you'd like to know what commands are available in that crate. Starting with bulker version 0.5.0, you can now use `bulker insepct`. When run from within an activate crate, `bulker inspect` will display the name of the active crate, and give you a list of commands provided by that crate.

You can also run `bulker insect {registry_path}` to inspect any crate, active or now. For example:

```console
$  bulker inspect bulker/demo
Bulker config: /home/nsheff/env/bulker_config.yaml
Bulker manifest: bulker/demo
Crate path: /home/nsheff/bulker_crates/bulker/demo/default
Available commands: ['fortune', 'cowsay']
```
