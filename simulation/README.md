# Simulation - HashAge/ SkAge
## Description
This simulation script evaluates HashAge/ SkAge against their counterparts HashPipe/ CMS.

## Usage
### Preprocessing
Before getting started, you will need to preprocess your packet captures. You may refer to the instructions [here](Preprocessing.md).

### Running the experiments
The evaluation script provides various arguments that can be passed to the program for each experiment run. You may run 
`./evaluation.py --help` to check the available arguments as well as the default values.

An example is provided as follows:
```
./evaluate.py --algorithm hashpipe --aging-factor --num-counters 12240 --num-stages 6 --dataset-path data/IMC2010DC1/ --window-size 5
```
We will be using this as a running example.

### Getting the results
#### Where are the results?
Upon completion of an experiment, the results can be found under the corresponding dataset folder. For this example, it will be `data/IMC2010DC1/results/`.

A different folder will be created for every different algorithm configuration, e.g., `data/IMC2010DC1/results/HashPage.6.12240/`.

For each *.dataset file, snapshots are captured at every second to ease further evaluation later.
```
 01.dataset
│   ├── 1458219601
│   ├── 1458219602
│   ├── 1458219603
│   ├── 1458219604
│   ├── 1458219605
...
```

#### Processing the results
To evaluate the results, various tools can be found under `tools/`. 

##### Evaluating the results against the groundtruth (Sequence matters)
1. `process_results.py` is used for evaluating the results against the groundtruth. See `process_results.py --help`  for the available arguments.
2. `graphs.py` is used to generate the graphs in Figure 3.
3. `analyse_results.py` is used to generate an intermediate summary of the results. (It is recommended to sort the result files according to the algorithms). Then, `parse_results_to_csv.py` should be used to convert the output to a CSV for further processing.
4. Depending on the situation, if there's the need, `tranpose_csv_lookback.py` and `transpose_csv_memory.py` are used to 
transpose the output of `parse_results_to_csv.py` to ease the graph plotting process (Figure 4, 5, 6, 7).

## Extending the Program
This program was designed with modularity in mind, hence, it can be easily extended with any other heavy hitter algorithms if necessary through the high-level APIs defined in `algorithms/algorithm.py`. You may refer to HashPipe/ CMS (or even SS)'s implementation on how the APIs of `algorithms/algorithm.py` are consumed. 