## getSeqENA
-- Download sequences from ENA database --


#### Depedencies
- wget (normally found in Linux OS)
- gzip >= v1.6 (normally found in Linux OS)
- Aspera Connect 2 >= v3.6.1 (optional)
- curl (optional)
- [SRA toolkit](https://trace.ncbi.nlm.nih.gov/Traces/sra/sra.cgi?view=software) >= v2.8.2 (optional) (for SRA interaction)
- GNU Awk (optional) (normally found in Linux OS) (for SRA interaction)

#### Input
 To interact directly with ENA, a list of IDs to download needs to be passed to getSeqENA. This can be done through the -l option.

#### Usage

    usage: getSeqENA.py [-h] [--version] -l /path/to/list/ENA_IDs.txt
                        [-o /output/directory/] [-j N]
                        [-a /path/to/asperaweb_id_dsa.openssh]
                        [--downloadLibrariesType PAIRED] [--downloadCramBam]
                        [--downloadInstrumentPlatform ILLUMINA]
                        [--maximumSamples N]
                        [--SRA | --SRAopt]

    Get fastq files from ENA using ENA IDs

    optional arguments:
      -h, --help            show this help message and exit
      --version             Version information

    Required options:
      -l /path/to/list/ENA_IDs.txt, --listENAids /path/to/list/ENA_IDs.txt
                            Path to list containing the ENA_IDs to be downloaded
                            (default: None)

    Facultative options:
      -o /output/directory/, --outdir /output/directory/
                            Path for output directory (default: .)
      -j N, --threads N     Number of threads (default: 1)
      -a /path/to/asperaweb_id_dsa.openssh, --asperaKey /path/to/asperaweb_id_dsa.openssh
                            Tells getSeqENA.py to download fastq files from ENA
                            using Aspera Connect. With this option, the path to
                            Private-key file asperaweb_id_dsa.openssh is provided
                            (normaly found in
                            ~/.aspera/connect/etc/asperaweb_id_dsa.openssh).
                            (default: None)
      --downloadLibrariesType PAIRED
                            Tells getSeqENA.py to download files with specific
                            library layout (default: BOTH)
      --downloadCramBam     Tells getSeqENA.py to also download cram/bam files and
                            convert them to fastq files (default: False)
      --downloadInstrumentPlatform ILLUMINA
                            Tells getSeqENA.py to download files with specific
                            library layout (default: ILLUMINA)
      --maximumSamples N    Tells getSeqENA.py to only download files for N
                            samples (default: None)

    SRA download options (one of the following):
      --SRA                 Tells getSeqENA.py to download reads in fastq format
                            only from NCBI SRA database (not recommended)
                            (default: False)
      --SRAopt              Tells getSeqENA.py to download reads from NCBI SRA
                            if the download from ENA fails

#### Outputs
**run.*.log**
getSeqENA running log file.

**getSeqENA.report.txt**
Report for each sample downloaded, retrieved from ENA data warehouse. It contains the following fields:
- *#sample*
- *run_accession*
- *instrument_platform*
- *instrument_model*
- *library_layout*
- *library_souce*
- *extra_run_accession*
- *nominal_length*
- *read_count*
- *base_count*
- *date_download*

#### Contact

Miguel Machado
<mpmachado@medicina.ulisboa.pt>
