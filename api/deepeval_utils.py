# This is a sample Python script.
from deepeval.models.base_model import DeepEvalBaseLLM, DeepEvalBaseModel
from deepeval.metrics import AnswerRelevancyMetric, GEval
from deepeval import assert_test
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part
import vertexai.preview.generative_models as generative_models

from typing import Any, AsyncIterator, Dict, Iterator, List, Optional

from langchain_core.callbacks import (
    AsyncCallbackManagerForLLMRun,
    CallbackManagerForLLMRun,
)
from langchain_core.language_models import BaseChatModel, SimpleChatModel
from langchain_core.messages import AIMessageChunk, BaseMessage, HumanMessage, AIMessage
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult
from langchain_core.runnables import run_in_executor

class DBModel:
    def __init__(self, prompt: str):
        self.prompt = prompt

    def __call__(self, testing=False):
        if not testing:

            project_id = "db-dev-l5je-model-serving-lab"
            location = "europe-west4"
            vertexai.init(project=project_id, location=location)
            # TODO(Kains): Add code for hitting custom endpoints using curl/python api

        else:
            return multiturn_generate_content(self.prompt)


class DBCustomLLM(DeepEvalBaseLLM):
    def __init__(
        self,
        model,
        # tokenizer
    ):
        self.model = model
    def __call__(self, prompt):
        response =  self.generate(prompt, testing=True)
        return response
    def load_model(self):
        return self.model
    
    def multiturn_generate_content(self, prompt:str):
        config = {
            "max_output_tokens": 2048,
            "temperature": 0.9,
            "top_p": 1
        }
        model = GenerativeModel("gemini-1.0-pro-001")
        chat = model.start_chat()
        resp = chat.send_message(prompt, generation_config=config, safety_settings={
            generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        })
        return resp.text

    def generate(self, prompt: str, testing=False) -> str:
        if not testing:

            project_id = "db-dev-l5je-model-serving-lab"
            location = "europe-west4"
            vertexai.init(project=project_id, location=location)
            # TODO(Kains): Add code for hitting custom endpoints using curl/python api

        else:
            return self.multiturn_generate_content(prompt)

    async def a_generate(self, prompt: str) -> str:
        return self.generate(prompt, testing=True)

    def get_model_name(self):
        return "Mistral 7B - DB Custom"


mistral_7b = DBCustomLLM(model='https://europe-west4-aiplatform.googleapis.com/v1/projects/1034748742049/locations/europe-west4/endpoints/3005048841595518976:predict')
input  = "write me a joke"
print(mistral_7b(input))


# metric = AnswerRelevancyMetric(model=mistral_7b)
# print(metric)

test_case = LLMTestCase(
        input=input,
        actual_output=mistral_7b(input),
        # expected_output="fragmented nature of the supply chain and existing monopolies",
        context=["test the working of model"],
    )

coherence_metric = GEval(
    name="Coherence",
    criteria="Coherence - determine if the actual output is coherent with the input.",
    model = mistral_7b,
    # NOTE: you can only provide either criteria or evaluation_steps, and not both
    evaluation_steps=["Check whether the sentences in 'actual output' aligns with that in 'input'"],
    evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
)

coherence_metric.measure(test_case)
print(coherence_metric.score)
print(coherence_metric.reason)
assert_test(test_case, [coherence_metric])

