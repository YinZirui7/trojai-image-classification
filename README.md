# TrojAI Image Classification

Bachelor's thesis project at the University of Szeged on Trojan/backdoor detection in pretrained image classification models.

The project focuses on reproducing and evaluating **LoRA as Oracle** using the NIST TrojAI `image-classification-sep2022` dataset.

## NIST TrojAI Challenge

- Challenge: `image-classification-sep2022`
- Task: Determine whether a pretrained image classification model contains a Trojan backdoor
- Model architectures encountered locally: ResNet-50, MobileNetV2, and ViT
- Detector output: Probability that the inspected model is poisoned

## Research Objectives

1. Understand the NIST TrojAI dataset and evaluation procedure.
2. Implement Clean Accuracy and Attack Success Rate evaluation.
3. Reproduce the LoRA as Oracle method.
4. Apply LoRA as Oracle to the TrojAI `image-classification-sep2022` dataset.
5. Evaluate the method across clean and poisoned models.

## Current Status

Completed:

- Configured the local TrojAI environment.
- Reproduced the official NIST example inference.
- Implemented Clean Accuracy evaluation.
- Implemented Attack Success Rate evaluation.
- Added command-line arguments for selecting model directories.
- Tested the evaluation scripts on locally available sep2022 models.
- Verified that the image preprocessing used by the scripts matches the inspected official NIST example implementation.
- Recorded example-image evaluation results for models `id-00000140` through `id-00000149`.

Planned:

- Further verify preprocessing requirements across model architectures.
- Further verify poisoned-example JSON label semantics.
- Implement batch evaluation across multiple model directories.
- Save batch evaluation results to structured output files.
- Reproduce LoRA as Oracle.
- Adapt LoRA as Oracle to `image-classification-sep2022`.

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

The script loads the model on CPU, evaluates PNG, JPG, and JPEG images in `clean-example-data`, reads their corresponding JSON labels, and reports the number of correct predictions and Clean Accuracy.

## Attack Success Rate Evaluation

Run the evaluation script from the repository root:

```powershell
python scripts/evaluate_attack_success_rate.py --model-dir "C:\path\to\model\id-XXXXXXXX"
```

The specified model directory must contain:

```text
model.pt
poisoned-example-data/
```

The current implementation reads each poisoned image and its corresponding JSON file, treats the integer stored in the JSON file as the attack target label, and counts an attack as successful when the predicted label equals that target label.

The script reports the overall Attack Success Rate and per-target-label results.

If poisoned example data is unavailable, the result must be treated as not applicable or missing data rather than as an ASR of zero.

## Evaluation Results

Detailed example-image evaluation results for the locally available models are recorded in:

[`results/sep2022_example_evaluation.md`](results/sep2022_example_evaluation.md)

These results apply only to the example images included in the local model directories. They do not represent performance on the complete dataset, generalization to unseen images, or completion of the LoRA as Oracle backdoor-detection method.

A result of 100% does not by itself prove that the evaluation implementation is completely correct.

## Data

NIST datasets, pretrained models, and example images are not stored in this repository. They remain outside the Git repository because of their size and licensing or distribution requirements.

The official NIST repository is used only as a source of data and reference code. This project does not modify the official repository.

## Hardware

Small-scale development and evaluation can be performed locally on CPU. GPU resources may be used later for larger experiments and LoRA training.

## Author

Yin Zirui