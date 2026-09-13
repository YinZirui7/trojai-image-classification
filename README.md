# TrojAI Image Classification

Bachelor's thesis project on Trojan/backdoor detection in pretrained image classification models.

This project uses the NIST TrojAI Round 11 challenge:

- Challenge: `image-classification-sep2022`
- Task: Determine whether a pretrained image classification model contains a Trojan backdoor
- Model architectures: ResNet-50, MobileNetV2, and ViT
- Output: Probability that the inspected model is poisoned

## Research Objectives

1. Understand the NIST TrojAI dataset and evaluation procedure.
2. Reproduce a baseline or existing Trojan detection method.
3. Evaluate the detector across different model architectures and trigger types.
4. Explore lightweight improvements suitable for cross-architecture detection.
5. Compare detection performance using cross-entropy, Brier score, ROC-AUC, and runtime.

## Current Status

The project is currently in the environment setup and official example reproduction stage.

## Environment Setup

Create the Conda environment:

```bash
conda env create -f environment.yml
```

Activate the environment:

```bash
conda activate trojai
```

## Data

The NIST datasets and pretrained models are not stored in this repository because of their size.

- [NIST Round 11 dataset documentation](https://pages.nist.gov/trojai/docs/image-classification-sep2022.html)
- [Official NIST example implementation](https://github.com/usnistgov/trojai-example/tree/image-classification-sep2022)

## Hardware

Small-scale development and testing can be performed on CPU. Full experiments and batch model analysis will use NVIDIA GPU resources.

## Author

Yin Zirui
BSc Computer Science
University of Szeged