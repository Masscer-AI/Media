import React, { useEffect, useState } from "react";
import axios from "axios";
import io from "socket.io-client";
import "./page.css";
import { Message } from "../../components/Message/Message";
import { ChatInput } from "../../components/ChatInput/ChatInput";
import { SVGS } from "../../assets/svgs";
import { useLoaderData } from "react-router-dom";
import { Sidebar } from "../../components/Sidebar/Sidebar";
import { Counter, useStore } from "../../modules/store";

export type TMessage = {
  sender: string;
  text: string;
  imageUrl?: string;
};
const socket = io("http://localhost:8000");

export default function ChatView() {
  const [messages, setMessages] = useState([] as TMessage[]);


  const { chatState, toggleSidebar, input, setInput, model } = useStore();
  const loaderData = useLoaderData();

  useEffect(() => {
    socket.on("connect", () => {
      console.log("Connected to socket server");
    });

    socket.on("disconnect", () => {
      console.log("Disconnected from socket server");
    });

    return () => {
      socket.off("connect");
      socket.off("disconnect");
    };
  }, []);

  useEffect(() => {
    const updateMessages = (chunk: string) => {
      const newMessages = [...messages];
      const lastMessage = newMessages[newMessages.length - 1];

      if (lastMessage && lastMessage.sender === "assistant") {
        lastMessage.text += chunk;
      } else {
        const assistantMessage = {
          sender: "assistant",
          text: chunk,
        };
        newMessages.push(assistantMessage);
      }
      return newMessages;
    };

    socket.on("response", (data) => {
      setMessages((prevMessages) => updateMessages(data.chunk));
    });

    socket.on("responseFinished", (data) => {
      console.log("Response finished:", data);
      socket.disconnect()
    });

    return () => {
      socket.off("response");
      socket.off("responseFinished");
    };
  }, [messages]);

  const handleSendMessage = async () => {
    if (input.trim() === "") return;
    socket.connect()

    const userMessage = { sender: "user", text: input };
    setMessages([...messages, userMessage]);

    try {
      console.log(model, "MODEL IN STORE");
      

      const token = localStorage.getItem("token");
      socket.emit("message", {
        message: input,
        context: messages.map((msg) => `${msg.sender}: ${msg.text}`).join("\n"),
        model: model,
        token: token,
      });

      setInput("");
    } catch (error) {
      console.error("Error sending message:", error);
    }
  };

  const handleGenerateSpeech = async (text) => {
    try {
      const token = localStorage.getItem("token");
      const response = await axios.post(
        "/generate_speech/",
        { text },
        {
          headers: {
            Authorization: `Token ${token}`,
          },
          responseType: "blob",
        }
      );
      const audioBlob = new Blob([response.data], { type: "audio/mpeg" });
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      audio.play();
    } catch (error) {
      console.error("Error generating speech:", error);
    }
  };

  const handleGenerateImage = async (text) => {
    try {
      const token = localStorage.getItem("token");
      const response = await axios.post(
        "/generate_image/",
        { prompt: text },
        {
          headers: {
            Authorization: `Token ${token}`,
          },
        }
      );
      const imageUrl = response.data.image_url;

      const imageMessage = {
        sender: "assistant",
        text: "Generated Image",
        imageUrl,
      };
      setMessages([...messages, imageMessage]);
    } catch (error) {
      console.error("Error generating image:", error);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter") {
      handleSendMessage();
    } else {
      setInput(event.target.value);
    }
  };

  return (
    <>
      {chatState.isSidebarOpened && <Sidebar toggleSidebar={toggleSidebar} />}
      <div className="chat-container">
        <ChatHeader
          toggleSidebar={toggleSidebar}
        >
          <Counter />
        </ChatHeader>
        <ChatInput
          handleSendMessage={handleSendMessage}
          handleKeyDown={handleKeyDown}
        />
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
      </div>
    </>
  );
}

const ChatHeader = ({ toggleSidebar, children }) => {
  const { setModels, models, model, setModel } = useStore();

  useEffect(() => {
    getModels();
  }, []);

  const getModels = async () => {
    try {
      const response = await fetch("/get-models");
      const json = await response.json();
      const ollamaModels = json.map((model) => ({
        name: model.name,
        provider: "ollama",
      }));
      setModels([...models, ...ollamaModels]);
    } catch (e) {
      console.log(e);
    }
  };

  return (
    <div className="chat-header">
      <button onClick={toggleSidebar}>{SVGS.burger}</button>
      <select
        value={model.name}
        onChange={(e) => {
          const selectedModel = models.find((m) => m.name === e.target.value);
          if (selectedModel) {
            setModel(selectedModel);
          }
        }}
      >
        {models.map((modelObj, index) => (
          <option key={index} value={modelObj.name}>
            {modelObj.name} ({modelObj.provider})
          </option>
        ))}
      </select>
      <button>{SVGS.controls}</button>
      {children}
    </div>
  );
};
