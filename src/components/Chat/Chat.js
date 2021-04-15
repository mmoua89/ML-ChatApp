import React, { useState, useEffect } from "react";
import { useHistory, useParams } from 'react-router-dom'

// Componenents
import TextContainer from '../TextContainer/TextContainer';
import Messages from '../Messages/Messages';
import InfoBar from '../InfoBar/InfoBar';
import Input from '../Input/Input';

import './Chat.css';


const Chat = ({ location }) => {
  // Read name from URL
  const name = window.location.search.split('=')[1];
  const [users, setUsers] = useState([
    { name: name }, { name: "Naive Bayes Bot" }, { name: "DNN Bot" }
  ]);
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]);

  const sendMessage = (event) => {
    event.preventDefault();
    setMessages([ ...messages, { text: message, user: name } ]);
    console.log(messages);
    console.log(message)
  }



  return (
    <div className="outerContainer">
      <div className="container">
          <InfoBar room={"SA Chat"} />
          <Messages messages={messages} name={name} />
          <Input message={message} setMessage={setMessage} sendMessage={sendMessage} />
      </div>
      <TextContainer users={users}/>
    </div>
  );
}

export default Chat;
