import { UseFormReturn } from "react-hook-form";

export type FormValues = {
  evalQuestionsCount: number;
  chunkSize: number;
  overlap: number;
  splitMethod: string;
  embeddingAlgorithm: string;
  model: string;
  retriever: string;
  gradingPrompt: string;
  numNeighbors: number;
  files: any[];
};

export type Form = UseFormReturn<FormValues>;

export type Result = {
  question: string;
  answer: string;
  result: string;
  retrievalScore: { score: number; justification: string };
  answerScore: { score: number; justification: string };
  latency: number;
};

export type Result2 = {
  question: string;
  answer: string;
  result: string;
  faithfulness: { score: number; JUSTIFICATION: string };
  contextualPrecision: { score: number; JUSTIFICATION: string };
  contextualRecall: { score: number; JUSTIFICATION: string };
  contextualRelevancy: { score: number; JUSTIFICATION: string };
  hallucination: { score: number; JUSTIFICATION: string };
  bias: { score: number; JUSTIFICATION: string };
  toxicity: { score: number; JUSTIFICATION: string };
  latency: number;
};

export type QAPair = {
  question: string;
  answer: string;
};

export type Experiment = {
  evalQuestionsCount: number;
  chunkSize: number;
  overlap: number;
  splitMethod: string;
  retriever: string;
  embeddingAlgorithm: string;
  model: string;
  gradingPrompt: string;
  numNeighbors: number;
  avgRelevancyScore: number;
  avgAnswerScore: number;
  avgLatency: number;
  performance: number;
  id: number;
};
