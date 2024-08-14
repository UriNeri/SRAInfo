#!/usr/bin/env python -i
# FireLab_SRAInfoFinder version ah00 11-18-22
## Extracts basic information about a set of SRA accessions, starting with accession number
## -  Basic Syntax
## -    python SRAInfo##.py SRAListFile
## -       Where SRAListFile is a simple text file with one tab-delimited entry per line that
## -         contains a SRR/ERR/DRR accession number (alternative: you can list individual SRR#s on command line) 
## -  Advanced Syntax
## -    python SRAInfo##.py SRAListFile <parameter1>=<value1>  <parameter2>=<value2> ...
## -       This syntax allows setting of a number of optional parameters
## -  Output
## -    Output is a tab-delimited text file, each column having one attribute for a given SRA archive
## -  Operation
## -    SRAInfoFinder grabs metadata in real time from the NCBI website
## -    The retrieval is very sensitive to the way NCBI display is set up
## -    So the program (in particular the "boundingtext1" dictionary
## -      will need to be updated as the formats for display change
## -    There are some SRA entries where the information is not correctly parsed
## -    SRAInfoFinder can hang due to NCBI server issues.
## -  Optional Parameters <and defaults>
## -    idcolumn=<0>      Which column in the input contains the SRR/DRR/ERR id
## -    threads=<16>      How many threads to dedicate to the program 
## -    MaxLines1=<all>   Limits the number of lines processed from input file (includes header line) 
## -    delimiter=<'\r'>  Delimiter between lines in output
## -    report=<100>      How often to report progress (100 provides a report every 100 reads)
## -    outfile=<>        Output file name will be assigned automatically but can be overridden
## -    terminal=<true/false>       Provides additional (verbose) output to the terminal
      
## End Help        

def PutURLTextIntoQueue1(accession,url,Queue):
    import urllib.request
    MyText = ''
    try:
        MySite = urllib.request.urlopen(url)
        MyText = str(MySite.read())
    except:
        print()
        print('Retrieval Failure for Accession '+accession)
        print('Continuing without metadata for that entry in output table')
    Queue.put((accession,MyText))



