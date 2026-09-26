import argparse
import csv
import json
from pathlib import Path

import cv2
import torch


IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg")


def find_images(data_dir):
    image_paths = []

    for extension in IMAGE_EXTENSIONS:
        image_paths.extend(data_dir.glob(f"*{extension}"))

    def sort_key(path):
        try:
            return 0, int(path.stem)
        except ValueError:
            return 1, path.stem

    return sorted(image_paths, key=sort_key)


def load_label(image_path):
    label_path = image_path.with_suffix(".json")

    if not label_path.is_file():
        raise FileNotFoundError(f"Missing label file: {label_path}")

    with label_path.open("r", encoding="utf-8") as label_file:
        label = json.load(label_file)

    if not isinstance(label, int):
        raise ValueError(f"Label is not an integer: {label_path}")

    return label


def prepare_image(image_path):
    image_bgr = cv2.imread(str(image_path), cv2.IMREAD_UNCHANGED)

    if image_bgr is None:
        raise ValueError(f"Could not read image: {image_path}")

    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

    image_tensor = torch.as_tensor(image_rgb, dtype=torch.uint8)
    image_tensor = image_tensor.permute(2, 0, 1)
    image_tensor = image_tensor.to(torch.float32) / 255.0
    image_tensor = image_tensor.unsqueeze(0)

    return image_tensor


def predict(model, image_path):
    image_tensor = prepare_image(image_path)
    logits = model(image_tensor)
    return logits.argmax(dim=1).item()


def evaluate_clean(model, model_dir):
    clean_data_dir = model_dir / "clean-example-data"
    image_paths = find_images(clean_data_dir)

    if not image_paths:
        return {
            "clean_status": "missing_data",
            "clean_correct": "",
            "clean_total": 0,
            "clean_accuracy": "",
            "clean_error": f"No images found in {clean_data_dir}",
        }

    correct_count = 0

    try:
        with torch.no_grad():
            for image_path in image_paths:
                true_label = load_label(image_path)
                predicted_label = predict(model, image_path)
                correct_count += int(predicted_label == true_label)

        total_count = len(image_paths)

        return {
            "clean_status": "success",
            "clean_correct": correct_count,
            "clean_total": total_count,
            "clean_accuracy": correct_count / total_count,
            "clean_error": "",
        }
    except Exception as error:
        return {
            "clean_status": "failed",
            "clean_correct": "",
            "clean_total": len(image_paths),
            "clean_accuracy": "",
            "clean_error": str(error),
        }


def evaluate_asr(model, model_dir, poisoned):
    if not poisoned:
        return {
            "asr_status": "not_applicable",
            "asr_success": "",
            "asr_total": "",
            "attack_success_rate": "",
            "target_statistics": "",
            "asr_error": "",
        }

    poisoned_data_dir = model_dir / "poisoned-example-data"
    image_paths = find_images(poisoned_data_dir)

    if not image_paths:
        return {
            "asr_status": "missing_data",
            "asr_success": "",
            "asr_total": 0,
            "attack_success_rate": "",
            "target_statistics": "",
            "asr_error": f"No images found in {poisoned_data_dir}",
        }

    success_count = 0
    target_statistics = {}

    try:
        with torch.no_grad():
            for image_path in image_paths:
                target_label = load_label(image_path)
                predicted_label = predict(model, image_path)
                is_success = predicted_label == target_label

                if target_label not in target_statistics:
                    target_statistics[target_label] = {
                        "success": 0,
                        "total": 0,
                    }

                success_count += int(is_success)
                target_statistics[target_label]["success"] += int(is_success)
                target_statistics[target_label]["total"] += 1

        total_count = len(image_paths)

        return {
            "asr_status": "success",
            "asr_success": success_count,
            "asr_total": total_count,
            "attack_success_rate": success_count / total_count,
            "target_statistics": json.dumps(
                target_statistics,
                sort_keys=True,
            ),
            "asr_error": "",
        }
    except Exception as error:
        return {
            "asr_status": "failed",
            "asr_success": "",
            "asr_total": len(image_paths),
            "attack_success_rate": "",
            "target_statistics": "",
            "asr_error": str(error),
        }


