# This is a sample Python script.
from deepeval.models.base_model import DeepEvalBaseLLM, DeepEvalBaseModel
from deepeval.metrics import ( 
    AnswerRelevancyMetric, 
    GEval,
    FaithfulnessMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    ContextualRelevancyMetric,
    HallucinationMetric,
    BiasMetric,
    ToxicityMetric,
)
from deepeval.metrics.ragas import RagasMetric
from langchain.schema import Document

import time
from deepeval import assert_test, evaluate
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
import logging

from llm_utils import DBCustomEmbeddingsLC
logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

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
        response =  self.generate(prompt, testing=False)
        return response
    def load_model(self):
        return self.model
    
    def multiturn_generate_content(self, prompt:str):
        config = {
            "max_output_tokens": 8192,
            "temperature": 0.1,
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
        # print("*****", resp.text)
        return resp.text

    def generate(self, prompt: str, testing=False) -> str:
        if testing:

            project_id = "db-dev-l5je-model-serving-lab"
            location = "europe-west4"
            vertexai.init(project=project_id, location=location)
            # TODO(Kains): Add code for hitting custom endpoints using curl/python api

        else:
            return self.multiturn_generate_content(prompt)

    async def a_generate(self, prompt: str) -> str:
        return self.generate(prompt, testing=False)

    def get_model_name(self):
        return "Mistral 7B - DB Custom"


mistral_7b = DBCustomLLM(model='https://europe-west4-aiplatform.googleapis.com/v1/projects/1034748742049/locations/europe-west4/endpoints/3005048841595518976:predict')
input  = "write me a joke"
# print(mistral_7b(input))

actual_output = mistral_7b.generate(input)
contexts = ["A Joke"]
output = mistral_7b.generate("""For each context in contexts, which is a list of strings, please generate a list of JSON objects to indicate whether the given 'actual output' agrees with EACH context. The JSON will have 2 fields: 'verdict' and 'reason'.
The 'verdict' key should STRICTLY be either 'yes' or 'no', and states whether the given text agrees with the context. 
The 'reason' is the reason for the verdict. When the answer is 'no', try to provide a correction in the reason. 

**
IMPORTANT: Please make sure to only return in JSON format, with the 'verdicts' key as a list of JSON objects.
Example contexts: ["Einstein won the Nobel Prize for his discovery of the photoelectric effect.", "Einstein won the Nobel Prize in 1968."]
Example actual output: "Einstein won the Nobel Prize in 1969 for his discovery of the photoelectric effect."

Example:
{{
    "verdicts": [
        {{
            "verdict": "yes",
            "reason": "The actual output agrees with the provided context which states that Einstein won the Nobel Prize for his discovery of the photoelectric effect."
        }},
        {{
            "verdict": "no",
            "reason": "The actual output contradicts the provided context which states that Einstein won the Nobel Prize in 1968, not 1969."
        }}
    ]  
}}

You should NOT incorporate any prior knowledge you have and take each context at face value. Since you are going to generate a verdict for each context, the number of 'verdicts' SHOULD BE STRICTLY EQUAL to that of contexts.
You should FORGIVE cases where the actual output is lacking in detail, you should ONLY provide a 'no' answer if IT IS A CONTRADICTION.
**

Contexts:
{contexts}

Actual Output:
{actual_output}

JSON:
""")

print("Model output : ", output, "Type : ", type(output))
# metric = AnswerRelevancyMetric(model=mistral_7b)
# print(metric)
print("actual test case : ", actual_output)
test_case = LLMTestCase(
        input=input,
        actual_output=actual_output,
        # expected_output="fragmented nature of the supply chain and existing monopolies",
        # context=["test the working of model"],
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

def run_deep_eval(chain, retriever, eval_qa_pair, grade_prompt, retriever_type, num_neighbors, text, logger):
    logger.info("`Running DeepEval evaluation ...`")
    predictions = []
    retrieved_docs = []
    gt_dataset = []
    latency = []
    faithfulness = []
    contextual_precision = []
    contextual_recall = []
    contextual_relevancy = []
    hallucination = []
    bias = []
    toxicity = []
    ragas = []


    # knowledge_retention = []
    # Get answer and log latency
    start_time = time.time()
    if retriever_type == "Anthropic-100k":
        docs=[Document(page_content=text)]
        answer = chain.run(input_documents=docs,question=eval_qa_pair["question"])
        predictions.append(
            {"question": eval_qa_pair["question"], "answer": eval_qa_pair["answer"], "result": answer})
    else :
        temp_dict = chain(eval_qa_pair)
        temp_dict["text"] = text
        predictions.append(temp_dict)
    gt_dataset.append(eval_qa_pair)
    end_time = time.time()
    elapsed_time = end_time - start_time
    latency.append(elapsed_time)

    # Extract text from retrieved docs
    retrieved_doc_text = ""
    if retriever_type == "Anthropic-100k":
        retrieved_doc_text = "Doc %s: " % str(eval_qa_pair["answer"])
    else:
        docs = retriever.get_relevant_documents(eval_qa_pair["question"])
        for i, doc in enumerate(docs):
            retrieved_doc_text += "Doc %s: " % str(i+1) + \
                doc.page_content + " "

    # Log
    retrieved = {"question": eval_qa_pair["question"],
                 "answer": eval_qa_pair["answer"], "result": retrieved_doc_text}
    retrieved_docs.append(retrieved)


    test_case = LLMTestCase(
    input=eval_qa_pair["question"],
    actual_output = temp_dict["result"],
    expected_output = eval_qa_pair["answer"],
    retrieval_context = [retrieved_doc_text]
    )
    print("\n\n",retrieved_doc_text, "\n\n")

    # Grade
    #   Faithfulness
    
    try:
        metric = FaithfulnessMetric(
        threshold=0.7,
        model=DBCustomLLM(model='https://europe-west4-aiplatform.googleapis.com/v1/projects/1034748742049/locations/europe-west4/endpoints/3005048841595518976:predict'),
        include_reason=True)
        metric.measure(test_case)
        print("!!!!!!!!!!!!!!!! ", metric.score, type(metric.score))
        faithfulness.append({"score":int(metric.score), "JUSTIFICATION": metric.reason})
    except Exception as e:
        logger.info(e)
        faithfulness.append({"score":-1, "JUSTIFICATION": "Evaluator Model did not return correct Response"})


    #   Contextual Precision
    try:
        metric = ContextualPrecisionMetric(
        threshold=0.7,
        model=DBCustomLLM(model='https://europe-west4-aiplatform.googleapis.com/v1/projects/1034748742049/locations/europe-west4/endpoints/3005048841595518976:predict'),
        include_reason=True
        )
        metric.measure(test_case)
        contextual_precision.append({"score":int(metric.score), "JUSTIFICATION": metric.reason})
    except Exception as e:
        logger.info(e)
        contextual_precision.append({"score":-1, "JUSTIFICATION": "Evaluator Model did not return correct Response"})

    # Contextual Recall
    try:
        metric = ContextualRecallMetric(
        threshold=0.7,
        model=DBCustomLLM(model='https://europe-west4-aiplatform.googleapis.com/v1/projects/1034748742049/locations/europe-west4/endpoints/3005048841595518976:predict'),
        include_reason=True
        )
        metric.measure(test_case)
        contextual_recall.append({"score":int(metric.score), "JUSTIFICATION": metric.reason})
    except Exception as e:
        logger.info(e)
        contextual_recall.append({"score":-1, "JUSTIFICATION": "Evaluator Model did not return correct Response"})

    # Contextual Relevancy
    try:
        metric = ContextualRelevancyMetric(
        threshold=0.7,
        model=DBCustomLLM(model='https://europe-west4-aiplatform.googleapis.com/v1/projects/1034748742049/locations/europe-west4/endpoints/3005048841595518976:predict'),
        include_reason=True
        )
        metric.measure(test_case)
        contextual_relevancy.append({"score":int(metric.score), "JUSTIFICATION": metric.reason})
    except Exception as e:
        logger.info(e)
        contextual_relevancy.append({"score":-1, "JUSTIFICATION": "Evaluator Model did not return correct Response"})


    # Hallucination
    try:
        test_case_h = LLMTestCase(
        input=eval_qa_pair["question"],
        actual_output = temp_dict["result"],
        expected_output = eval_qa_pair["answer"],
        context = [retrieved_doc_text],
        retrieval_context = [retrieved_doc_text]
        )
        metric = HallucinationMetric(
            threshold=0.7,
            model=DBCustomLLM(model='https://europe-west4-aiplatform.googleapis.com/v1/projects/1034748742049/locations/europe-west4/endpoints/3005048841595518976:predict'),
            include_reason=True
        )
        metric.measure(test_case_h)
        hallucination.append({"score":int(metric.score), "JUSTIFICATION": metric.reason})
    except Exception as e:
        logger.info(e)
        hallucination.append({"score":-1, "JUSTIFICATION": "Evaluator Model did not return correct Response"})

    # Bias
    try:
        metric = BiasMetric(
            threshold=0.7,
            model=DBCustomLLM(model='https://europe-west4-aiplatform.googleapis.com/v1/projects/1034748742049/locations/europe-west4/endpoints/3005048841595518976:predict'),
            include_reason=True
        )
        metric.measure(test_case)
        bias.append({"score":int(metric.score), "JUSTIFICATION": metric.reason})
        # bias.append({"GRADE":"None", "JUSTIFICATION": "NONE"})
    except Exception as e:
        logger.info(e)
        bias.append({"score":-1, "JUSTIFICATION": "Evaluator Model did not return correct Response"})

    # Toxicity
    try:
        metric = ToxicityMetric(
            threshold=0.7,
            model=DBCustomLLM(model='https://europe-west4-aiplatform.googleapis.com/v1/projects/1034748742049/locations/europe-west4/endpoints/3005048841595518976:predict'),
            include_reason=True
        )
        metric.measure(test_case)
        toxicity.append({"score":int(metric.score), "JUSTIFICATION": metric.reason})
    except Exception as e:
        logger.info(e)
        toxicity.append({"score":-1, "JUSTIFICATION": "Evaluator Model did not return correct Response"})

    # RAGAS

    # metric = RagasMetric(
    #     threshold=0.7,
    #     model=DBCustomLLM(model='https://europe-west4-aiplatform.googleapis.com/v1/projects/1034748742049/locations/europe-west4/endpoints/3005048841595518976:predict'),
    #     embeddings=DBCustomEmbeddingsLC()
    # )
    # metric.measure(test_case)
    # ragas.append({"GRADE":metric.score, "JUSTIFICATION": metric.reason})
    ragas.append({"GRADE":"None", "JUSTIFICATION": "NONE"})

    return predictions, latency, faithfulness, contextual_precision, contextual_recall, contextual_relevancy, hallucination, bias, toxicity, ragas









    # graded_answers = grade_model_answer(
    #     gt_dataset, predictions, grade_prompt, logger)
    # # graded_answers["text"] = text
    # graded_retrieval = grade_model_retrieval(
    #     gt_dataset, retrieved_docs, grade_prompt, logger)


    # graded_retrieval["text"] = text
    return graded_answers, graded_retrieval, latency, predictions