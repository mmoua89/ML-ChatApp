import React, { useState } from 'react';
import { Link } from "react-router-dom";

import './Join.css';

// Submit if user presses enter key
function checkKey(event){
    if (event.key === 'Enter') {
        document.getElementById("JoinButton").click();
    }
}

export default function SignIn() {
  const [name, setName] = useState('');

  return (
    <div className="joinOuterContainer">
      <div className="joinInnerContainer">
        <h1 className="heading">SA Chat</h1>
        <div>
          <input 
            id="NameBox" placeholder="Enter your name" className="joinInput" type="text" 
            onChange={(event) => setName(event.target.value)} onKeyPress={(event) => checkKey(event)}
          />
        </div>
        <Link onClick={e => (!name) ? e.preventDefault() : null} to={`/chat?name=${name}`}>
          <button id="JoinButton" className={'button mt-20'} type="submit">Start Chatting</button>
        </Link>
      </div>
    </div>
  );
}
