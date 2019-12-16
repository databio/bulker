# Disabling user or network mapping


The default bulker templates set the container user to the active user, and map the container network to match the host network. This works well for many images, but there are a few that don't play nicely with these run-time settings. So, for these finicky containers, you can turn off the user mapping and network mapping with `no_user` and `no_network` attributes, like in this example:

```
  - command: rstudio-server
    docker_image: waldronlab/bioconductor:release
    docker_command: " "
    no_user: True
    no_network: True
```

If you specify these attributes, then the user map and/or the network map will be left off the `docker run` template for this image only.