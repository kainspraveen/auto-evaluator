"""
This is an API to support the LLM QA chain auto-evaluator. 
"""

import io
import os
from dotenv import load_dotenv
import sentry_sdk
import json
import time
import pypdf
import random
import logging
import itertools
import faiss
import pandas as pd
from typing import Dict, List
from json import JSONDecodeError

from langchain.schema import Document
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.chains import QAGenerationChain
from langchain.retrievers import SVMRetriever
from langchain.evaluation.qa import QAEvalChain
from langchain.retrievers import TFIDFRetriever
from sse_starlette.sse import EventSourceResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile, Form
# from langchain.chains.question_answering import load_qa_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain_community.vectorstores import Chroma
from deepeval_utils import run_deep_eval
# from ragas.integrations.langchain import EvaluatorChain
# from ragas.langchain.evalchain import RagasEvaluatorChain
from ragas.metrics import (
    answer_correctness,
    answer_relevancy,
    context_precision,
    context_recall,
    context_relevancy,
    faithfulness,
)
from text_utils import GRADE_DOCS_PROMPT, GRADE_ANSWER_PROMPT, GRADE_DOCS_PROMPT_FAST, GRADE_ANSWER_PROMPT_FAST, GRADE_ANSWER_PROMPT_BIAS_CHECK, GRADE_ANSWER_PROMPT_OPENAI, QA_CHAIN_PROMPT, QA_CHAIN_PROMPT_LLAMA
from llm_utils import multiturn_generate_content_geminipro, multiturn_generate_content_dbcustom, DBCustomLLM, DBCustomEmbedding,DBCustomChatModel,DBCustomEmbeddingsLC

def generate_eval(text, chunk, logger):
    """
    Generate question answer pair from input text 
    @param text: text to generate eval set from
    @param chunk: chunk size to draw question from text
    @param logger: logger
    @return: dict with keys "question" and "answer"
    """

    logger.info("`Generating eval QA pair ...`")
    # Generate random starting index in the doc to draw question from
    num_of_chars = len(text)
    starting_index = random.randint(0, num_of_chars-chunk)
    sub_sequence = text[starting_index:starting_index+chunk]
    # Set up QAGenerationChain chain using GPT 3.5 as default
    chain = QAGenerationChain.from_llm(DBCustomChatModel())
    eval_set = []
    # Catch any QA generation errors and re-try until QA pair is generated
    awaiting_answer = True
    while awaiting_answer:
        try:
            qa_pair = chain.run(sub_sequence)
            eval_set.append(qa_pair)
            awaiting_answer = False
        except JSONDecodeError:
            logger.error("Error on question")
            starting_index = random.randint(0, num_of_chars-chunk)
            sub_sequence = text[starting_index:starting_index+chunk]
    eval_pair = list(itertools.chain.from_iterable(eval_set))
    return eval_pair


def split_texts(text, chunk_size, overlap, split_method, logger):
    """
    Split text into chunks
    @param text: text to split
    @param chunk_size: charecters per split
    @param overlap: charecter overlap between splits
    @param split_method: method used to split text
    @param logger: logger
    @return: list of str splits
    """

    logger.info("`Splitting doc ...`")
    if split_method == "RecursiveTextSplitter":
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size,
                                                       chunk_overlap=overlap)
    elif split_method == "CharacterTextSplitter":
        text_splitter = CharacterTextSplitter(separator=" ",
                                              chunk_size=chunk_size,
                                              chunk_overlap=overlap)
    splits = text_splitter.split_text(text)
    return splits


