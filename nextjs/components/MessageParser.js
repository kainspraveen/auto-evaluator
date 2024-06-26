class MessageParser {
    constructor(actionProvider) {
      this.actionProvider = actionProvider;
    }
  
    parse(message) {
      console.log(message);
    //   const lowercase = message.toLowerCase();
      this.actionProvider.addPosts(message);
    }
  }
  
  export default MessageParser;