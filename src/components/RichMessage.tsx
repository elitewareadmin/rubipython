import React from 'react';

interface RichMessageProps {
  content: string;
  onReaction: (emoji: string) => void;
}

const RichMessage: React.FC<RichMessageProps> = ({ content, onReaction }) => {
  const emojis = ['👍', '❤️', '😊', '🎉', '👏'];

  return (
    <div className="relative group">
      <div className="whitespace-pre-wrap break-words">{content}</div>
      
      <div className="absolute -top-8 left-0 hidden group-hover:flex bg-white dark:bg-gray-800 rounded-lg shadow-lg p-2 gap-2">
        {emojis.map((emoji) => (
          <button
            key={emoji}
            onClick={() => onReaction(emoji)}
            className="hover:scale-125 transition-transform"
          >
            {emoji}
          </button>
        ))}
      </div>
    </div>
  );
};

export default RichMessage;