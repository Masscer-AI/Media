import React from "react";
import { ChatItem } from "../../types";
import "./Messages.css";


export const ChatMessages: React.FC<{ chat: ChatItem[] }> = ({ chat }) => {
  return (
    <div className="chat">
      {chat.map((item, index) => (
        <div
          key={index}
          className={item.isUser ? "user-message" : "bot-message"}
        >
          <p>{item.text}</p>
          {item.audioSrc && (
            <audio controls autoPlay={!item.isUser} src={item.audioSrc} />
          )}
        </div>
      ))}
    </div>
  );
};
