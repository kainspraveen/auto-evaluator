// import {
//   useCallback,
//   useEffect,
//   useMemo,
//   useRef,
//   useState,
// } from "react";
// import {
//   Group,
//   Text,
//   useMantineTheme,
//   Alert,
//   Table,
//   Button,
//   Title,
//   Flex,
//   Stack,
//   Spoiler,
//   Progress,
//   Card,
//   ScrollArea,
//   createStyles,
// } from "@mantine/core";
// import ExperimentResultTable2 from "./tables/ExperimentResultTable2";
// import { IconUpload, IconX, IconAlertCircle } from "@tabler/icons-react";
// import { Dropzone, MIME_TYPES } from "@mantine/dropzone";
// import { Experiment, Form, QAPair, Result, Result2 } from "../utils/types";
import { notifications } from "@mantine/notifications";
import { API_URL, IS_DEV } from "../utils/variables";
import { fetchEventSource } from "@microsoft/fetch-event-source";
import ActionProvider from "./ActionProvider";
import MessageParser from "./MessageParser";
// import { Parser } from "@json2csv/plainjs";
// import { IconFile } from "@tabler/icons-react";
// import { ResponsiveScatterPlot } from "@nivo/scatterplot";
// import { isEmpty, isNil, orderBy } from "lodash";
// import TestFileUploadZone from "./TestFileUploadZone";
// import LogRocket from "logrocket";








import Chatbot from 'react-chatbot-kit'
import 'react-chatbot-kit/build/main.css'
import React, {useState, useEffect} from 'react';

import { createChatBotMessage } from 'react-chatbot-kit';
import { IconBracketsContainEnd } from '@tabler/icons-react';

const config = {
  initialMessages: [createChatBotMessage(`Hello! How can I help you?`)],
};

// export default config;



// const ActionProvider = ({ createChatBotMessage, setState, children }) => {
//   return (
//     <div>
//       {React.Children.map(children, (child) => {
//         return React.cloneElement(child, {
//           actions: {},
//         });
//       })}
//     </div>
//   );
// };

// const MessageParser = ({ children, actions }) => {
//   const parse = (message) => {
//     console.log(message);
//   };

//   return (
//     <div>
//       {React.Children.map(children, (child) => {
//         return React.cloneElement(child, {
//           parse: parse,
//           actions: {},
//         });
//       })}
//     </div>
//   );
// };

// --------------------------------------------------------------------------------------------------------------------------------------------
// Logic for connecting to the Backend
//  ENDPOINT_URL: "/evaluator-stream"
// const [posts, setPosts] = useState([]);
// const [title, setTitle] = useState('');
// const [body, setBody] = useState('');


// const addPosts = async (title, body) => {
//   await fetch(API_URL + 'evaluator-stream', {
//   method: 'POST',
//   body: JSON.stringify({
//      title: title,
//      body: body,
//      userId: Math.random().toString(36).slice(2),
//   }),
//   headers: {
//      'Content-type': 'application/json; charset=UTF-8',
//   },
//   })
//   .then((response) => response.json())
//   .then((data) => {
//      setPosts((posts) => [data, ...posts]);
//      setTitle('');
//      setBody('');
//   })
//   .catch((err) => {
//      console.log(err.message);
//   });
//   };



// const handleSubmit = (e) => {
//     e.preventDefault();
//     addPosts(title, body);
//  };    
//  onmessage(ev) {
//   try {
//     const responseMessage: string = JSON.parse(ev.data)?.data; 
//     const chatResponse = [createChatBotMessage(responseMessage)];
//   } catch (e) {
//     console.warn("Error parsing data", e);
//   }
// },
// onclose() {
//   console.log("Connection closed by the server");
//   throw new Error("No results were returned from the server.");
// },
// onerror(err) {
//   console.log("There was an error from server", err);
//   throw new Error(err);
// },




//  return (
//     // <div className="app">
//     //    <div className="add-post-container">
//     //       <form onSubmit={handleSubmit}>
//     //          <input type="text" className="form-control" value={title}
//     //             onChange={(e) => setTitle(e.target.value)}
//     //          />
//     //          <textarea name="" className="form-control" id="" cols="10" rows="8" 
//     //             value={body} onChange={(e) => setBody(e.target.value)} 
//     //          ></textarea>
//     //          <button type="submit">Add Post</button>
//     //       </form>
//     //    </div>
//     //    {/* ... */}
//     // </div>

//  );
//  };




// --------------------------------------------------------------------------------------------------------------------------------------------------

const ChatAgent = () => {
    return (
      <Chatbot
{/*         style={{
          marginTop: "100px",
          width: 800,
          overflowX: "hidden",
          height: "100%",
          paddingRight: "15px",
          paddingLeft: "5px",
          paddingTop: "15px",
        }} */}
        config={config}
        messageParser={MessageParser}
        
        
        actionProvider={ActionProvider}
      />
    
      );
};

export default ChatAgent;