def make_llm(model):
    """
    Make LLM
    @param model: LLM to use
    @return: LLM
    """

    #Note: WIP -> additional DB custom models

    if model == "Gemini-1.0-pro-001":
        # llm = DBCustomLLM(model='https://europe-west4-aiplatform.googleapis.com/v1/projects/1034748742049/locations/europe-west4/endpoints/3005048841595518976:predict')
        llm = DBCustomChatModel()
    elif model == "Mistral-7b":
        # llm = DBCustomLLM(model='https://europe-west4-aiplatform.googleapis.com/v1/projects/1034748742049/locations/europe-west4/endpoints/3005048841595518976:predict')
        llm = DBCustomChatModel()

    elif model == "Llama2-7b":
        # llm = DBCustomLLM(model='https://europe-west4-aiplatform.googleapis.com/v1/projects/1034748742049/locations/europe-west4/endpoints/3005048841595518976:predict')
        llm = DBCustomChatModel()
    
    elif model == "Mistral-8x7b":
        # llm = DBCustomLLM(model='https://europe-west4-aiplatform.googleapis.com/v1/projects/1034748742049/locations/europe-west4/endpoints/3005048841595518976:predict')
        llm = DBCustomChatModel()
    elif model == "Llama2-30b":
        # llm = DBCustomLLM(model='https://europe-west4-aiplatform.googleapis.com/v1/projects/1034748742049/locations/europe-west4/endpoints/3005048841595518976:predict')
        llm = DBCustomChatModel()
    else:
        # llm = DBCustomLLM(model='https://europe-west4-aiplatform.googleapis.com/v1/projects/1034748742049/locations/europe-west4/endpoints/3005048841595518976:predict')
        llm = DBCustomChatModel()
    return llm


def make_retriever(splits, retriever_type, embeddings, num_neighbors, llm, logger):
    """
    Make document retriever
    @param splits: list of str splits
    @param retriever_type: retriever type
    @param embedding_type: embedding type
    @param num_neighbors: number of neighbors for retrieval
    @param _llm: model
    @param logger: logger
    @return: retriever
    """

    logger.info("`Making retriever ...`")
    # Set embeddings
    
    # Note: Test
    if embeddings == "vertex-gecko":
        embd = DBCustomEmbeddingsLC()
    else:
        print("No case satisfies")

    # Select retriever
    if retriever_type == "similarity-search":
        vectorstore = FAISS.from_texts(splits, embd)
        retriever = vectorstore.as_retriever(k=num_neighbors)
    elif retriever_type == "custom-chromaDB":
        vectorstore = Chroma(collection_name = "langchain_store", embedding_function = embd).from_texts(texts = splits, embedding = embd)
        retriever  = vectorstore.as_retriever(k = num_neighbors)
    elif retriever_type == "SVM":
        retriever = SVMRetriever.from_texts(splits, embd)
    elif retriever_type == "TF-IDF":
        retriever = TFIDFRetriever.from_texts(splits)
    return retriever

def make_chain(llm, retriever, retriever_type, model):

    """
    Make retrieval chain
    @param llm: model
    @param retriever: retriever
    @param retriever_type: retriever type
    @return: QA chain
    """

    chain_type_kwargs = {"prompt": QA_CHAIN_PROMPT}

    # Select model 
    
    chain_type_kwargs = {"prompt": QA_CHAIN_PROMPT}
    qa_chain = RetrievalQA.from_chain_type(llm,
                                            chain_type="stuff",
                                            retriever=retriever,
                                            chain_type_kwargs=chain_type_kwargs,
                                            input_key="question")
    return qa_chain


def grade_model_answer(predicted_dataset, predictions, grade_answer_prompt, logger):
    """
    Grades the answer based on ground truth and model predictions.
    @param predicted_dataset: A list of dictionaries containing ground truth questions and answers.
    @param predictions: A list of dictionaries containing model predictions for the questions.
    @param grade_answer_prompt: The prompt level for the grading. Either "Fast" or "Full".
    @param logger: logger
    @return: A list of scores for the distilled answers.
    """

    logger.info("`Grading model answer ...`")
    if grade_answer_prompt == "Fast":
        prompt = GRADE_ANSWER_PROMPT_FAST
    elif grade_answer_prompt == "Descriptive w/ bias check":
        prompt = GRADE_ANSWER_PROMPT_BIAS_CHECK
    elif grade_answer_prompt == "OpenAI grading prompt":
        prompt = GRADE_ANSWER_PROMPT_OPENAI
    else:
        prompt = GRADE_ANSWER_PROMPT

    # Note: GPT-4 grader is advised by OAI 
    eval_chain = QAEvalChain.from_llm(llm=DBCustomChatModel(),
                                      prompt=prompt)
    graded_outputs = eval_chain.evaluate(predicted_dataset,
                                         predictions,
                                         question_key="question",
                                         prediction_key="result")
    return graded_outputs


