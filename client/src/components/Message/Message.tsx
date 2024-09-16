import React from "react";

interface MessageProps {
  sender: string;
  text: string;
  imageUrl?: string;
  onGenerateSpeech: (text: string) => void;
  onGenerateImage: (text: string) => void;
}

export const Message: React.FC<MessageProps> = ({
  sender,
  text,
  imageUrl,
  onGenerateSpeech,
  onGenerateImage,
}) => {
  return (
    <div className={`message ${sender}`}>
      <p>{text}</p>
      {imageUrl && <img src={imageUrl} alt="Generated" />}
      <div className="message-buttons">
        <button onClick={() => onGenerateSpeech(text)}>Generate Speech</button>
        <button onClick={() => onGenerateImage(text)}>Generate Image</button>
      </div>
    </div>
  );
};
