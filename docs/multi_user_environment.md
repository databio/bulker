# How to use bulker in a multi-user environment

## Is it possible to share a bulker configuration file in a group?

Yes! In fact, that's a great idea, and this is an intended use case. In fact this is what we do in my lab on our local HPC, because it allows us to have a centralized source for all software, and people don't have to rebuild it. I have a lab script that people can source in their .bashrc, and it sets environment variables for bulker, and a few other things ([divvy](http://divvy.databio.org), [refgenie](http://refgenie.databio.org), *etc.*). I configure bulker to point to a shared location for crates and manifests, so that everyone can use the same bulker crates and singularity containers. For us, this system has effectively replaced the environment modules system on our server, plus it has the advantage that it works across computing systems, si the same setup can be used on multiple servers without problem, unlike server-specific environment modules. And, not only that, I use the same crates on my local desktop with docker.

## What if multiple people try to edit the file at the same time?

One problem in a multi-user environment is the potential for multiple actors to be requesting access to the file at the exact same time. It may seem rare if you haven't experienced this before, but we sometimes run hundreds of jobs, and each one may try to look at the file at the same time. In the middle of this, what if a user was updating a crate or somehow modifying the configuration file, right when a hundred jobs were trying to read the file? It's possible that someone would end up reading a partially written file.

We've solved this issue with a simple file locking system. Before writing the file, bulker creates a file lock. Before reading the configuration file, bulker checks to make sure it's not locked. The file lock only lasts a split second, while the file is being updated, but it ensures that bulker will not try to read the file while another process is writing it. This system prevents clashes and parsing errors that would lead to broken processes.

We use the same system is used for [divvy](http://divvy.databio.org) and [refgenie](http://refgenie.databio.org). This functionality is actually encoded in [yacman](http://github.com/databio/yacman/), our configuration file management software that underlies many of our tools.

So: please do make these things a shared central resource! It's built for that.
