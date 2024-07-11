import asyncio
from nnsight import LanguageModel
from tqdm import tqdm
import os
os.environ["CONFIG_PATH"] = "configs/caden_gpt2.yaml"

from sae_auto_interp.clients import get_client
from sae_auto_interp.scorers import ScorerInput, OpenAISimulator
from sae_auto_interp.utils import load_tokenized_data, execute_model
from sae_auto_interp.features import FeatureRecord
from sae_auto_interp.experiments import sample_top_and_quantiles
from sae_auto_interp.logger import logger

model = LanguageModel("openai-community/gpt2", device_map="auto", dispatch=True)
tokens = load_tokenized_data(model.tokenizer)

raw_features_path = "raw_features"
processed_features_path = "processed_features"
explanations_dir = "explanations/simple_local_70b"
scorer_out_dir = "scores/oai_70b/simple_local_70b"

def flatten(l):
    return [item for sublist in l for item in sublist]

def load_explanation(feature):
    explanations_path = f"{explanations_dir}/layer{feature.layer_index}_feature{feature.feature_index}.txt"

    with open(explanations_path, "r") as f:
        explanation = f.read()

    return explanation

scorer_inputs = []

for layer in range(0,12,2):
    records = FeatureRecord.from_tensor(
        tokens,
        layer,
        tokenizer=model.tokenizer,
        selected_features=list(range(50)),
        raw_dir= raw_features_path,
        processed_dir=processed_features_path,
        n_random=10,
        min_examples=120,
        max_examples=10000
    )
    
    for record in tqdm(records):

        if len(record.examples) < 150:
            continue

        try:
            explanation = load_explanation(record.feature)
            _, test = sample_top_and_quantiles(
                record=record,
                n_train=0,
                n_test=2,
                n_quantiles=4,
                seed=22,
            )
        except Exception as e:
            logger.error(f"Failed while sampling for {record.feature}: {e}") 
            continue

        scorer_inputs.append(
            ScorerInput(
                record=record,
                test_examples=flatten(test),
                explanation=explanation
            )
        )

    break

client = get_client("local", "casperhansen/llama-3-70b-instruct-awq")
scorer = OpenAISimulator(client)


asyncio.run(
    execute_model(
        scorer, 
        scorer_inputs,
        output_dir=scorer_out_dir,
    )
)