def grade_model_retrieval(gt_dataset, predictions, grade_docs_prompt, logger):
    """
    Grades the relevance of retrieved documents based on ground truth and model predictions.
    @param gt_dataset: list of dictionaries containing ground truth questions and answers.
    @param predictions: list of dictionaries containing model predictions for the questions
    @param grade_docs_prompt: prompt level for the grading.
    @return: list of scores for the retrieved documents.
    """

    logger.info("`Grading relevance of retrieved docs ...`")
    if grade_docs_prompt == "Fast":
        prompt = GRADE_DOCS_PROMPT_FAST
    else:
        prompt = GRADE_DOCS_PROMPT

    # Note: GPT-4 grader is advised by OAI
    eval_chain = QAEvalChain.from_llm(llm=DBCustomChatModel(),
                                      prompt=prompt)
    graded_outputs = eval_chain.evaluate(gt_dataset,
                                         predictions,
                                         question_key="question",
                                         prediction_key="result")
    return graded_outputs


# def run_eval_geval(chain, retriever, eval_qa_pair, retriever_type, num_neighbours, text, logger):
#     logger.info("`Running G-Eval Evaluator....`")
#     predictions = []
#     retrieved_docs = []
#     gt_dataset = []
#     latency = []
#     start_time = time.time()

# def run_eval_ragas(chain, retriever, eval_qa_pair, retriever_type, num_neighbours, text, logger):
#     logger.info("`Running RAGAS evaluation...`")
#     predictions = []
#     retrieved_docs = []
#     gt_dataset = []
#     latency = []
#     start_time = time.time()




def run_eval(chain, retriever, eval_qa_pair, grade_prompt, retriever_type, num_neighbors, text, logger):
    """
    Runs evaluation on a model's performance on a given evaluation dataset.
    @param chain: Model chain used for answering questions
    @param retriever:  Document retriever used for retrieving relevant documents
    @param eval_set: List of dictionaries containing questions and corresponding ground truth answers
    @param grade_prompt: String prompt used for grading model's performance
    @param retriever_type: String specifying the type of retriever used
    @param num_neighbors: Number of neighbors to retrieve using the retriever
    @param text: full document text
    @return: A tuple of four items:
    - answers_grade: A dictionary containing scores for the model's answers.
    - retrieval_grade: A dictionary containing scores for the model's document retrieval.
    - latencies_list: A list of latencies in seconds for each question answered.
    - predictions_list: A list of dictionaries containing the model's predicted answers and relevant documents for each question.
    """

    logger.info("`Running eval ...`")
    predictions = []
    retrieved_docs = []
    gt_dataset = []
    latency = []

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
    
    docs = retriever.get_relevant_documents(eval_qa_pair["question"])
    for i, doc in enumerate(docs):
        retrieved_doc_text += "Doc %s: " % str(i+1) + \
            doc.page_content + " "

    # Log
    retrieved = {"question": eval_qa_pair["question"],
                 "answer": eval_qa_pair["answer"], "result": retrieved_doc_text}
    retrieved_docs.append(retrieved)

    # Grade
    graded_answers = grade_model_answer(
        gt_dataset, predictions, grade_prompt, logger)
    # graded_answers["text"] = text
    graded_retrieval = grade_model_retrieval(
        gt_dataset, retrieved_docs, grade_prompt, logger)
    # graded_retrieval["text"] = text
    return graded_answers, graded_retrieval, latency, predictions

load_dotenv()

if os.environ.get("ENVIRONMENT") != "development":
    sentry_sdk.init(
    dsn="https://065aa152c4de4e14af9f9e7335c8eae4@o4505106202820608.ingest.sentry.io/4505106207735808",
    traces_sample_rate=1.0,
    )

app = FastAPI()

origins = [
    "http://localhost:3000",
    "localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Welcome to the Auto Evaluator!"}


