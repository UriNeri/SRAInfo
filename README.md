# SRAInfo
Easy-to-use python script that takes a list/table with SRA accessions and returns a table with metadata

FireLab_SRAInfoFinder version ah00 11-18-22

Extracts basic information about a set of SRA accessions, starting with accession number



-> Basic Syntax

    python SRAInfo##.py SRAListFile

Where SRAListFile is a simple text file with one tab-delimited entry per line that contains a SRR/ERR/DRR accession number (alternative: you can list individual SRR#s on command line) 



-> Advanced Syntax

    python SRAInfo##.py SRAListFile <parameter1>=<value1>  <parameter2>=<value2> ...

  This syntax allows setting of a number of optional parameters



-> Output

   Output is a tab-delimited text file, each column having one attribute for a given SRA archive



-> Operation

   SRAInfoFinder grabs metadata in real time from the NCBI website

   The retrieval is very sensitive to the way NCBI display is set up

   So the program (in particular the "boundingtext1" dictionary will need to be updated as the formats for display change

   There are some SRA entries where the information is not correctly parsed

   SRAInfoFinder can hang due to NCBI server issues.



-> Optional Parameters <and defaults>

   idcolumn=<0>      Which column in the input contains the SRR/DRR/ERR id

   threads=<16>      How many threads to dedicate to the program 

   MaxLines1=<all>   Limits the number of lines processed from input file (includes header line) 

   delimiter=<'\r'>  Delimiter between lines in output

   report=<100>      How often to report progress (100 provides a report every 100 reads)

   outfile=<>        Output file name will be assigned automatically but can be overridden

   terminal=<true/false>       Provides additional (verbose) output to the terminal

