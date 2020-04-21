# Dataset Preprocessing Guidelines
## Pre-processing
The guideline is written for pre-processing CAIDA passive traces. Other traffic traces (e.g. IMC2010 DC trace) may require corresponding minor tweaks. 

The following steps are discussed based on the use of CAIDA passive traces.

Taking the CAIDA February 2016 data trace as an example, once downloaded, the directory, `20160218-130000.UTC`, contains
the files with extensions *.pcap.gz, *.pcap.stats and *.times.gz.

> Note: Since we are only interested in the first fifteen minutes of the trace, we will just need to include the PCAPs from the first fifteen minutes into the folder.

#### Step 1: Extracting the PCAPs
Since we are only interested at the PCAPs, hence we will extract all the *.pcap.gz files with `gunzip`.

#### Step 2: Extracting the timestamps and the five-tuple
In order to reduce processing time, instead of replaying the PCAP for every experiment, we will first extract the timestamps and five-tuple values into a *.dataset file. For this, `tools/extract.sh` will get the job done.

Example:
```
# Pass the CAIDA trace's directory as the first argument
./extract.sh 20160218-130000.UTC/
```  

#### Step 3: Verifying the directory structure
Upon completion of Step 1 and Step 2, the following directory structure is expected.
```
├── 20160218-130000.UTC
│   ├── equinix-chicago.dirA.20160218-130000.UTC.anon.pcap
│   ├── equinix-chicago.dirA.20160218-130000.UTC.anon.pcap.dataset
│   ├── equinix-chicago.dirA.20160218-130000.UTC.anon.pcap.stats
│   ├── equinix-chicago.dirA.20160218-130000.UTC.anon.times.gz
│   ├── equinix-chicago.dirA.20160218-130100.UTC.anon.pcap
│   ├── equinix-chicago.dirA.20160218-130100.UTC.anon.pcap.dataset
│   ├── equinix-chicago.dirA.20160218-130100.UTC.anon.pcap.stats
│   ├── equinix-chicago.dirA.20160218-130100.UTC.anon.times.gz
...
```

#### Step 4: Concatenating the PCAPs
In the paper, we use three minute chunks for our evaluations. Hence, it is necessary to concatenate three consecutive PCAPs in the form of *.dataset together.

For the first fifteen minutes, we name the chunks `01.dataset` to `05.dataset`. You should organize the chunks under a new folder, which will be the dataset folder that you will pass to the simulator later. The new directory should look like this.

```
2016CAIDA02/
├── 01.dataset
├── 02.dataset
├── 03.dataset
├── 04.dataset
├── 05.dataset

```

#### Step 5: Getting the groundtruth
For the further evaluation, we will need the groundtruths of the data trace. `tools/extract_groundtruth.py` will process the dataset files (i.e., `0*.dataset`) and extract the groundtruths for every second.

```
groundtruth/
├── 1458219551
├── 1458219552
├── 1458219553
├── 1458219554
├── 1458219555
...
```
#### Step 6: You're ready to go!
Once you are done with the above steps, you may proceed to README.md for simulation instructions.