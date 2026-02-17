"""
Ragas Evaluation for Travel Chatbot
RUBRIC: Evaluation Framework (RAGAS) (8 marks total)
- RAGAS evaluation implemented (3 marks)
- Golden dataset created (2 marks)
- All four metrics computed (2 marks)
- Results saved with pass/fail logic (1 mark)

TASK: Implement Ragas evaluation with 4 metrics
"""
import os
import json
import logging
import asyncio
import pandas as pd
from pathlib import Path
from typing import List, Dict

from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
from datasets import Dataset

from src.search_engine import TravelSearchEngine
from src.config import Config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("evaluation")


class TravelChatbotEvaluator:
    """Evaluates Travel Chatbot using Ragas metrics"""

    def __init__(self):
        # Initialize search engine and golden dataset path
        self.engine = TravelSearchEngine()
        self.golden_dataset_path = Path("data") / "golden_dataset.json"

    def load_golden_dataset(self) -> List[Dict]:
        """
        Load golden dataset for evaluation

        Checks if file exists, if not creates sample dataset
        """
        if not self.golden_dataset_path.exists():
            logger.warning(f"Golden dataset not found at {self.golden_dataset_path}")
            logger.info("Creating sample golden dataset...")
            return self._create_sample_dataset()

        with open(self.golden_dataset_path, 'r') as f:
            return json.load(f)

    def _create_sample_dataset(self) -> List[Dict]:
        """
        Create sample golden dataset if not exists

        Creates list of dicts with 'question' and 'ground_truth' keys
        Saves to golden_dataset_path
        """
        sample_data = [
            {
                "question": "What are the baggage allowance rules for international flights?",
                "ground_truth": "International flights typically allow 23kg checked baggage and 7kg cabin baggage per passenger. Specific allowances may vary by airline and ticket class."
            },
            {
                "question": "What is Air India's cancellation policy?",
                "ground_truth": "Air India allows cancellations with applicable fees depending on fare type. Refundable tickets can be cancelled with minimal charges, while non-refundable tickets may have higher cancellation fees."
            },
            {
                "question": "Do I need a visa to travel from India to UK?",
                "ground_truth": "Yes, Indian passport holders require a visa to travel to the UK. You must apply for a UK visa before travel through the official UK government visa application process."
            },
            {
                "question": "What are the refund policies for flight cancellations?",
                "ground_truth": "Refund policies vary by airline and ticket type. Refundable tickets allow full or partial refunds, while non-refundable tickets may only offer travel credits. Cancellation fees typically apply."
            },
            {
                "question": "What documents do I need for international travel?",
                "ground_truth": "For international travel, you need a valid passport, visa (if required for destination country), confirmed flight tickets, and any required health certificates or vaccination records."
            }
        ]

        # Save sample dataset
        self.golden_dataset_path.parent.mkdir(exist_ok=True)
        with open(self.golden_dataset_path, 'w') as f:
            json.dump(sample_data, f, indent=2)

        logger.info(f"Sample golden dataset saved to {self.golden_dataset_path}")
        return sample_data

    def generate_responses(self, questions: List[str]) -> tuple:
        """
        Generate responses for questions

        For each question:
        1. Searches for documents
        2. Synthesizes response
        3. Collects contexts
        Returns (answers, contexts)
        """
        answers = []
        contexts = []

        for question in questions:
            logger.info(f"Generating answer for: {question}")

            try:
                # Search for relevant documents
                docs, _ = self.engine.search_by_text(question, k=5)

                # Generate answer
                answer = self.engine.synthesize_response(docs, question)

                # Collect contexts (retrieved documents)
                context_texts = [doc.page_content for doc in docs]

                answers.append(answer)
                contexts.append(context_texts)

            except Exception as e:
                logger.error(f"Error generating answer for '{question}': {e}")
                answers.append("Unable to generate answer")
                contexts.append([])

        return answers, contexts

    async def run_ragas_evaluation(self):
        """
        Run Ragas evaluation

        This method:
        1. Loads golden dataset
        2. Generates responses
        3. Prepares dataset dict
        4. Runs Ragas evaluation with 4 metrics
        5. Saves results
        """
        logger.info("=" * 70)
        logger.info("Starting Ragas Evaluation...")
        logger.info("=" * 70)

        # Load golden dataset
        golden_data = self.load_golden_dataset()

        if not golden_data:
            logger.error("No evaluation data available")
            return None

        logger.info(f"Loaded {len(golden_data)} test cases")

        # Extract questions and ground truths
        questions = [item["question"] for item in golden_data]
        ground_truths = [[item["ground_truth"]] for item in golden_data]

        # Generate answers and contexts
        logger.info("\nGenerating responses...")
        answers, contexts = self.generate_responses(questions)

        # Prepare dataset for Ragas
        dataset_dict = {
            "question": questions,
            "answer": answers,
            "contexts": contexts,
            "ground_truth": ground_truths
        }

        # Create HuggingFace Dataset
        hf_dataset = Dataset.from_dict(dataset_dict)

        logger.info("\nRunning Ragas metrics...")
        logger.info("Metrics: faithfulness, answer_relevancy, context_precision, context_recall")

        # Run evaluation
        try:
            results = evaluate(
                hf_dataset,
                metrics=[
                    faithfulness,
                    answer_relevancy,
                    context_precision,
                    context_recall
                ],
            )

            logger.info("\n" + "=" * 70)
            logger.info("EVALUATION RESULTS")
            logger.info("=" * 70)
            logger.info(f"\nRagas Scores:")
            logger.info(f"  Faithfulness:       {results['faithfulness']:.4f}")
            logger.info(f"  Answer Relevancy:   {results['answer_relevancy']:.4f}")
            logger.info(f"  Context Precision:  {results['context_precision']:.4f}")
            logger.info(f"  Context Recall:     {results['context_recall']:.4f}")
            logger.info("=" * 70)

            # Save detailed results
            self._save_results(results, dataset_dict)

            return results

        except Exception as e:
            logger.error(f"Ragas evaluation failed: {e}")
            logger.error("Make sure you have OPENAI_API_KEY set for Ragas to work")
            return None

    def _save_results(self, results: dict, dataset_dict: dict):
        """
        Save evaluation results to file

        Saves summary JSON and detailed CSV
        """
        output_dir = Path("reports")
        output_dir.mkdir(exist_ok=True)

        # Save summary
        summary = {
            "faithfulness": float(results.get('faithfulness', 0)),
            "answer_relevancy": float(results.get('answer_relevancy', 0)),
            "context_precision": float(results.get('context_precision', 0)),
            "context_recall": float(results.get('context_recall', 0)),
            "total_test_cases": len(dataset_dict["question"])
        }

        summary_path = output_dir / "evaluation_summary.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)

        logger.info(f"\n✅ Evaluation summary saved to {summary_path}")

        # Save detailed results
        detailed_df = pd.DataFrame(dataset_dict)
        detailed_path = output_dir / "evaluation_detailed.csv"
        detailed_df.to_csv(detailed_path, index=False)

        logger.info(f"✅ Detailed results saved to {detailed_path}")

    def run(self):
        """Run evaluation (sync wrapper)"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(self.run_ragas_evaluation())


def run_evaluation():
    """
    Main evaluation function

    Runs evaluator and checks if results pass thresholds
    """
    evaluator = TravelChatbotEvaluator()
    results = evaluator.run()

    if results:
        # Check if evaluation passes minimum thresholds
        min_faithfulness = 0.6
        min_relevancy = 0.6

        passed = (
                results.get('faithfulness', 0) >= min_faithfulness and
                results.get('answer_relevancy', 0) >= min_relevancy
        )

        if passed:
            logger.info("\n✅ EVALUATION PASSED")
            return 0
        else:
            logger.warning("\n⚠️  EVALUATION BELOW THRESHOLDS")
            return 1
    else:
        logger.error("\n❌ EVALUATION FAILED")
        return 1


if __name__ == "__main__":
    import sys

    exit_code = run_evaluation()
    sys.exit(exit_code)