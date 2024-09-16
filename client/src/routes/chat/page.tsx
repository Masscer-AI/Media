import React, { useState } from "react";
import axios from "axios";
import "./page.css";
import { Message } from "../../components/Message/Message";
import { ChatInput } from "../../components/ChatInput/ChatInput";


interface Message {
  sender: string;
  text: string;
  imageUrl?: string;
}

export default function ChatView() {
  const [messages, setMessages] = useState<Message[]>([
    {
      sender: "assistant",
      text: "response.data.response",
    },
    {
      sender: "assistant",
      text: "response.data.response",
    },
    {
      sender: "user",
      text: "response.data.response",
    },
  ]);
  const [input, setInput] = useState<string>("");

  const handleSendMessage = async () => {
    if (input.trim() === "") return;

    const userMessage: Message = { sender: "user", text: input };
    setMessages([...messages, userMessage]);

    try {
      const response = await axios.post("/get_completion/", {
        message: input,
        context: messages.map((msg) => `${msg.sender}: ${msg.text}`).join("\n"),
      });

      const assistantMessage: Message = {
        sender: "assistant",
        text: response.data.response,
      };
      setMessages([...messages, userMessage, assistantMessage]);
    } catch (error) {
      console.error("Error sending message:", error);
    }

    setInput("");
  };

  const handleGenerateSpeech = async (text: string) => {
    try {
      const response = await axios.post(
        "/generate_speech/",
        { text },
        { responseType: "blob" }
      );
      const audioBlob = new Blob([response.data], { type: "audio/mpeg" });
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      audio.play();
    } catch (error) {
      console.error("Error generating speech:", error);
    }
  };

  const handleGenerateImage = async (text: string) => {
    try {
      const response = await axios.post("/generate_image/", { prompt: text });
      const imageUrl = response.data.image_url;

      const imageMessage: Message = {
        sender: "assistant",
        text: "Generated Image",
        imageUrl,
      };
      setMessages([...messages, imageMessage]);
    } catch (error) {
      console.error("Error generating image:", error);
    }
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Enter") {
      handleSendMessage();
    }
  };

  return (
    <div className="chat-view">
      <div className="chat-messages">
        {messages.map((msg, index) => (
          <Message
            key={index}
            sender={msg.sender}
            text={msg.text}
            imageUrl={msg.imageUrl}
            onGenerateSpeech={handleGenerateSpeech}
            onGenerateImage={handleGenerateImage}
          />
        ))}
      </div>
      <ChatInput
        input={input}
        setInput={setInput}
        handleSendMessage={handleSendMessage}
        handleKeyDown={handleKeyDown}
      />
    </div>
  );
}
