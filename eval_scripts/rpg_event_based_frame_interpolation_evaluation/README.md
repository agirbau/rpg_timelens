# TimeLens Frame Interpolation Evaluation Toolbox

## Installation

This installation was tested with Python 3.7. To install the dependencies call 

    pip install -r requirements.txt

## Data format

The toolbox requires the following results folder format

```
└── results_folder
    ├── sequence_0
    │   ├── GT               <------ this is where ground truth images are stored
    │   │   ├── 000000.png
    │   │   ├── 000001.png
    │   │   └── ...
    │   ├── method_0          <------ this is the first method to be evaluated
    │   │   ├── 000000.png
    │   │   ├── 000001.png
    │   │   └── ...
    │   ├── method_1
    │   │   ├── 000000.png
    │   │   ├── 000001.png
    │   │   └── ...
    │   └── ...
    ├── sequence_1
    │   ├── GT
    │   │   ├── 000000.png
    │   │   ├── 000001.png
    │   │   └── ...
    │   └── ...
    └── ...
```

## Evaluation

Evaluation is performed by calling

    python quantitative_evaluation.py path/to/results_folder --num_processes 4
                                                             --output_file output.yaml
                                                             --num_skips 3

Here `--num_processes` sets the number of processes used (the code runs in parallel to save computation time).
The path to the output file is set with `--output_file` and the number of skips considered (in our case 4 and 7 for the HS-ERGB dataset)
is set with `--num_skips`. For example, `--num_skips 3` skips the first and every fourth image for evaluation, since these are considered keyframes.

The output file contains a summary across the different datasets (`sequence_0`, `sequence_1`, ...) and different methods (`method_0`, `method_1`, ...).


