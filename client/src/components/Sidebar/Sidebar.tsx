import React, { useEffect, useState } from "react";
import axios from "axios";
import "./Sidebar.css";
import { SVGS } from "../../assets/svgs";

interface Conversation {
  id: number;
  user_id: number;
  message_count: number;
}

interface SidebarProps {
  toggleSidebar: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ toggleSidebar }) => {
  const [conversations, setConversations] = useState<Conversation[]>([]);

  useEffect(() => {
    populateHistory();
  }, []);

  const populateHistory = async () => {
    const token = localStorage.getItem("token");
    if (!token) {
      console.error("No token found in localStorage");
      return;
    }

    try {
      const res = await axios.get<Conversation[]>("/conversations", {
        headers: {
          Authorization: `Token ${token}`,
        },
      });

      const conversations = res.data;
      setConversations(conversations); // Update state with fetched conversations
    } catch (error) {
      console.error("Failed to fetch conversations", error);
    }
  };

  return (
    <div className="sidebar">
      <div>
        <button>New chat</button>
        <button onClick={toggleSidebar}>{SVGS.burger}</button>
      </div>
      <div>Historial</div>
      <div>
        {conversations.map((conversation) => (
          <div key={conversation.id}>
            Conversation ID: {conversation.id}, Messages: {conversation.message_count}
          </div>
        ))}
      </div>
    </div>
  );
};
