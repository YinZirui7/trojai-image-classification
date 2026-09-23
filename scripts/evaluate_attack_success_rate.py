import argparse
import json
from pathlib import Path

import cv2
import torch


parser = argparse.ArgumentParser(
    description="Evaluate attack success rate for a TrojAI model."
)
parser.add_argument(
    "--model-dir",
    type=Path,
    required=True,
    help="Directory containing model.pt and poisoned-example-data.",
)
args = parser.parse_args()

MODEL_DIR = args.model_dir
MODEL_PATH = MODEL_DIR / "model.pt"
POISONED_DATA_DIR = MODEL_DIR / "poisoned-example-data"

image_paths = sorted(
    POISONED_DATA_DIR.glob("*.png"),
    key=lambda path: int(path.stem),
)

if not image_paths:
    raise ValueError(f"No PNG images found in: {POISONED_DATA_DIR}")

model = torch.load(MODEL_PATH, map_location="cpu")
model.eval()

success_count = 0
total_count = len(image_paths)
target_statistics = {}

with torch.no_grad():
    for image_path in image_paths:
        label_path = image_path.with_suffix(".json")

        with label_path.open("r", encoding="utf-8") as label_file:
            target_label = json.load(label_file)

        if target_label not in target_statistics:
            target_statistics[target_label] = {"success": 0, "total": 0}

        image_bgr = cv2.imread(str(image_path), cv2.IMREAD_UNCHANGED)

        if image_bgr is None:
            raise ValueError(f"Could not read image: {image_path}")

        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

        image_tensor = torch.as_tensor(image_rgb, dtype=torch.uint8)
        image_tensor = image_tensor.permute(2, 0, 1)
        image_tensor = image_tensor.to(torch.float32) / 255.0
        image_tensor = image_tensor.unsqueeze(0)

        logits = model(image_tensor)
        predicted_label = logits.argmax(dim=1).item()

        is_success = predicted_label == target_label

        success_count += int(is_success)
        target_statistics[target_label]["success"] += int(is_success)
        target_statistics[target_label]["total"] += 1

        print(
            f"{image_path.name}: "
            f"predicted={predicted_label}, "
            f"target={target_label}, "
            f"success={is_success}"
        )

attack_success_rate = success_count / total_count

print(f"\nAttack Success Rate: {attack_success_rate:.2%}")
for target_label, stats in target_statistics.items():
    success_rate = stats["success"] / stats["total"] if stats["total"] > 0 else 0
    print(f"Target Label {target_label}: {success_rate:.2%}")