import json
import random
from pathlib import Path

random.seed(42)

output_path = Path("data_up.json")

models = ["Qwen2.5-VL", "LLaVA", "InternVL"]

samples = [
    "Hello I am ",
    "Today I saw ",
    "The image shows ",
]

up_questions = {
    "Hello I am": "What is the model likely to generate after this text?",
    "Today I saw ": "Which next tokens are most likely after this sentence?",
    "The image shows ": "What objects or words can the model continue with?",
}

tokens = [str(i) for i in range(50)]

sentence_templates = [
    "{token} is clearly visible.",
    "{token} appears in the scene.",
    "{token} is near the center.",
    "{token} can be seen in the image.",
    "{token} is part of the scene.",
]


def choose_group(index):
    invalid_indexes = {4, 9, 13, 15, 18, 23, 27, 33, 35, 40, 44, 49}

    if index in invalid_indexes:
        return "invalid"

    return "valid"


def make_completed_sentence(token, num_sentences=6):
    sentences = []

    for _ in range(num_sentences):
        sentence = random.choice(sentence_templates).format(token=token)
        sentences.append(sentence)

    return " ".join(sentences)


def make_precision_recall(index, total):
    cutoff_ratio = index / max(1, total - 1)

    precision_noise = random.uniform(-0.012, 0.012)
    recall_noise = random.uniform(-0.012, 0.012)

    precision = 0.95 - 0.45 * cutoff_ratio + precision_noise
    recall = 0.10 + 0.85 * cutoff_ratio + recall_noise

    precision = max(0.0, min(1.0, precision))
    recall = max(0.0, min(1.0, recall))

    return round(precision, 4), round(recall, 4)


data = {}

for model in models:
    data[model] = {}

    for sample in samples:
        sample_data = {}

        sample_data["up_question"] = up_questions.get(
            sample,
            "What is the model likely to generate next?"
        )

        group_counts = {
            "valid": 0,
            "invalid": 0,
        }

        total = len(tokens)

        for i, token in enumerate(tokens):
            base_value = 50 - i
            noise = random.uniform(-2.0, 2.0)
            logit_value = max(0.01, base_value + noise)

            group = choose_group(i)
            group_counts[group] += 1

            precision, recall = make_precision_recall(i, total)

            sample_data[token] = {
                "logit_value": round(logit_value, 4),
                "completed_sentence": make_completed_sentence(token),
                "group": group,
                "precision": precision,
                "recall": recall,
            }

        total_count = sum(group_counts.values())

        sample_data["valid"] = group_counts["valid"] / total_count
        sample_data["invalid"] = group_counts["invalid"] / total_count

        data[model][sample] = sample_data

with output_path.open("w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Saved {output_path}")