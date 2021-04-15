import React, { useState, useEffect } from "react";

// Componenents
import TextContainer from '../TextContainer/TextContainer';
import Messages from '../Messages/Messages';
import InfoBar from '../InfoBar/InfoBar';
import Input from '../Input/Input';

import './Chat.css';


const Chat = ({ location }) => {
  const [name, setName] = useState('');
  const [room, setRoom] = useState('');
  const [users, setUsers] = useState('');
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]);

  const sendMessage = (event) => {
    event.preventDefault();
    console.log(message)
  }

  // Check the users list to see if the bots have been added yet
  const usersArr = Array.from(users)
  const foundDNN = usersArr.some(el => el.name === "DNN Bot");
  const foundNB = usersArr.some(el => el.name === "Naive Bayes Bot");
  
  // Add the bots only if they havent been added previously and there is atleast 1 user in the room
  if(!foundNB && usersArr.length > 0)
    users.push({id: usersArr[0].id, name: "Naive Bayes Bot", room: users[0].room})
  if(!foundDNN && usersArr.length > 0)
    users.push({id: usersArr[0].id, name: "DNN Bot", room: users[0].room})


  return (
    <div className="outerContainer">
      <div className="container">
          <InfoBar room={room} />
          <Messages messages={messages} name={name} />
          <Input message={message} setMessage={setMessage} sendMessage={sendMessage} />
      </div>
      <TextContainer users={users}/>
    </div>
  );
}

export default Chat;
