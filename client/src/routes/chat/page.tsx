import React, { useEffect, useState } from "react";
import axios from "axios";
import "./page.css";
import { Message } from "../../components/Message/Message";
import { ChatInput } from "../../components/ChatInput/ChatInput";
import { SVGS } from "../../assets/svgs";
import { useLoaderData } from "react-router-dom";
import { Sidebar } from "../../components/Sidebar/Sidebar";

interface Message {
  sender: string;
  text: string;
  imageUrl?: string;
}

interface Model {
  name: string;
  provider: string;
}

export default function ChatView() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState<string>("");
  const [model, setModel] = useState<Model>({
    name: "gpt-4o",
    provider: "openai",
  });
  const [chatState, setChatState] = useState<{ isSidebarOpened: boolean }>({
    isSidebarOpened: false,
  });

  const loaderData = useLoaderData();

  const handleSendMessage = async () => {
    if (input.trim() === "") return;

    const userMessage: Message = { sender: "user", text: input };
    setMessages([...messages, userMessage]);

    try {
      const token = localStorage.getItem("token");
      const response = await axios.post(
        "/get_completion/",
        {
          message: input,
          context: messages
            .map((msg) => `${msg.sender}: ${msg.text}`)
            .join("\n"),
          model: model,
        },
        {
          headers: {
            Authorization: `Token ${token}`,
          },
        }
      );

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

  const handleGenerateImage = async (text: string) => {
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

  const toggleSidebar = () => {
    setChatState((prevState) => ({
      ...prevState,
      isSidebarOpened: !prevState.isSidebarOpened,
    }));
  };
  return (
    <>
      {chatState.isSidebarOpened && <Sidebar toggleSidebar={toggleSidebar} />}
      <div className="chat-container">
        <ChatHeader
          model={model}
          setModel={setModel}
          toggleSidebar={toggleSidebar}
        />
        <ChatInput
          input={input}
          setInput={setInput}
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

interface ChatHeaderProps {
  model: Model;
  setModel: React.Dispatch<React.SetStateAction<Model>>;
  toggleSidebar: () => void;
}

const ChatHeader: React.FC<ChatHeaderProps> = ({
  model,
  setModel,
  toggleSidebar,
}) => {
  const [models, setModels] = useState<Model[]>([
    { name: "gpt-4o", provider: "openai" },
    { name: "gpt-4o-mini", provider: "openai" },
  ]);

  useEffect(() => {
    getModels();
  }, []);

  const getModels = async () => {
    try {
      const response = await fetch("/get-models");
      const json = await response.json();
      const ollamaModels = json.map((model: { name: string }) => ({
        name: model.name,
        provider: "ollama",
      }));
      setModels((prevModels) => [...prevModels, ...ollamaModels]);
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
    </div>
  );
};