def run_evaluator(
    files,
    num_eval_questions,
    chunk_chars,
    overlap,
    split_method,
    retriever_type,
    embeddings,
    model_version,
    grade_prompt,
    num_neighbors,
    test_dataset
):

    # Set up logging
    logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
    logger = logging.getLogger(__name__)

    # Read content of files
    texts = []
    fnames = []
    for file in files:
        logger.info("Reading file: {}".format(file.filename))
        contents = file.file.read()
        # PDF file
        if file.content_type == 'application/pdf':
            logger.info("File {} is a PDF".format(file.filename))
            pdf_reader = pypdf.PdfReader(io.BytesIO(contents))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            texts.append(text)
            fnames.append(file.filename)
        # Text file
        elif file.content_type == 'text/plain':
            logger.info("File {} is a TXT".format(file.filename))
            texts.append(contents.decode())
            fnames.append(file.filename)
        else:
            logger.warning(
                "Unsupported file type for file: {}".format(file.filename))
    text = " ".join(texts)

    
    
    logger.info("Splitting texts")
    splits = split_texts(text, chunk_chars, overlap, split_method, logger)

    logger.info("Make LLM")
    llm = make_llm(model_version)

    logger.info("Make retriever")
    retriever = make_retriever(
        splits, retriever_type, embeddings, num_neighbors, llm, logger)

    logger.info("Make chain")
    qa_chain = make_chain(llm, retriever, retriever_type, model_version)

    for i in range(num_eval_questions):

        # Generate one question
        if i < len(test_dataset):
            eval_pair = test_dataset[i]
        else:
            eval_pair = generate_eval(text, 3000, logger)
            if len(eval_pair) == 0:
                # Error in eval generation
                continue
            else:
                # This returns a list, so we unpack to dict
                eval_pair = eval_pair[0]

        # Run eval
        graded_answers, graded_retrieval, latency, predictions = run_eval(
            qa_chain, retriever, eval_pair, grade_prompt, retriever_type, num_neighbors, text, logger)
        
        # Run DeepEval
        predictions_d, latency_d, faithfulness, contextual_precision, contextual_recall, contextual_relevancy, hallucination, bias, toxicity, ragas = run_deep_eval(qa_chain, retriever, eval_pair, grade_prompt, retriever_type, num_neighbors, text, logger)

        # Assemble output
        d = pd.DataFrame(predictions)
        
        d['answerScore'] = [g['results'] for g in graded_answers]
        d['retrievalScore'] = [g['results'] for g in graded_retrieval]
        d['latency'] = latency

        # Summary statistics
        d['answerScore'] = [{'score': 1 if "Incorrect" not in text else 0,
                             'justification': text} for text in d['answerScore']]
        d['retrievalScore'] = [{'score': 1 if "Incorrect" not in text else 0,
                                'justification': text} for text in d['retrievalScore']]
        

        # Deepeval Dataframe
        de = pd.DataFrame(predictions_d)
        print(de.head())
        print(de.index, de.shape,faithfulness)
        de["faithfulness"] = faithfulness
        de["contextualPrecision"] = contextual_precision
        de["contextualRecall"] = contextual_recall
        de["contextualRelevancy"] = contextual_relevancy
        de["hallucination"] = hallucination
        de["bias"] = bias
        de["toxicity"] = toxicity
        de["ragas"] = ragas
        de["latency"] = latency_d


        # Convert dataframe to dict
        d_dict = d.to_dict('records')
        de_dict = de.to_dict('records')

        if len(d_dict) == 1:
            yield json.dumps({"data":  d_dict[0],"data2": de_dict[0]})
            # if(len(de_dict) == 1):
            #     yield json.dumps({"data2": de_dict[0]})
        else:
            logger.warn(
                "A QA pair was not evaluated correctly. Skipping this pair.")
            


@app.post("/evaluator-stream")
async def create_response(
    files: List[UploadFile] = File(...),
    num_eval_questions: int = Form(5),
    chunk_chars: int = Form(1000),
    overlap: int = Form(100),
    split_method: str = Form("RecursiveTextSplitter"),
    retriever_type: str = Form("similarity-search"),
    embeddings: str = Form("vertex-gecko"),
    model_version: str = Form("Gemini-1.0-pro-001"),
    grade_prompt: str = Form("Fast"),
    num_neighbors: int = Form(3),
    test_dataset: str = Form("[]"),
):
    test_dataset = json.loads(test_dataset)
    return EventSourceResponse(run_evaluator(files, num_eval_questions, chunk_chars,
                                             overlap, split_method, retriever_type, embeddings, model_version, grade_prompt, num_neighbors, test_dataset), headers={"Content-Type": "text/event-stream", "Connection": "keep-alive", "Cache-Control": "no-cache"})
