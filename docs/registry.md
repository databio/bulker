# How to share a manifest with a bulker registry

When you run `bulker load`, you can pass a local manifest using `-f`, or bulker will try to locate the manifest at a remote server called a bulker registry. You can use our registry server or create your own.

## Linking your bulker CLI to a bulker registry

You can link your bulker CLI to a registry by changing the `registry_url` path in your bulker config file:

```console
registry_url: https://hub.bulker.io
```

## The default bulker registry

The default bulker registry is located at [hub.bulker.io](http://hub.bulker.io) and is backed by a GitHub repository that is exposed via GitHub pages. 

### Contributing a manifest to the default registry

To contribute a manifest, you first have to write a manifest yaml file. Consult the [bulker docs on how to write a manifest](http://docs.bulker.io/en/latest/manifest/). After creating your manifest file, it's nice to host it on a server so that you and others can more easily load it with the bulker CLI.  Name your manifest yaml file with the name of the manifest. For a tag, append an understore, so it's `manifestname_tag.yaml`. Manifests in the registry are divided into namespaces, which are represented as subfolders in this repository. So, place your manifest into an appropriate subfolder, and then open a pull request. Once merged, you will be able to pull your manifest with `bulker load namespace/manifestname:tag`.


## Building your own registry


Alternatively, you could set up your own registry really easily in the same way. All you need is a repository on GitHub served via GitHub pages. In fact, you could use any file server. You just have to make sure the manifest files are organized according to the registry structure, which is subfolders for namespaces, and then filenames as *{manifest}_{tag}.yaml*. Then, change the `registry_url` key in your bulker config to point to your new registry file server.


## Multiple registries

Bulker currently doesn't accommodate more than 1 registry, but this is a feature we plan to add as users start to develop more manifests and multiple registries becomes useful.
