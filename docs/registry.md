# How to share a manifest

The bulker registry is located at `hub.bulker.io` and is backed by a GitHub repository that is exposed via GitHub pages. If you want to share a manifest, you can do so by issuing a pull request against this repository.

Alternatively, you could clone this repository and set up your own registry really easily. Just change the `registry_url` key in your bulker config to point to your new Github pages site.


<!-- By default, when you activate a crate, bulker simply prepends the manifest commands to your `PATH`. -->