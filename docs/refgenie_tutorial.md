
bulker activate databio/refgenie:0.7.0
wget ftp://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/000/786/075/GCA_000786075.2_hs38d1/GCA_000786075.2_hs38d1_genomic.fna.gz -O hs38d1.fna.gz
refgenie init -c refgenie.yaml
refgenie build -c refgenie.yaml -g hs38d1 -a fasta --fasta hs38d1.fna.gz


<!-- Need to make pypiper work inside bulker environments somehow...
I guess the real problem is if pypiper is running within a container, then any of its executed commands also run inside that container.
 -->