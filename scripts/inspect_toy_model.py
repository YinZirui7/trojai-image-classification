from pathlib import Path
import json

import cv2
import matplotlib.pyplot as plt
import torch


project_root = Path(__file__).resolve().parents[1]
thesis_root = project_root.parent

model_dir = thesis_root / "trojai-example" / "model" / "id-00000002"
examples_dir = model_dir / "clean-example-data"
output_dir = project_root / "outputs"
output_dir.mkdir(exist_ok=True)

image_path = sorted(examples_dir.glob("*.jpg"))[0]
label_path = image_path.with_suffix(".json")
model_path = model_dir / "model.pt"

true_class = json.loads(label_path.read_text(encoding="utf-8"))

image_bgr = cv2.imread(str(image_path))
if image_bgr is None:
    raise FileNotFoundError(f"Could not read image: {image_path}")

image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

input_tensor = (
    torch.from_numpy(image_rgb)
    .permute(2, 0, 1)
    .float()
    .div(255.0)
    .unsqueeze(0)
)

model = torch.load(model_path, map_location="cpu")
model.eval()

with torch.no_grad():
    logits = model(input_tensor)
    probabilities = torch.softmax(logits, dim=1)
    confidence, predicted_class = probabilities.max(dim=1)

predicted_class = predicted_class.item()
confidence = confidence.item()

result_path = output_dir / "toy_prediction.png"

plt.figure(figsize=(7, 6))
plt.imshow(image_rgb)
plt.axis("off")
plt.title(
    f"True class: {true_class} | Predicted class: {predicted_class}\n"
    f"Confidence: {confidence:.2%}"
)
plt.tight_layout()
plt.savefig(result_path, dpi=150, bbox_inches="tight")
plt.show()

print(f"Image: {image_path.name}")
print(f"Input shape: {tuple(input_tensor.shape)}")
print(f"Logits shape: {tuple(logits.shape)}")
print(f"True class: {true_class}")
print(f"Predicted class: {predicted_class}")
print(f"Confidence: {confidence:.6f}")
print(f"Saved visualization: {result_path}")