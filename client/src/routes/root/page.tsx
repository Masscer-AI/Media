import React, { useState, useEffect } from "react";
import { Navbar } from "../../components/Navbar/Navbar";
import { Talkie } from "../../components/Talkie/Talkie";

import { ChatItem } from "../../types";
import { ChatMessages } from "../../components/Messages/Messages";

export default function Root() {
  const [chat, setChat] = useState<ChatItem[]>([]);

  const processAudioExample = async (
    audioFile: Blob,
    transcription: string
  ) => {
    const formData = new FormData();
    formData.append("file", audioFile, "audiofile.wav");

    try {
      const response = await fetch("/upload-audio/", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        // Create a URL for the audio file
        const audioUrl = URL.createObjectURL(audioFile);
        // Usar la transcripción que llega del servidor
        setChat((prevChat) => [
          ...prevChat,
          { text: data.transcription, audioSrc: audioUrl, isUser: true },
        ]);
        await getCompletion(data.transcription, audioFile);
      } else {
        console.error("Failed to upload audio file");
      }
    } catch (error) {
      console.error("Error uploading audio file:", error);
    }
  };

  const getCompletion = async (transcription: string, audioFile: Blob) => {
    try {
      const context = chat
        .slice(-6)
        .map((item) => `${item.isUser ? "user" : "ai"}: ${item.text}`)
        .join("\n");
      const completionResponse = await fetch("/get_completion/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: transcription, context }),
      });

      if (completionResponse.ok) {
        const completionData = await completionResponse.json();
        console.log("Completion from server:", completionData.response);
        await generateSpeech(completionData.response, audioFile);
      } else {
        console.error("Failed to get completion");
      }
    } catch (error) {
      console.error("Error getting completion:", error);
    }
  };

  const generateSpeech = async (text: string, audioFile: Blob) => {
    try {
      const response = await fetch("/generate_speech/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text }),
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        setChat((prevChat) => [
          ...prevChat,
          { text, audioSrc: url, isUser: false },
        ]);
      } else {
        console.error("Failed to generate speech");
      }
    } catch (error) {
      console.error("Error generating speech:", error);
    }
  };

  return (
    <>
      <Navbar />
      <ChatMessages chat={chat} />

      <Talkie processAudio={processAudioExample} />
    </>
  );
}
