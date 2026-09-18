import argparse
import json
from pathlib import Path

import cv2
import torch


parser = argparse.ArgumentParser(
    description="Evaluate clean accuracy for a TrojAI model."
)
parser.add_argument(
    "--model-dir",
    type=Path,
    required=True,
    help="Directory containing model.pt and clean-example-data.",
)
args = parser.parse_args()

MODEL_DIR = args.model_dir
MODEL_PATH = MODEL_DIR / "model.pt"
CLEAN_DATA_DIR = MODEL_DIR / "clean-example-data"

image_paths = sorted(
    CLEAN_DATA_DIR.glob("*.jpg"),
    key=lambda path: int(path.stem),
)

if not image_paths:
    raise ValueError(f"No JPG images found in: {CLEAN_DATA_DIR}")

model = torch.load(MODEL_PATH, map_location="cpu")
model.eval()

correct_count = 0

with torch.no_grad():
    for image_path in image_paths:
        label_path = image_path.with_suffix(".json")

        with label_path.open("r", encoding="utf-8") as label_file:
            true_label = json.load(label_file)

        image_bgr = cv2.imread(str(image_path), cv2.IMREAD_COLOR)

        if image_bgr is None:
            raise ValueError(f"Could not read image: {image_path}")

        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

        image_tensor = torch.as_tensor(image_rgb, dtype=torch.uint8)
        image_tensor = image_tensor.permute(2, 0, 1)
        image_tensor = image_tensor.to(torch.float32) / 255.0
        image_tensor = image_tensor.unsqueeze(0)

        logits = model(image_tensor)
        predicted_label = logits.argmax(dim=1).item()

        is_correct = predicted_label == true_label
        correct_count += int(is_correct)

        print(
            f"{image_path.name}: "
            f"predicted={predicted_label}, "
            f"true={true_label}, "
            f"correct={is_correct}"
        )

total_count = len(image_paths)
clean_accuracy = correct_count / total_count

print(f"\nCorrect predictions: {correct_count}/{total_count}")
print(f"Clean Accuracy: {clean_accuracy:.2%}")