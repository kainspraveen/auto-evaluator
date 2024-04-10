# import vertexai
from typing import Any, AsyncIterator, Dict, Iterator, List, Optional

from langchain_core.callbacks import (
    AsyncCallbackManagerForLLMRun,
    CallbackManagerForLLMRun,
)
from langchain_core.language_models import BaseChatModel, SimpleChatModel
from langchain_core.messages import AIMessageChunk, BaseMessage, HumanMessage, AIMessage
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult
from langchain_core.runnables import run_in_executor

from vertexai.preview.generative_models import GenerativeModel, Part
import vertexai.preview.generative_models as generative_models
from deepeval.models.base_model import DeepEvalBaseLLM, DeepEvalBaseModel
from deepeval.metrics import AnswerRelevancyMetric, GEval
from deepeval import assert_test
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
import vertexai
import requests

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
            return multiturn_generate_content_geminipro(self.prompt)

class DBCustomChatModel(BaseChatModel):
    """A custom chat model that hits an api-endpoint of a readily deployed llm chat model
    either vertex endpoint or a out-of-the-box api service from gcp.

    Example:

        .. code-block:: python

            model = CustomChatModel(model = "{model_api}")
            result = model.invoke([HumanMessage(content="hello")])
            result = model.batch([[HumanMessage(content="hello")],
                                 [HumanMessage(content="world")]])
    """
    def multiturn_generate_content_geminipro(self, prompt:str):
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

    def _generate(self,
                  messages: List[BaseMessage],
                  stop: Optional[List[str]] = None,
                  run_manager: Optional[CallbackManagerForLLMRun] = None,
                  **kwargs: Any,
                  ) -> ChatResult:
        """Override the _generate method to implement the chat model logic.

        This can be a call to an API, a call to a local model, or any other
        implementation that generates a response to the input prompt.

        Args:
            messages: the prompt composed of a list of messages.
            stop: a list of strings on which the model should stop generating.
                  If generation stops due to a stop token, the stop token itself
                  SHOULD BE INCLUDED as part of the output. This is not enforced
                  across models right now, but it's a good practice to follow since
                  it makes it much easier to parse the output of the model
                  downstream and understand why generation stopped.
            run_manager: A run manager with callbacks for the LLM.
        """
        #TODO(Kains): Implement call to custom model API/GeminiPro
        response = self.multiturn_generate_content_geminipro(messages[-1].content)
        message = AIMessage(content=response)
        print(message)
        print(type(message))
        generation = ChatGeneration(message = message)
        print(generation)
        print(type([generation]))
        return ChatResult(generations = [generation])

    def _stream(self,
                messages: List[BaseMessage],
                stop: Optional[List[str]] = None,
                run_manager: Optional[CallbackManagerForLLMRun] = None,
                **kwargs: Any,
                ) -> Iterator[ChatGenerationChunk]:
        """Stream the output of the model.

        This method should be implemented if the model can generate output
        in a streaming fashion. If the model does not support streaming,
        do not implement it. In that case streaming requests will be automatically
        handled by the _generate method.

        Args:
            messages: the prompt composed of a list of messages.
            stop: a list of strings on which the model should stop generating.
                  If generation stops due to a stop token, the stop token itself
                  SHOULD BE INCLUDED as part of the output. This is not enforced
                  across models right now, but it's a good practice to follow since
                  it makes it much easier to parse the output of the model
                  downstream and understand why generation stopped.
            run_manager: A run manager with callbacks for the LLM.
        """
        #TODO(Kains): Implementation for streaming
        
        response = self.multiturn_generate_content_geminipro(messages[-1].content)


        for token in response:
            chunk = ChatGenerationChunk(message=AIMessageChunk(content=token))

            if run_manager:
                run_manager.on_llm_new_token(token, chunk=chunk)

            yield chunk

    async def _astream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> AsyncIterator[ChatGenerationChunk]:
        """An async variant of astream.

        If not provided, the default behavior is to delegate to the _generate method.

        The implementation below instead will delegate to `_stream` and will
        kick it off in a separate thread.

        If you're able to natively support async, then by all means do so!
        """
        result = await run_in_executor(
            None,
            self._stream,
            messages,
            stop=stop,
            run_manager=run_manager.get_sync() if run_manager else None,
            **kwargs,
        )
        for chunk in result:
            yield chunk 
    
    @property
    def _llm_type(self) -> str:
        """Get the type of language model used by this chat model."""
        return "Gemini-Pro-001"

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Return a dictionary of identifying parameters."""
        return {"n": "none"}
        


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
    
    def multiturn_generate_content_geminipro(prompt:str):
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
            return self.multiturn_generate_content_geminipro(prompt)

    async def a_generate(self, prompt: str) -> str:
        return self.generate(prompt, testing=True)

    def get_model_name(self):
        return "GEminiPro-1.0.0 - DB Custom"


class DBCustomEmbedding(DeepEvalBaseLLM):
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

    def generate(self, prompt: List[str], testing=False) -> str:
        return generate_embeddings_hf(texts = prompt)

    async def a_generate(self, prompt: str) -> str:
        return self.generate(prompt)

    def get_model_name(self):
        return "Embeddings Model Custom huggingFace"
    
    def embed_documents(self, documents: List[str]):
        return self.generate(prompt = documents)
    def embed_query(self, query:str):
        return self.generate(prompt=[query])

# class DBCustomEmbedder()


def generate_embeddings_hf(model_id = "sentence-transformers/all-MiniLM-L6-v2", texts = ["this is a default sentence. Please provide the input"]):
    hf_token = "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"
    api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{model_id}"
    headers = {"Authorization": f"Bearer {hf_token}"}
    response = requests.post(api_url, headers=headers, json={"inputs": texts, "options":{"wait_for_model":True}})
    # print(response.json())
    return response.json()


# geminipro_v1 = DBCustomLLM(model='https://europe-west4-aiplatform.googleapis.com/v1/projects/1034748742049/locations/europe-west4/endpoints/3005048841595518976:predict')
# input  = "write me a joke"
# print(mistral_7b(input))


# metric = AnswerRelevancyMetric(model=mistral_7b)
# print(metric)

# test_case = LLMTestCase(
#         input=input,
#         actual_output=mistral_7b(input),
#         # expected_output="fragmented nature of the supply chain and existing monopolies",
#         context=["test the working of model"],
#     )

# coherence_metric = GEval(
#     name="Coherence",
#     criteria="Coherence - determine if the actual output is coherent with the input.",
#     model = mistral_7b,
#     # NOTE: you can only provide either criteria or evaluation_steps, and not both
#     evaluation_steps=["Check whether the sentences in 'actual output' aligns with that in 'input'"],
#     evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
# )

# coherence_metric.measure(test_case)
# print(coherence_metric.score)
# print(coherence_metric.reason)
# assert_test(test_case, [coherence_metric])

def multiturn_generate_content_geminipro(prompt:str):
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

def multiturn_generate_content_dbcustom(prompt: str) -> str:
    # TODO(Kains): Implement custom model vertex api deployment content generation
    pass

def mutltuturn_generate_content_():
    pass