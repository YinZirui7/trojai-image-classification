# sep2022 Example-Image Evaluation

## Scope

This record summarizes evaluation results for the locally available models from the NIST TrojAI `image-classification-sep2022` dataset.

The evaluation used only the example images included in each local model directory. These results do not represent performance on the complete test dataset or generalization to unseen images.

Evaluation session: 2026-09-25 to 2026-09-26.

## Metrics

- Clean Accuracy: the proportion of clean example images for which the predicted label equals the ground-truth label.
- Attack Success Rate (ASR): the proportion of poisoned example images for which the predicted label equals the attack target label stored in the corresponding JSON file.
- N/A: poisoned example data was not available or the metric was not applicable for that clean model.

## Results

| Model | Configuration | Architecture | Triggers | Clean Accuracy | Poisoned Examples | ASR | Target Labels |
|---|---|---|---:|---:|---:|---:|---|
| id-00000140 | Poisoned | mobilenet_v2 | 2 | 20/20 (100%) | 40 | 40/40 (100%) | 13, 40 |
| id-00000141 | Poisoned | vit_base_patch32_224 | 1 | 20/20 (100%) | 20 | 20/20 (100%) | 1 |
| id-00000142 | Poisoned | mobilenet_v2 | 2 | 20/20 (100%) | 40 | 40/40 (100%) | 20, 40 |
| id-00000143 | Clean | mobilenet_v2 | 0 | 20/20 (100%) | N/A | N/A | N/A |
| id-00000144 | Clean | resnet50 | 0 | 20/20 (100%) | N/A | N/A | N/A |
| id-00000145 | Clean | resnet50 | 0 | 20/20 (100%) | N/A | N/A | N/A |
| id-00000146 | Poisoned | mobilenet_v2 | 2 | 20/20 (100%) | 31 | 31/31 (100%) | 8, 16 |
| id-00000147 | Clean | vit_base_patch32_224 | 0 | 20/20 (100%) | N/A | N/A | N/A |
| id-00000148 | Poisoned | resnet50 | 2 | 20/20 (100%) | 40 | 40/40 (100%) | 45, 84 |
| id-00000149 | Poisoned | mobilenet_v2 | 4 | 20/20 (100%) | 80 | 80/80 (100%) | 2, 3, 5, 26 |

For `id-00000140`, the 40 poisoned examples were distributed as follows:

- Target label 13: 20 samples
- Target label 40: 20 samples

## Validation Notes

### Poisoned-label semantics

For the six locally available poisoned models (`id-00000140`, `id-00000141`, `id-00000142`, `id-00000146`, `id-00000148`, and `id-00000149`), the unique integer labels stored in `poisoned-example-data` JSON files matched the `target_class` values recorded in each model's `config.json`.

This supports interpreting the poisoned-example JSON integer as the attack target label for the inspected local models. It does not by itself establish that every TrojAI model or dataset split uses the same structure.

### Image preprocessing

The preprocessing implementation was compared with `example_trojan_detector.py` from the official `trojai-example` repository. Both implementations perform OpenCV image loading, BGR-to-RGB conversion, HWC-to-CHW conversion, conversion from `uint8` values to floating-point values in `[0, 1]`, and addition of the batch dimension.

The official example uses `torchvision.transforms.ConvertImageDtype(torch.float)`, while the local evaluation scripts use `float32 / 255.0`. No additional resize or mean/standard-deviation normalization was present in the inspected official inference path.

## Interpretation Limitations

A result of 100% does not by itself prove that the evaluation implementation is completely correct.

The results apply only to the local example images supplied with each model. They do not represent evaluation on the full dataset and do not evaluate the LoRA as Oracle backdoor-detection method.

The model configuration fields were read from the nested `py/state` object in each `config.json`.

The dataset models, model weights, and example images are stored outside this Git repository and are not included in version control.