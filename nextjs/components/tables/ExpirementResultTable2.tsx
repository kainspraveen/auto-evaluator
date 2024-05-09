import { ScrollArea, Spoiler, Table, Text } from "@mantine/core";
import { Result2 } from "../../utils/types";
import renderPassFail from "../../utils/renderPassFail";

const ExperimentResultsTable2 = ({
  results,
  isFastGradingPrompt,
}: {
  results: any[];
  isFastGradingPrompt: boolean;
}) => {
  return (
    <ScrollArea scrollbarSize={0}>
      <Table withBorder withColumnBorders striped highlightOnHover>
        <thead>
          <tr>
            <th>Question</th>
            <th>Expected Answer</th>
            <th>Observed Answer</th>
            <th>Faithfulness</th>
            <th>Contextual Precision</th>
            <th>Contextual Recall</th>
            <th>Contextual Relevancy</th>
            <th>Contextual hellucination</th>
            <th>Contextual bias</th>
            <th>Toxicity</th>
            <th>Latency (s)</th>
          </tr>
        </thead>
        <tbody>
          {results?.map((result: Result2, index: number) => {
            return (
              <tr key={index}>
                <td>{result?.question}</td>
                {/* <td>{result?.answer}</td> */}
                <td style={{ whiteSpace: "pre-wrap" }}>
                  
                    <Spoiler
                      maxHeight={150}
                      hideLabel={
                        <Text weight="bold" color="blue">
                          Show less
                        </Text>
                      }
                      showLabel={
                        <Text weight="bold" color="blue">
                          Show more
                        </Text>
                      }
                    >
                      {result?.answer}
                    </Spoiler>
                  
                </td>
                {/* <td>{result?.result}</td> */}
                <td style={{ whiteSpace: "pre-wrap" }}>
                  
                    <Spoiler
                      maxHeight={150}
                      hideLabel={
                        <Text weight="bold" color="blue">
                          Show less
                        </Text>
                      }
                      showLabel={
                        <Text weight="bold" color="blue">
                          Show more
                        </Text>
                      }
                    >
                      {result?.result}
                    </Spoiler>
                  
                </td>
                <td style={{ whiteSpace: "pre-wrap" }}>
                  {isFastGradingPrompt ? (
                    renderPassFail(result.faithfulness)
                  ) : (
                    <Spoiler
                      maxHeight={150}
                      hideLabel={
                        <Text weight="bold" color="blue">
                          Show less
                        </Text>
                      }
                      showLabel={
                        <Text weight="bold" color="blue">
                          Show more
                        </Text>
                      }
                    >
                      {result?.faithfulness.JUSTIFICATION}
                    </Spoiler>
                  )}
                </td>
                <td style={{ whiteSpace: "pre-wrap" }}>
                  {isFastGradingPrompt ? (
                    renderPassFail(result.contextualPrecision)
                  ) : (
                    <Spoiler
                      maxHeight={150}
                      hideLabel={
                        <Text weight="bold" color="blue">
                          Show less
                        </Text>
                      }
                      showLabel={
                        <Text weight="bold" color="blue">
                          Show more
                        </Text>
                      }
                    >
                      {result?.contextualPrecision.JUSTIFICATION}
                    </Spoiler>
                  )}
                </td>
                <td style={{ whiteSpace: "pre-wrap" }}>
                  {isFastGradingPrompt ? (
                    renderPassFail(result.contextualRecall)
                  ) : (
                    <Spoiler
                      maxHeight={150}
                      hideLabel={
                        <Text weight="bold" color="blue">
                          Show less
                        </Text>
                      }
                      showLabel={
                        <Text weight="bold" color="blue">
                          Show more
                        </Text>
                      }
                    >
                      {result?.contextualRecall.JUSTIFICATION}
                    </Spoiler>
                  )}
                </td>
                <td style={{ whiteSpace: "pre-wrap" }}>
                  {isFastGradingPrompt ? (
                    renderPassFail(result.contextualRelevancy)
                  ) : (
                    <Spoiler
                      maxHeight={150}
                      hideLabel={
                        <Text weight="bold" color="blue">
                          Show less
                        </Text>
                      }
                      showLabel={
                        <Text weight="bold" color="blue">
                          Show more
                        </Text>
                      }
                    >
                      {result?.contextualRelevancy.JUSTIFICATION}
                    </Spoiler>
                  )}
                </td>
                <td style={{ whiteSpace: "pre-wrap" }}>
                  {isFastGradingPrompt ? (
                    renderPassFail(result.hallucination)
                  ) : (
                    <Spoiler
                      maxHeight={150}
                      hideLabel={
                        <Text weight="bold" color="blue">
                          Show less
                        </Text>
                      }
                      showLabel={
                        <Text weight="bold" color="blue">
                          Show more
                        </Text>
                      }
                    >
                      {result?.hallucination.JUSTIFICATION}
                    </Spoiler>
                  )}
                </td>
                <td style={{ whiteSpace: "pre-wrap" }}>
                  {isFastGradingPrompt ? (
                    renderPassFail(result.bias)
                  ) : (
                    <Spoiler
                      maxHeight={150}
                      hideLabel={
                        <Text weight="bold" color="blue">
                          Show less
                        </Text>
                      }
                      showLabel={
                        <Text weight="bold" color="blue">
                          Show more
                        </Text>
                      }
                    >
                      {result?.bias.JUSTIFICATION}
                    </Spoiler>
                  )}
                </td>
                <td style={{ whiteSpace: "pre-wrap" }}>
                  {isFastGradingPrompt ? (
                    renderPassFail(result.toxicity)
                  ) : (
                    <Spoiler
                      maxHeight={150}
                      hideLabel={
                        <Text weight="bold" color="blue">
                          Show less
                        </Text>
                      }
                      showLabel={
                        <Text weight="bold" color="blue">
                          Show more
                        </Text>
                      }
                    >
                        {/* {result?.toxicity.score} */}
                        {/* {console.log(result)} */}

                      {result?.toxicity.JUSTIFICATION}
                      
                    </Spoiler>
                  )}
                </td>
                {/* <td style={{ whiteSpace: "pre-wrap" }}>
                  {isFastGradingPrompt ? (
                    renderPassFail(result?.contextualPrecision)
                  ) : (
                    <Spoiler
                      maxHeight={150}
                      hideLabel={
                        <Text weight="bold" color="blue">
                          Show less
                        </Text>
                      }
                      showLabel={
                        <Text weight="bold" color="blue">
                          Show more
                        </Text>
                      }
                    >
                      {result?.contextualPrecision.JUSTIFICATION}
                    </Spoiler>
                  )}
                </td> */}
                <td>{result?.latency?.toFixed(3)}</td>
              </tr>
            );
          })}
        </tbody>
      </Table>
    </ScrollArea>
  );
};
export default ExperimentResultsTable2;
