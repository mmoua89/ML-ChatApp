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
    "Here's what I think about the sentiment score for your message: ",
    "I give your message a sentiment score of: ",
    "After some thinking, I would give your message a sentiment score of: ",
    "Based on what I've seen before, I would say your message has a sentiment score of: ",
    "It seems likely to me that your message has a sentiment score of: ",
    "The sentiment score I would give your message is: ",
    "I think the sentiment score of your message is: "
  ]

  // Init bots
  let NB = {
    name: "Naive Bayes Bot", 
    score: null, 
    thinking: "",
    answer: ""
  }
  let DNN = {
    name: "DNN Bot", 
    score: null,
    thinking: "",
    answer: ""
  }

  // Read name from URL on init
  const humanUser = window.location.search.split('=')[1];                          
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
  const getScoreNB = async (userMsg) => {
    params.body = JSON.stringify({ "Message" : message });
    await(                                                                                                     
      fetch(urlNB, params)
      .then((response) => response.json())
      .then((scoreData) => { NB.score = scoreData.Score})
    ) .catch((err) => { console.log(err); }); 
  }
  // Retrieve DNN sentiment prediction from ML server for the user sent text
  const getScoreDNN = async(userMsg) => {
    params.body = JSON.stringify({ "Message" : message });
    await(
      fetch(urlDNN, params)
      .then((response) => response.json())
      .then((scoreData) => { DNN.score = scoreData.Score})
    ) .catch((err) => { console.log(err); });
  }

  // Render a message to the screen
  const sendMessage = (name, msg) => {
    let currMsg = { user: name, text: msg};
    setMessages(prevMsgs => ([ ...prevMsgs, currMsg ]));    
  } 

  const respondNB = async (userMsg, callback) => {
    // Retrieve NB score from the ML prediction server for the message
    await getScoreNB(userMsg);

    // Randomly select thinking and answer responses
    NB.thinking = getResponse(thinkingMsgs, [DNN.thinking, NB.thinking]);
    NB.answer = getResponse(answerMsgs, [DNN.answer, NB.answer]);

    // Render the bots messages
    let thinkDelay = getDelay();
    let repeatDelay = thinkDelay + getDelay();
    let scoreDelay = repeatDelay + getDelay();
    setTimeout(function() { sendMessage(NB.name, NB.thinking) }, thinkDelay);               // Send thinking message
    setTimeout(function() { sendMessage(NB.name, NB.answer + NB.score) }, scoreDelay);      // Send user the sentiment score
    if(callback)
      setTimeout(function() { callback(userMsg, function(){}) }, thinkDelay);               // Call the other bot if not yet called                                 
  }

  const respondDNN = async (userMsg, callback) => {
    // Retrieve the DNN score from the ML prediction server for the message
    await getScoreDNN(userMsg);

    // Randomly select thinking and answer responses
    DNN.thinking = getResponse(thinkingMsgs, [NB.thinking, DNN.thinking]);
    DNN.answer = getResponse(answerMsgs, [NB.answer, DNN.answer]);

    // Render the bots messages
    let thinkDelay = getDelay();
    let repeatDelay = thinkDelay + getDelay();
    let scoreDelay = repeatDelay + getDelay();
    setTimeout(function() { sendMessage(DNN.name, DNN.thinking) }, thinkDelay);             // Send thinking message
    setTimeout(function() { sendMessage(DNN.name, DNN.answer + DNN.score) }, scoreDelay);   // Send user the sentiment score
    if(callback)
      setTimeout(function() { callback(userMsg, function(){}) }, thinkDelay);               // Call the other bot if not yet called                                 
  }

  const handleMessage = async (event) => {
    event.preventDefault();
    // Render user message
    let userMsg = message;
    sendMessage(humanUser, message)
    setMessage('');

    // Randomly alternate which bot responds to the message first
    if(Math.random() < 0.5){
      respondNB(userMsg, respondDNN)
    }
    else{
      respondDNN(userMsg, respondNB);
    }
  }

  // Send introduction message once user joins room
  const sendIntro = () => {
    let welcomeDelay = getDelay() / 2;
    let introDelay = welcomeDelay + getDelay();
    let scoreDelay = introDelay + getDelay();
    
    setTimeout(function() { 
      sendMessage("Admin", `Welcome to sentiment analyzer ${humanUser}!`) 
    }, welcomeDelay); 
    setTimeout(function() { 
      sendMessage("Admin", `Send a message and ${NB.name} and ${DNN.name} will try to predict 
      the sentiment of your message`) 
    }, introDelay); 
    setTimeout(function() { 
      sendMessage("Admin", "Your message will be rated with a score from 0 (negative) to 4 (positive)") 
    }, scoreDelay); 
    introSent = true;
  }

  // ----------------------------------- Rendered HTML -----------------------------------

  return (
    <div className="outerContainer">
      <div className="container">
          <InfoBar room="SA ChatML"/>
          <Messages messages={messages} name={humanUser} />
          <Input message={message} setMessage={setMessage} sendMessage={handleMessage} />
      </div>
      <TextContainer users={users}/>
    </div>
  );
}

export default Chat;
