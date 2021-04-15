import React, { useState } from 'react';
import { Link } from "react-router-dom";

import './Join.css';

export default function SignIn() {
  const [name, setName] = useState('');
  // const [room, setRoom] = useState('');

  return (
    <div className="joinOuterContainer">
      <div className="joinInnerContainer">
        <h1 className="heading">SA Chat</h1>
        <div>
          <input placeholder="Enter your name" className="joinInput" type="text" onChange={(event) => setName(event.target.value)} />
        </div>
        {/* <div>
          <input placeholder="Room" className="joinInput mt-20" type="text" onChange={(event) => setRoom(event.target.value)} />
        </div> */}
        {/* <Link onClick={e => (!name || !room) ? e.preventDefault() : null} to={`/chat?name=${name}&room=${room}`}> */}
        <Link onClick={e => (!name) ? e.preventDefault() : null} to={`/chat?name=${name}`}>
          <button className={'button mt-20'} type="submit">Start Chatting</button>
        </Link>
      </div>
    </div>
  );
}
