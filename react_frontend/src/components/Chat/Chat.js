import React, { useState, useEffect } from "react";

// Componenents
import TextContainer from '../TextContainer/TextContainer';
import Messages from '../Messages/Messages';
import InfoBar from '../InfoBar/InfoBar';
import Input from '../Input/Input';
import './Chat.css';

// REST API endpoints to ML prediction server
const urlNB = "/api/predict/NaiveBayes";
const urlDNN = "/api/predict/DeepNeuralNet";
let introSent = false;

const Chat = ({ location }) => {

  // ----------------------------------- Initialization -----------------------------------
  useEffect(() => {
    if(!introSent)
      sendIntro()
  });

  // Possible responses to add variation to the bot's messaging
  let thinkingMsgs = [
    "Hm let's take a closer look at your message...",
    "Let me think about that...",
    "Give me a second...",
    "Let's see if I can figure this one out...",
    "Hmm I need a moment to think about this one...",
    "Let me check this one out...",
    "Give me a few seconds to figure this out..."
  ]
  let answerMsgs = [
    "Here's what I think about the sentiment of your message: ",
    "I give your message a sentiment that is: ",
    "After some thinking, I would give your message a sentiment that is: ",
    "Based on what I've seen before, I would say your message has a sentiment that is: ",
    "It seems likely to me that your message has a sentiment that is: ",
    "The sentiment I would give your message is: ",
    "I think the sentiment of your message is: "
  ]

  // Init bots
  let NB = {
    name: "Naive Bayes Bot", 
    sentiment: null, 
    thinking: "",
    answer: ""
  }
  let DNN = {
    name: "Neural Net Bot", 
    sentiment: null,
    thinking: "",
    answer: ""
  }

  // Read name from URL on init, parse space characters
  const humanUser = decodeURI(window.location.search.split('=')[1]);                        
  const [users, setUsers] = useState([
    { name: humanUser }, { name: NB.name }, { name: DNN.name }
  ]);

  // Stateful message rendering
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]);  

  // Request headers for API call to ML server for predictions
  let params = {
    method: "POST",  
    headers: { "Content-type": "application/json" },  
    body: null
  }

  // ----------------------------------- Messaging Functions -----------------------------------

  // Generate a random delay between messages the bots send
  const getDelay = () => { return Math.floor(Math.random() * (1650 - 2250) ) + 2250;}

  /* Get and return a random response from a list of responses 
      params: 
        - responses, the array of responses to randomly select from
        - notAllowed, the responses that has already been selected (by the other bot) or last iteration
  */
  const getResponse = (responses, notAllowed) => {
    let randomResponse = responses[Math.floor(Math.random() * responses.length)];
    while(notAllowed.includes(randomResponse))
      randomResponse = responses[Math.floor(Math.random() * responses.length)];
    return randomResponse;
  }

  // Retrieve NB sentiment prediction from ML server for the user sent text
  const getSentimentNB = async (userMsg) => {
    params.body = JSON.stringify({ "Message" : message });
    await(                                                                                                     
      fetch(urlNB, params)
      .then((response) => response.json())
      .then((sentimentData) => { NB.sentiment = sentimentData.Sentiment})
    ) .catch((err) => { console.log(err); }); 
  }
  // Retrieve DNN sentiment prediction from ML server for the user sent text
  const getSentimentDNN = async(userMsg) => {
    params.body = JSON.stringify({ "Message" : message });
    await(
      fetch(urlDNN, params)
      .then((response) => response.json())
      .then((sentimentData) => { DNN.sentiment = sentimentData.Sentiment})
    ) .catch((err) => { console.log(err); });
  }

  // Render a message to the screen
  const sendMessage = (name, msg) => {
    let currMsg = { user: name, text: msg};
    setMessages(prevMsgs => ([ ...prevMsgs, currMsg ]));    
  } 

  const respondNB = async (userMsg, callback) => {
    // Randomly select thinking and answer responses
    NB.thinking = getResponse(thinkingMsgs, [DNN.thinking, NB.thinking]);
    NB.answer = getResponse(answerMsgs, [DNN.answer, NB.answer]);

    // Render the bots messages
    let thinkDelay = getDelay();
    let repeatDelay = thinkDelay + getDelay();
    let sentimentDelay = repeatDelay + getDelay();
    setTimeout(function() { sendMessage(NB.name, NB.thinking) }, thinkDelay);                       // Send thinking message

    // Retrieve NB sentiment from the ML prediction server for the message
    await getSentimentNB(userMsg);

    setTimeout(function() { sendMessage(NB.name, NB.answer + NB.sentiment) }, sentimentDelay);      // Send user the sentiment
    if(callback)
      setTimeout(function() { callback(userMsg, function(){}) }, thinkDelay);                       // Call the other bot if not yet called                                 
  }

  const respondDNN = async (userMsg, callback) => {
    // Randomly select thinking and answer responses
    DNN.thinking = getResponse(thinkingMsgs, [NB.thinking, DNN.thinking]);
    DNN.answer = getResponse(answerMsgs, [NB.answer, DNN.answer]);

    // Render the bots messages
    let thinkDelay = getDelay();
    let repeatDelay = thinkDelay + getDelay();
    let sentimentDelay = repeatDelay + getDelay();
    setTimeout(function() { sendMessage(DNN.name, DNN.thinking) }, thinkDelay);                     // Send thinking message

    // Retrieve the DNN sentiment from the ML prediction server for the message
    await getSentimentDNN(userMsg);

    setTimeout(function() { sendMessage(DNN.name, DNN.answer + DNN.sentiment) }, sentimentDelay / 3);   // Send user the sentiment
    if(callback)
      setTimeout(function() { callback(userMsg, function(){}) }, thinkDelay);                       // Call the other bot if not yet called                                 
  }

  const handleMessage = async (event) => {
    event.preventDefault();
    // Render user message
    let userMsg = message;
    sendMessage(humanUser, message)
    setMessage('');

    // Temporarily disable NB for DNN testing

    // Randomly alternate which bot responds to the message first
    // if(Math.random() < 0.5){
    //   respondNB(userMsg, respondDNN)
    // }
    // else{
    //   respondDNN(userMsg, respondNB);
    // }


    respondDNN(userMsg);
  }

  // Send introduction message once user joins room
  const sendIntro = () => {
    let welcomeDelay = getDelay() / 2;
    let introDelay = welcomeDelay + getDelay();
    let sentimentDelay = introDelay + getDelay();
    
    setTimeout(function() { 
      sendMessage("Admin", `Welcome to sentiment analyzer ${humanUser}!`) 
    }, welcomeDelay); 
    setTimeout(function() { 
      sendMessage("Admin", `Send a message and ${NB.name} and ${DNN.name} will try to predict 
      the sentiment of your message`) 
    }, introDelay); 
    setTimeout(function() { 
      sendMessage("Admin", "Your message will be rated based on sentiment as either postive or negative") 
    }, sentimentDelay); 
    introSent = true;
  }

  // ----------------------------------- Rendered HTML -----------------------------------

  return (
    <div className="outerContainer">
      <div className="container">
          <InfoBar room="SA Chat.ML"/>
          <Messages messages={messages} name={humanUser} />
          <Input message={message} setMessage={setMessage} sendMessage={handleMessage} />
      </div>
      <TextContainer users={users}/>
    </div>
  );
}

export default Chat;
