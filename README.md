# TrojAI Image Classification

Bachelor's thesis project at the University of Szeged on Trojan/backdoor detection in pretrained image classification models.

The project focuses on reproducing and evaluating **LoRA as Oracle** using the NIST TrojAI `image-classification-sep2022` dataset.

## NIST TrojAI Challenge

- Challenge: `image-classification-sep2022`
- Task: Determine whether a pretrained image classification model contains a Trojan backdoor
- Model architectures: ResNet-50, MobileNetV2, and ViT
- Detector output: Probability that the inspected model is poisoned

## Research Objectives

1. Understand the NIST TrojAI dataset and evaluation procedure.
2. Implement Clean Accuracy and Attack Success Rate evaluation.
3. Reproduce the LoRA as Oracle method.
4. Apply LoRA as Oracle to the TrojAI `image-classification-sep2022` dataset.
5. Analyze the threat model and compare detection performance across models and trigger types.

## Current Status

Completed:

- Configured the local TrojAI environment.
- Reproduced the official NIST example inference.
- Implemented Clean Accuracy evaluation.
- Added a command-line argument for selecting different model directories.
- Tested the script on `id-00000002`.
- Verified image preprocessing against the official NIST implementation.

Next steps:

- Evaluate additional TrojAI models when available.
- Implement Attack Success Rate evaluation.
- Reproduce LoRA as Oracle.
- Apply the method to `image-classification-sep2022`.

## Environment Setup

Create the Conda environment:

```powershell
conda env create -f environment.yml
```

Activate the environment:

```powershell
conda activate trojai
```

## Clean Accuracy Evaluation

Run the evaluation script from the repository root:

```powershell
python scripts/evaluate_clean_accuracy.py --model-dir "C:\path\to\model\id-XXXXXXXX"
```

The specified model directory must contain:

```text
model.pt
clean-example-data/
```

The script loads the model on CPU, evaluates all JPG images in `clean-example-data`, reads their JSON labels, and reports the number of correct predictions and Clean Accuracy.

## Current Test Result

The script was tested on the clean model `id-00000002`:

```text
Correct predictions: 20/20
Clean Accuracy: 100.00%
```

This result applies only to the 20 clean example images included with this model. It does not represent accuracy on the complete Cityscapes dataset, and Clean Accuracy alone cannot determine whether a model contains a backdoor.

## Data

NIST datasets, pretrained models, and example images are not stored in this repository. They must remain outside the Git repository because of their size and licensing or distribution requirements.

The official NIST repository is used only as a source of data and reference code.

## Hardware

Small-scale development and evaluation can be performed locally on CPU. GPU resources may be used later for larger experiments and LoRA training.

## Author

Yin Zirui