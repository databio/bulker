# Bulker refgenie tutorial

Here we'll show you how to use bulker together with refgenie to create a bunch of custom refgenie assets without having to install any indexing software.

## Introduction to refgenie

Refgenie manages storage, access, and transfer of reference genome data assets. Among other tasks, it builds aligner indexes for custom genome assemblies. You can [read more about refgenie](http://refgenie.databio.org/en/latest/) if you like, but for now, you can just think of it as a simple pipeline that will run a few commands: `bowtie2-build`, `bwa index`, and `hisat2-build` to produce 3 different genome indexes for a custom fasta file.

You'll need to make sure refgenie is installed for this to work, using some variation of this command:

```{console}
pip install --user refgenie
```

Refgenie is easy to install, but we don't want to have to install all of those individual genome indexing tools, which probably require compiling and are distributed in different places. Luckily, there's a bulker manifest available that groups together all the necessary biocontainers to run a refgenie build pipeline.

## Activating the crate

All we have to do to make those commands available is *load* and *activate* the bulker crate:

```{console}
bulker load databio/refgenie:0.7.0
bulker activate databio/refgenie:0.7.0
```

This populates your environment with the commands necessary for the refgenie pipeline to run.

## Downloading data

We'll need a fasta file to feed to our indexing pipeline. Here we'll use a small decoy sequence so the pipeline doesn't take too long to run the indexes. You could use this same approach to produce indexes for any fasta file


```{console}
wget -O hs38d1.fna.gz \
  ftp://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/000/786/075/GCA_000786075.2_hs38d1/GCA_000786075.2_hs38d1_genomic.fna.gz 
```

## Running the pipeline

Make sure you have a refgenie config file initialized. If not, run these commands:

```console
export REFGENIE="refgenie.yaml"
refgenie init -c $REFGENIE
```

Now, start the refgenie pipeline:

```{console}
refgenie build \
	--genome hs38d1 \
	--fasta hs38d1.fna.gz \
	fasta bowtie2_index bwa_index hisat2_index star_index
```

This command will run `bowtie2-build`, `bwa index`, and `hisat2-build` in succession on your given fasta file. These tools don't have to be installed on your computer; they are included in the bulker crate.

## Using the assets

Now we can use the `refgenie seek` command to retrieve the paths to any of these assets like this:

```{console}
refgenie seek hs38d1/fasta
refgenie seek hs38d1/fasta.fai
refgenie seek hs38d1/fasta.chrom_sizes
refgenie seek hs38d1/bowtie2_index
refgenie seek hs38d1/hisat2_index
refgenie seek hs38d1/bwa_index
```



<!-- Need to make pypiper work inside bulker environments somehow...
I guess the real problem is if pypiper is running within a container, then any of its executed commands also run inside that container.

If you can install the workflow natively, then it will work. If you have to use a container to run the workflow, so the commands run in a container, then things are a bit more complicated... but it can still work, if:

- we enable docker-in-docker, so that the workflow, which is itself executing within a container, can execute commands that run in a container
- we make sure that the workflow container has access to all the bulker executables in PATH. this is a bit tricky; one way to accomplish it is to prepend 'bulker run crate ...' to each command. But this means the workflow has to be aware of bulker. The other way is to prepend the cratepath to the PATH variable *within* the container that is running the workflow. This is also tricky...


 -->

<!-- Problem with this: the biocontainer for bismark doesn't contain bowtie2-build. but it calls this. so, if you're running bismark_genome_preparation in a container, it fails because the bowtie2-build command is not found (even if you have it locally; it has to be in the container as well). So, that's a container problem.
 -->







