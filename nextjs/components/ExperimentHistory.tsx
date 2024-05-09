import React, {
    useCallback,
    useEffect,
    useMemo,
    useRef,
    useState,
  } from "react";
  import {
    Group,
    Text,
    useMantineTheme,
    Alert,
    Table,
    Button,
    Title,
    Flex,
    Stack,
    Spoiler,
    Progress,
    Card,
    ScrollArea,
    createStyles,
  } from "@mantine/core";
//   import ExperimentResultTable2 from "./tables/ExperimentResultTable2";
  import { IconUpload, IconX, IconAlertCircle } from "@tabler/icons-react";
  import { Dropzone, MIME_TYPES } from "@mantine/dropzone";
  import { Experiment, Form, QAPair, Result, Result2 } from "../utils/types";
  import { notifications } from "@mantine/notifications";
  import { API_URL, IS_DEV } from "../utils/variables";
  import { fetchEventSource } from "@microsoft/fetch-event-source";
  import { Parser } from "@json2csv/plainjs";
  import { IconFile } from "@tabler/icons-react";
  import { ResponsiveScatterPlot } from "@nivo/scatterplot";
  import { isEmpty, isNil, orderBy } from "lodash";
//   import TestFileUploadZone from "./TestFileUploadZone";
  import LogRocket from "logrocket";

const ExperimentHistory = () => {
    return (
        <ScrollArea scrollbarSize={0}>
          <Table withBorder withColumnBorders striped highlightOnHover style = {{borderCollapse: "collapse", borderTop:"1px", borderBottom:"1px"}}>
            <thead>
              <tr>
                <th>Experiment Id</th>
                <th>Data Time</th>
                <th>Avg answer Relevancy</th>
                <th> Svg Retrieval Relevancy</th>
                <th>Avg Latency (s)</th>
              </tr>
            </thead>
            
          </Table>
        </ScrollArea>
      );
};

export default ExperimentHistory;