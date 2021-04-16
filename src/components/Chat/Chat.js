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

  // TODO: Create a array of different thinking responses and score responses
  //       bots should randomly select from this array for variation
  // Init bots
  let NB = {
    name: "Naive Bayes Bot", score: null, 
    thinking: "Let me think about that . . .",
    scoreMsg: "Here's what I think about the sentiment score for your message: "
  }
  let DNN = {
    name: "DNN Bot", score: null,
    thinking: "Give me a second . . .",
    scoreMsg: "I give your message a sentiment score of: "
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
  // Render a message to the screen
  const sendMessage = (name, msg) => {
    let currMsg = { user: name, text: msg};
    setMessages(prevMsgs => ([ ...prevMsgs, currMsg ]));    
  } 

  // Generate a random delay between messages the bots send
  const getDelay = () => { return Math.floor(Math.random() * (1650 - 2250) ) + 2250;}

  // Retrieve NB sentiment prediction from ML server for the user sent text
  const getScoreNB = async (userMsg) => {
    params.body = JSON.stringify({ "Message" : message });
    console.log(params);
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

  const respondNB = async (userMsg, callback) => {
    let thinkDelay = getDelay();
    let repeatDelay = thinkDelay + getDelay();
    let scoreDelay = repeatDelay + getDelay();
    setTimeout(function() { sendMessage(NB.name, NB.thinking) }, thinkDelay);               // Send thinking message
    setTimeout(function() { sendMessage(NB.name, NB.scoreMsg + NB.score) }, scoreDelay);    // Send user the sentiment score
    await getScoreNB();
    if(callback)
      setTimeout(function() { callback(userMsg, function(){}) }, thinkDelay);               // Call the other bot if not yet called                                 
  }

  const respondDNN = async (userMsg, callback) => {
    let thinkDelay = getDelay();
    let repeatDelay = thinkDelay + getDelay();
    let scoreDelay = repeatDelay + getDelay();
    setTimeout(function() { sendMessage(DNN.name, DNN.thinking) }, thinkDelay);             // Send thinking message
    setTimeout(function() { sendMessage(DNN.name, DNN.scoreMsg + DNN.score) }, scoreDelay); // Send user the sentiment score
    await getScoreDNN();
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
          <InfoBar room="SA Chat"/>
          <Messages messages={messages} name={humanUser} />
          <Input message={message} setMessage={setMessage} sendMessage={handleMessage} />
      </div>
      <TextContainer users={users}/>
    </div>
  );
}

export default Chat;
