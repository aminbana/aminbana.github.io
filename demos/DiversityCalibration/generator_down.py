import json
import random
from pathlib import Path

random.seed(42)

output_path = Path("data_down.json")

models = ["Qwen2.5-VL", "LLaVA", "InternVL"]

samples = [
    "Hello I am",
    "Today I saw ",
    "The image shows ",
]

temperatures = ["0.1", "0.5", "1.0"]

tokens = [str(i) for i in range(40)]

sentence_templates = [
    "{token} is clearly visible.",
    "{token} appears in the scene.",
    "{token} is near the center.",
    "{token} can be seen in the image.",
    "{token} is part of the scene.",
]


def choose_group(index):
    if index < 15:
        return "valid_and_frequent"

    if index < 24:
        return "valid_and_rare"

    return "invalid"


def make_completed_sentence(token, num_sentences=6):
    sentences = []

    for _ in range(num_sentences):
        sentence = random.choice(sentence_templates).format(token=token)
        sentences.append(sentence)

    return " ".join(sentences)


def make_temperature_rates(temperature):
    if temperature == "0.1":
        base = {
            "valid_and_frequent": 0.66,
            "valid_and_rare": 0.24,
            "invalid": 0.10,
        }
        noise_scale = 0.025
    elif temperature == "0.5":
        base = {
            "valid_and_frequent": 0.55,
            "valid_and_rare": 0.30,
            "invalid": 0.15,
        }
        noise_scale = 0.040
    else:
        base = {
            "valid_and_frequent": 0.43,
            "valid_and_rare": 0.32,
            "invalid": 0.25,
        }
        noise_scale = 0.055

    values = {
        key: max(0.001, value + random.uniform(-noise_scale, noise_scale))
        for key, value in base.items()
    }

    total = sum(values.values())

    return {
        key: round(value / total, 4)
        for key, value in values.items()
    }


data = {}

for model in models:
    data[model] = {}

    for sample in samples:
        data[model][sample] = {}

        for temperature in temperatures:
            temperature_data = {}

            temperature_data["__temperature_rates"] = make_temperature_rates(temperature)

            for i, token in enumerate(tokens):
                base_value = 40 - i

                if temperature == "0.1":
                    noise = random.uniform(0.0, 1.0)
                elif temperature == "0.5":
                    noise = random.uniform(-3.0, 3.0)
                else:
                    noise = random.uniform(-6.0, 6.0)

                logit_value = max(0.01, base_value + noise)
                group = choose_group(i)

                temperature_data[token] = {
                    "logit_value": round(logit_value, 4),
                    "completed_sentence": make_completed_sentence(token),
                    "group": group,
                }

            data[model][sample][temperature] = temperature_data

with output_path.open("w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Saved {output_path}")