def main():
    import multiprocess as mp
    from time import sleep, time, strftime, localtime
    import sys
    import os
    def isAnSRA1(s):
        ''' tests if a string is of the format Cs#s where Cs is a string of characters and ##s a string of numbers'''
        for i,c in enumerate(s):
            if not c.isalpha():
                break
        if (i>0) and (i<len(s)-1) and s[i:].isdigit():
            return True
        return False
    def FileInfo1(FileID):
        if type(FileID)==str:
            Fn1=FileID
        else:
            Fn1=FileID.name
        s11=os.stat(Fn1)
        return '\n    '.join([Fn1,
                          'Path='+os.path.dirname(os.path.abspath(Fn1)),
                            'Size='+str(s11[6]),
                            'Created='+strftime("%m_%d_%y_at_%H_%M_%S",localtime(s11[9]))+' Modified='+strftime("%m_%d_%y_at_%H_%M_%S",localtime(s11[8]))])    
    def MyLink1(Accession):
        return 'https://www.ncbi.nlm.nih.gov/sra/?term='+Accession   
    IDColumn1 = 'default' ## (idcolumn=) Which column in the input contains the SRR/DRR/ERR id
    Threads1 = 16 ## (threads=) How many threads to dedicate to the program (in this case mainly IO intensive; setting this too high may generate resistance from the NCBI server)
    MaxLines1 = 0 ##999999 ## (maxlines=) Limits the number of lines processed in the input file (header line will be included in the count, so n+1 if you have a header line)
    delimiter1 = '\r' ## (delimiter=) Delimiter between lines in output
    ReportGranularity1 = 100 ## (reportgranularity=) How often to report progress (100 provides a report every 100 reads)
    InFileName1 = 'No File Name Specified' ## (infile=) A tab delimited text file where each line contains information from one SRA entry
    OutputFileName1 = 'default' ## (outfile=) An output file that will have the information from the input
    Terminal1 = 'default' ## (terminal= Provide verboase output to the terminal)
    vnow = strftime("D_%m_%d_%y_T_%H_%M_%S",localtime())
    boundingtext1 = {'Study':('>Study: <span>','<'),
                 'Sample':('>Sample: <span>','<'),
                 'Organism':('>Organism: <span>','<'),
                 'RunYield':('</b><br />','<'),
                 'Abstract':('Abstract</span></a><div class="expand-body">','<'),
                 'Submitted_By':('>Submitted by: <span>','<'),
                 'BioProjectID':('"Link to BioProject">','<'),
                 'SRA_StudyID':('"Link to SRA Study">','<'),
                 'SRA_BioSampleID':('"Link to BioSample">','<')}

    HeaderLine1 = False
    AdHockSRAList1 = []
    ## each entry is an attribute name (as the key) followed by a 2-ple with
    ##  0.  some unique text that always precedes the noted attribute and
    ##  1.  some unique text that always follows the  noted attribute.  
    for a0 in sys.argv[1:]:
        if a0.startswith('=') or a0.endswith('='):
            print('Encountered equals sign in unexpected position in command line; syntax should be free of spaces')
            exit()
        if a0.startswith('h') or a0.startswith('-h'):
            print()
            print('######################')
            print('SRA Info Finder-- get the lowdown on your favorite list of SRA entries')
            print('######################')
            print()
            for L1 in open(sys.argv[0],mode='rt').readlines():
                if L1.startswith('## End Help'): break
                if L1.startswith('##'):
                    print(L1.strip('#').strip())
            print('######################')
            print()
            exit()
        if not('=' in a0):
            if a0.isdigit():
                MaxLines1 = int(a0)
            elif os.path.isfile(a0.strip()): 
                InFileName1 = a0.strip()
            else:
                AdHockSRAList1 += a0.split(',')
                if Terminal1=='default':
                    Terminal1 = "+"       
        else:
            s1 = a0.split('=')[0].strip()
            v1 = a0.split('=')[1].strip()
            if s1.lower().startswith('idcolumn'):
                IDColumn1 =  int(v1)
            elif s1.lower().startswith('thread'):
                Threads1 =  int(v1)
            elif s1.lower().startswith('report'):
                ReportGranularity1 =  int(v1)
            elif s1.lower().startswith('max'):
                MaxLines1 =  int(v1)
            elif s1.lower().startswith('infile'):
                InFileName1 =  str(v1)        
            elif s1.lower().startswith('outfile'):
                OutputFileName1 =  str(v1)        
            elif s1.lower().startswith('delimit'):
                delimiter1 =  str(v1.strip("'").strip('"'))
            elif s1.lower().startswith('term'):
                if v1.lower().startswith('f'):
                    Terminal1 = "-"
                else:
                    Terminal1 = "+"
                    
                Terminal1 =  str(v1.strip("'").strip('"'))        
    NullInfo1 = ['' for h1 in boundingtext1]
    if OutputFileName1 == 'default':
        OutputFileName1 = "SRAInfo_"+InFileName1.split('.')[0]+'_'+vnow+'.tsv'
    t0 = time()

    TaskHeader1 = '\n-FireLAB SRAInfoFinder Creating '+OutputFileName1+'\n'
    TaskHeader1 +=  '  CommandLine:\n    '+'\n    '.join(sys.argv)+'\n'
    print(InFileName1)
    if os.path.isfile(InFileName1) and (InFileName1 != 'No File Name Specified'): TaskHeader1 +=  '  Input File:\n    '+FileInfo1(InFileName1)+'\n'
    TaskHeader1 +=  '  SRAInfoFinder_Version:\n    '+FileInfo1(sys.argv[0])+'\n'
    TaskHeader1 +=  '  PythonVersion:\n    '+'\n    '.join(sys.version.splitlines())+'\n'
    AbbrevHeader1 = ''.join(TaskHeader1.splitlines()[:-1])+'<!--SRAInfoFinderTableHeader-->'  ##ending with 'TableHeader-->' identifies a line as a row of table headers
    print(TaskHeader1)
    InLines1  = AdHockSRAList1
    if InFileName1!='No File Name Specified' and os.path.isfile(InFileName1):
        InLines1  += open(InFileName1, mode='rt').readlines()
    if IDColumn1=='default':
        IDColumn1 = 0
        if len(InLines1)==0:
            print("No input data found in file "+InFileName1)
            exit()
        elif len(InLines1)==1:
            TestLine1 = InLines1[0].split('\t')
        else:
            TestLine1 = InLines1[1].split('\t')
        for j1 in range(len(TestLine1)):
            if TestLine1[j1][:3] in ['SRR','ERR','DRR'] and len(TestLine1[j1])>3 and TestLine1[j1][3:].isdigit():
                IDColumn1 = j1
                break
    Header0 = '\t'.join(boundingtext1.keys())+'\tNCBI_Link (SRAList:'+os.path.basename(InFileName1)+' AccessionTime:'+vnow+')'
            
    FileLineToSRA1 = {} ## Keys are line numbers, values are SRA IDs
    SRAToMetaData1 = {} ## Keys are SRA IDs, values are Metadata Lines
    mp.set_start_method('spawn')
    if not(MaxLines1):
        MaxLines1 = len(InLines1)
    MyQueue1 = mp.Queue(Threads1)
    AllProcesses1 = []
    for i1 in range(MaxLines1):
        L1 = InLines1[i1].strip().split('\t')
        if i1 == 0: lL1 = len(L1)
        Accession1 = L1[IDColumn1]
        FileLineToSRA1[i1] = Accession1
        if not(Accession1 in SRAToMetaData1):
            if isAnSRA1(Accession1):
                SRAToMetaData1[Accession1] = ''
                MyURL = MyLink1(Accession1)
                AllProcesses1.append(mp.Process(target=PutURLTextIntoQueue1, args=(Accession1,MyURL,MyQueue1)))
            else:
                SRAToMetaData1[Accession1] = Header0
                if i1==0:
                    HeaderLine1 = True
    TotalProcesses1 = len(AllProcesses1)
    OngoingProcesses1 = []
    for NextProcess1 in range(min(Threads1,TotalProcesses1)):
        OngoingProcesses1.append(AllProcesses1[NextProcess1])
        OngoingProcesses1[-1].start()
    NextProcess1 += 1
    while OngoingProcesses1:
        for i,p1 in enumerate(OngoingProcesses1):            
            if not(p1.is_alive()):
                OngoingProcesses1[i].join()
                OngoingProcesses1[i].close()
                if NextProcess1<TotalProcesses1:
                    if NextProcess1%ReportGranularity1==0:
                        print("-Starting SRA Entry "+str(NextProcess1)+' at t=%.3f'%(time()-t0)+'s')
                    OngoingProcesses1[i] = AllProcesses1[NextProcess1]
                    OngoingProcesses1[i].start()
                    NextProcess1 += 1
                else:
                    del(OngoingProcesses1[i])
                acccession0,MyText0 = MyQueue1.get()
                ThisInfo = ['' for h1 in boundingtext1]
                for i1,h1 in enumerate(boundingtext1.keys()):
                    s1 = boundingtext1[h1][0]
                    e1 = boundingtext1[h1][1]
                    if s1 in MyText0:
                        NextNubbin = MyText0.split(s1)[1]
                        if NextNubbin.startswith('<a'):
                            NextNubbin = NextNubbin.split('>',1)[-1]
                            NextNubbin = NextNubbin.split('</a>')[0]
                        NextNubbin = NextNubbin.split(e1)[0]                        
                    else:
                        NextNubbin = ''
                    ThisInfo[i1] = NextNubbin
                SRAToMetaData1[acccession0] = '\t'.join(ThisInfo)
        sleep(0.001)
    OutFile1 = open(OutputFileName1, mode='w')
    if not(HeaderLine1):
        NewHeader1 = ['' for j1 in range(lL1)]
        NewHeader1[IDColumn1] = 'SRA_ID'
        OutFile1.write('\t'.join(NewHeader1)+'\t'+Header0+delimiter1)
    for i11 in range(MaxLines1):
        OutLine11 = InLines1[i11].strip().split('\t')
        Accession11 = OutLine11[IDColumn1].strip()
        OutFile1.write('\t'.join(OutLine11)+'\t'+SRAToMetaData1[Accession11]+'\t'+MyLink1(Accession11)+delimiter1)
        if Terminal1 == '+':
            print('Accession: '+Accession11)
            for h1,v1 in zip(Header0.split('\t'),SRAToMetaData1[Accession11].split('\t')):
                print(h1+': '+v1)
            print()
    OutFile1.close()
    print("-Finishing writing "+OutputFileName1+' at t=%.3f'%(time()-t0)+'s')
    print("-Total Lines Written "+str(MaxLines1))
if __name__ == '__main__':
    main()
    
## Copywrite 2022 Andrew Fire and Stanford University, All Rights Reserved