def read_config(model_dir):
    config_path = model_dir / "config.json"

    if not config_path.is_file():
        raise FileNotFoundError(f"Missing config file: {config_path}")

    with config_path.open("r", encoding="utf-8") as config_file:
        config = json.load(config_file)

    state = config.get("py/state")

    if not isinstance(state, dict):
        raise ValueError(f"Missing py/state object in: {config_path}")

    poisoned = state.get("poisoned")

    if not isinstance(poisoned, bool):
        raise ValueError(f"Invalid poisoned field in: {config_path}")

    return state


def failed_result(model_name, error):
    return {
        "model": model_name,
        "poisoned": "",
        "architecture": "",
        "num_triggers": "",
        "model_status": "failed",
        "model_error": str(error),
        "clean_status": "not_run",
        "clean_correct": "",
        "clean_total": "",
        "clean_accuracy": "",
        "clean_error": "",
        "asr_status": "not_run",
        "asr_success": "",
        "asr_total": "",
        "attack_success_rate": "",
        "target_statistics": "",
        "asr_error": "",
    }


def evaluate_model(model_dir):
    print(f"\nEvaluating {model_dir.name}...")

    try:
        state = read_config(model_dir)
        poisoned = state["poisoned"]
        model_path = model_dir / "model.pt"

        if not model_path.is_file():
            raise FileNotFoundError(f"Missing model file: {model_path}")

        model = torch.load(model_path, map_location="cpu")
        model.eval()

        clean_result = evaluate_clean(model, model_dir)
        asr_result = evaluate_asr(model, model_dir, poisoned)

        result = {
            "model": model_dir.name,
            "poisoned": poisoned,
            "architecture": state.get("model_architecture", ""),
            "num_triggers": state.get("num_triggers", ""),
            "model_status": "success",
            "model_error": "",
        }
        result.update(clean_result)
        result.update(asr_result)

        clean_value = result["clean_accuracy"]
        asr_value = result["attack_success_rate"]

        clean_text = (
            f"{clean_value:.2%}"
            if isinstance(clean_value, float)
            else result["clean_status"]
        )
        asr_text = (
            f"{asr_value:.2%}"
            if isinstance(asr_value, float)
            else result["asr_status"]
        )

        print(f"Clean Accuracy: {clean_text}")
        print(f"ASR: {asr_text}")

        del model
        return result

    except Exception as error:
        print(f"Model evaluation failed: {error}")
        return failed_result(model_dir.name, error)


def write_results(results, output_path):
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "model",
        "poisoned",
        "architecture",
        "num_triggers",
        "model_status",
        "model_error",
        "clean_status",
        "clean_correct",
        "clean_total",
        "clean_accuracy",
        "clean_error",
        "asr_status",
        "asr_success",
        "asr_total",
        "attack_success_rate",
        "target_statistics",
        "asr_error",
    ]

    with output_path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


def main():
    parser = argparse.ArgumentParser(
        description="Batch evaluate TrojAI image classification models."
    )
    parser.add_argument(
        "--models-dir",
        type=Path,
        required=True,
        help="Directory containing TrojAI model directories.",
    )
    parser.add_argument(
        "--model-pattern",
        default="id-*",
        help="Glob pattern used to select model directories.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/sep2022_batch_evaluation.csv"),
        help="CSV output path.",
    )
    args = parser.parse_args()

    model_dirs = sorted(
        path
        for path in args.models_dir.glob(args.model_pattern)
        if path.is_dir()
    )

    if not model_dirs:
        raise ValueError(
            f"No model directories matched {args.model_pattern!r} "
            f"in {args.models_dir}"
        )

    print(f"Selected model directories: {len(model_dirs)}")

    results = [
        evaluate_model(model_dir)
        for model_dir in model_dirs
    ]

    write_results(results, args.output)

    print(f"\nEvaluated models: {len(results)}")
    print(f"Results saved to: {args.output.resolve()}")


if __name__ == "__main__":
    main()