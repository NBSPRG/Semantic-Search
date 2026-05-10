"""
Optional Colab fine-tuning/evaluation script.

The API uses a pre-trained sentence-transformer directly. Use this file only if
you want to test whether a small domain-specific fine-tune improves retrieval.
"""

# Colab setup:
# !pip install -U sentence-transformers datasets accelerate

from sentence_transformers import InputExample, SentenceTransformer, losses
from sentence_transformers.evaluation import EmbeddingSimilarityEvaluator
from torch.utils.data import DataLoader

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
OUTPUT_DIR = "finetuned-minilm-similarity"


def build_examples() -> list[InputExample]:
    return [
        InputExample(
            texts=["B2B fintech lead generation", "Finding SaaS prospects in fintech"],
            label=0.92,
        ),
        InputExample(
            texts=["Real estate buyer intent data", "Property purchase leads"],
            label=0.88,
        ),
        InputExample(
            texts=["Healthcare appointment reminders", "Clinic patient scheduling"],
            label=0.83,
        ),
        InputExample(
            texts=["B2B fintech lead generation", "Quantum mechanics lecture notes"],
            label=0.05,
        ),
        InputExample(
            texts=["Restaurant menu design", "Cloud infrastructure monitoring"],
            label=0.03,
        ),
        InputExample(
            texts=["Fintech SaaS customer list", "Financial software prospect database"],
            label=0.9,
        ),
        InputExample(
            texts=["Dental clinic reminders", "B2B fintech sales intelligence"],
            label=0.08,
        ),
    ]


def main() -> None:
    model = SentenceTransformer(MODEL_NAME)
    examples = build_examples()

    train_examples = examples[:5]
    eval_examples = examples[5:]

    train_loader = DataLoader(train_examples, shuffle=True, batch_size=2)
    train_loss = losses.CosineSimilarityLoss(model)

    evaluator = EmbeddingSimilarityEvaluator.from_input_examples(
        eval_examples,
        name="mini-domain-eval",
    )

    model.fit(
        train_objectives=[(train_loader, train_loss)],
        evaluator=evaluator,
        epochs=1,
        warmup_steps=0,
        output_path=OUTPUT_DIR,
    )

    print(f"Saved fine-tuned model to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
