# How to import crates

The *imports* section in the manifest file lets you create *cascading manifests*.


For example, this manifest (`import.yaml`) has an `imports` section that provides registry paths to 2 crates:

```{yaml}
manifest:
  name: demo_import
  imports: 
  - bulker/alpine2:default
  - bulker/demo:default
  commands:
  - command: pi
    docker_image: nsheff/pi
    docker_command: pi
    docker_args: "-i"
```

If you load this manifest, it will merge all the commands from each of these crates (in priority order). This is a really powerful mechanism that lets you define cascading manifests. For example, we could then define yet another manifest that would import this one and add additional commands to it.

This import idea is similar to the `FROM` directive in a Dockerfile, but it's more flexible because you can import from multiple crates, and it's more efficient because it does not duplicate any actual underlying images, it only duplicates the bulker containerized executable files.