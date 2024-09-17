import React from "react";
import { SVGS } from "../../assets/svgs";

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
        <button onClick={() => onGenerateSpeech(text)}>{SVGS.waves}</button>
        <button onClick={() => onGenerateImage(text)}>{SVGS.image}</button>
      </div>
    </div>
  );
};
