import { notifications } from "@mantine/notifications";
import { fetchEventSource } from "@microsoft/fetch-event-source";
import { API_URL, IS_DEV } from "../utils/variables";
class ActionProvider {
    constructor( createChatBotMessage, setStateFunc) {
      this.createChatBotMessage = createChatBotMessage;
      this.setState = setStateFunc;
    }


    addPosts = async function(bod) {
      const controller = new AbortController();
      var aiMessage = '';
      try {
        const requestBody = JSON.stringify({
          "message": bod
        });
        const fetchResponse = await fetchEventSource(API_URL + '/chat', {
        method: 'POST',
        body: bod,
        headers: {
          ContentType: 'application/json',
          Accept: "text/event-stream",
          Connection: "keep-alive",
        },
        openWhenHidden: true,
        signal: controller.signal,
        onmessage(ev) {
          try {
            const data_ = JSON.parse(ev.data)?.data;
            aiMessage = data_;

            
          } catch (e) {
            console.warn("Error parsing data", e);
          }
        },
  
        onclose() {
          console.log("Connection closed by the server");
        },
  
        onerror(err) {
          console.log("There was an error from server", err);
          throw new Error(err);
        },
        });
        // const data = await fetchResponse.json();

        
        const message = this.createChatBotMessage(aiMessage);
        this.addMessageToState(message);
        // return data
      }
      catch (e) {
        notifications.show({
          title: "Error",
          message: "There was an error from the server.",
          color: "red",
        });
        return;
      }
      };

  
      addMessageToState = (message) => {
        this.setState((prevState) => ({
          ...prevState,
          messages: [...prevState.messages, message],
        }));
      };
  }
  export default ActionProvider;
