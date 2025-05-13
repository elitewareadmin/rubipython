import React from 'react';
import VoiceMessage from './VoiceMessage';
import { MicrophoneIcon } from '@heroicons/react/24/outline';

{/* ... rest of the existing code ... */}

// Add this function inside the Chat component:
const handleVoiceMessage = async (blob: Blob) => {
  try {
    // Upload voice message to Supabase storage
    const fileName = `voice_${Date.now()}.webm`;
    const filePath = `${session.user.id}/${fileName}`;

    const { error: uploadError } = await supabase.storage
      .from('chat-files')
      .upload(filePath, blob);

    if (uploadError) {
      console.error('Error uploading voice message:', uploadError);
      return;
    }

    const { data: { publicUrl } } = supabase.storage
      .from('chat-files')
      .getPublicUrl(filePath);

    // Send message with voice file
    await handleSubmit(null, publicUrl, 'audio/webm');
  } catch (error) {
    console.error('Error handling voice message:', error);
  }
};

// Update the form in the return statement:
<form onSubmit={handleSubmit} className="p-4 border-t border-gray-200 dark:border-gray-700">
  <div className="flex items-center gap-2">
    <button
      type="button"
      onClick={() => fileInputRef.current?.click()}
      className="p-2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
    >
      <PhotoIcon className="w-6 h-6" />
    </button>
    <input
      type="file"
      ref={fileInputRef}
      onChange={(e) => e.target.files?.[0] && handleFileUpload(e.target.files[0])}
      className="hidden"
      accept="image/*,video/*,audio/*,.pdf,.doc,.docx"
    />
    <VoiceMessage onRecordingComplete={handleVoiceMessage} />
    <button
      type="button"
      onClick={() => setShowEmojiPicker(!showEmojiPicker)}
      className="p-2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
    >
      <EmojiHappyIcon className="w-6 h-6" />
    </button>
    <div className="relative flex-1">
      <input
        type="text"
        value={newMessage}
        onChange={(e) => {
          setNewMessage(e.target.value);
          handleTyping(e.target.value.length > 0);
        }}
        placeholder="Type a message..."
        className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      {showEmojiPicker && (
        <div className="absolute bottom-full right-0 mb-2">
          <Picker
            data={data}
            onEmojiSelect={(emoji: any) => {
              setNewMessage(prev => prev + emoji.native);
              setShowEmojiPicker(false);
            }}
          />
        </div>
      )}
    </div>
    <button
      type="submit"
      disabled={!newMessage.trim() && !fileInputRef.current?.files?.length}
      className="p-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
    >
      <PaperAirplaneIcon className="w-6 h-6" />
    </button>
  </div>
</form>

// Update the message rendering to handle voice messages:
{message.file_url ? (
  message.file_type?.startsWith('audio/') ? (
    <audio
      controls
      className="max-w-full"
      src={message.file_url}
    >
      Your browser does not support the audio element.
    </audio>
  ) : message.file_type?.startsWith('image/') ? (
    <img
      src={message.file_url}
      alt="shared"
      className="max-w-full rounded-lg"
    />
  ) : (
    <a
      href={message.file_url}
      target="_blank"
      rel="noopener noreferrer"
      className="flex items-center gap-2 text-blue-600 dark:text-blue-400 hover:underline"
    >
      <PaperClipIcon className="w-5 h-5" />
      Download file
    </a>
  )
) : (
  <RichMessage
    content={message.content}
    onReaction={(emoji) => handleReaction(message.id, emoji)}
  />
)}

export default handleVoiceMessage