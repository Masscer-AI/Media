import React, { useEffect } from "react";
import { SVGS } from "../../assets/svgs";
import "./ChatInput.css";

interface ChatInputProps {
  input: string;
  setInput: React.Dispatch<React.SetStateAction<string>>;
  handleSendMessage: () => void;
  handleKeyDown: (event:any) => void;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  input,
  setInput,
  handleSendMessage,
  handleKeyDown,
}) => {

  useEffect(() => {
    const url = new URL(window.location.href);
    url.searchParams.set("prompt", input);
    window.history.pushState({}, '', url.toString());
  }, [input]);

  const handlePaste = (event: React.ClipboardEvent<HTMLTextAreaElement>) => {
    const items = event.clipboardData.items;
    for (let i = 0; i < items.length; i++) {
      if (items[i].type.indexOf("image") !== -1) {
        const blob = items[i].getAsFile();
        if (blob) {
          const reader = new FileReader();
          reader.onload = (event) => {
            if (event.target) {
              const img = new Image();
              img.src = event.target.result as string;
              img.onload = () => {
                const canvas = document.createElement("canvas");
                const ctx = canvas.getContext("2d");
                if (ctx) {
                  const maxSize = 100; // Thumbnail size
                  let width = img.width;
                  let height = img.height;

                  if (width > height) {
                    if (width > maxSize) {
                      height *= maxSize / width;
                      width = maxSize;
                    }
                  } else {
                    if (height > maxSize) {
                      width *= maxSize / height;
                      height = maxSize;
                    }
                  }
                  canvas.width = width;
                  canvas.height = height;
                  ctx.drawImage(img, 0, 0, width, height);
                  const thumbnail = canvas.toDataURL("image/png");
                  console.log("Thumbnail created:", thumbnail);
                  // Aquí puedes enviar el thumbnail en una request
                }
              };
            }
          };
          reader.readAsDataURL(blob);
        }
      }
    }
  };

  return (
    <div className="chat-input">
      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        onPaste={handlePaste}
        placeholder="Type your message..."
      />
      <button onClick={handleSendMessage}>{SVGS.send}</button>
    </div>
  );
};
