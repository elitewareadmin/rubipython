import { useEffect, useState, useRef } from 'react';
import { supabase } from '../lib/supabase';
import { format } from 'date-fns';

interface Message {
  id: string;
  content: string;
  user_id: string;
  created_at: string;
  file_url?: string;
  file_type?: string;
}

interface UserProfile {
  id: string;
  name: string;
  avatar_url: string;
}

interface Reaction {
  message_id: string;
  user_id: string;
  reaction: string;
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [userProfiles, setUserProfiles] = useState<Record<string, UserProfile>>({});
  const [reactions, setReactions] = useState<Reaction[]>([]);
  const [typingUsers, setTypingUsers] = useState<string[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRoom, setSelectedRoom] = useState<string | null>(null);
  const [rooms, setRooms] = useState<any[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [session, setSession] = useState<any>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      if (session) {
        fetchUserProfile(session.user.id);
      }
    });

    // Subscribe to new messages, reactions, and typing status
    const channel = supabase
      .channel('chat')
      .on('presence', { event: 'sync' }, () => {
        const newTypingUsers = Object.values(channel.presenceState())
          .flat()
          .filter((user: any) => user.isTyping)
          .map((user: any) => user.user_id);
        setTypingUsers(newTypingUsers);
      })
      .on('postgres_changes', {
        event: 'INSERT',
        schema: 'public',
        table: 'chat_messages'
      }, payload => {
        const newMessage = payload.new as Message;
        setMessages(prev => [...prev, newMessage]);
        fetchUserProfile(newMessage.user_id);
      })
      .on('postgres_changes', {
        event: '*',
        schema: 'public',
        table: 'chat_reactions'
      }, () => {
        fetchReactions();
      })
      .subscribe();

    // Track user typing
    channel.track({ user_id: session?.user?.id, isTyping: false });

    fetchMessages();
    fetchRooms();
    fetchReactions();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [session]);

  const fetchUserProfile = async (userId: string) => {
    if (userProfiles[userId]) return;

    const { data } = await supabase
      .from('user_profiles')
      .select('*')
      .eq('id', userId)
      .single();

    if (data) {
      setUserProfiles(prev => ({ ...prev, [userId]: data }));
    }
  };

  const fetchMessages = async () => {
    const query = supabase
      .from('chat_messages')
      .select('*')
      .order('created_at', { ascending: true });

    if (selectedRoom) {
      query.eq('room_id', selectedRoom);
    }

    if (searchQuery) {
      query.ilike('content', `%${searchQuery}%`);
    }

    const { data, error } = await query;

    if (error) {
      console.error('Error fetching messages:', error);
      return;
    }

    setMessages(data || []);
    data?.forEach(msg => fetchUserProfile(msg.user_id));
  };

  const fetchRooms = async () => {
    const { data, error } = await supabase
      .from('chat_rooms')
      .select('*')
      .order('created_at', { ascending: true });

    if (error) {
      console.error('Error fetching rooms:', error);
      return;
    }

    setRooms(data || []);
  };

  const fetchReactions = async () => {
    const { data, error } = await supabase
      .from('chat_reactions')
      .select('*');

    if (error) {
      console.error('Error fetching reactions:', error);
      return;
    }

    setReactions(data || []);
  };

  const handleTyping = async (typing: boolean) => {
    setIsTyping(typing);
    const channel = supabase.channel('chat');
    await channel.track({ user_id: session?.user?.id, isTyping: typing });
  };

  const handleReaction = async (messageId: string, reaction: string) => {
    const { error } = await supabase
      .from('chat_reactions')
      .upsert([
        {
          message_id: messageId,
          user_id: session?.user?.id,
          reaction
        }
      ]);

    if (error) {
      console.error('Error adding reaction:', error);
    }
  };

  const handleFileUpload = async (file: File) => {
    const fileExt = file.name.split('.').pop();
    const fileName = `${Math.random()}.${fileExt}`;
    const filePath = `${session.user.id}/${fileName}`;

    const { error: uploadError } = await supabase.storage
      .from('chat-files')
      .upload(filePath, file);

    if (uploadError) {
      console.error('Error uploading file:', uploadError);
      return;
    }

    const { data: { publicUrl } } = supabase.storage
      .from('chat-files')
      .getPublicUrl(filePath);

    await handleSubmit(null, publicUrl, file.type);
  };

  const handleSubmit = async (e?: React.FormEvent, fileUrl?: string, fileType?: string) => {
    if (e) e.preventDefault();
    if (!newMessage.trim() && !fileUrl) return;

    const { error } = await supabase
      .from('chat_messages')
      .insert([
        {
          content: newMessage,
          user_id: session?.user?.id,
          room_id: selectedRoom,
          file_url: fileUrl,
          file_type: fileType
        }
      ]);

    if (error) {
      console.error('Error sending message:', error);
      return;
    }

    setNewMessage('');
    handleTyping(false);
  };

  return (
    <div className="flex h-[calc(100vh-200px)]">
      {/* Rooms sidebar */}
      <div className="w-64 bg-gray-100 p-4 border-r">
        <h2 className="text-lg font-semibold mb-4">Rooms</h2>
        <div className="space-y-2">
          {rooms.map(room => (
            <button
              key={room.id}
              onClick={() => setSelectedRoom(room.id)}
              className={`w-full text-left p-2 rounded ${
                selectedRoom === room.id ? 'bg-blue-100' : 'hover:bg-gray-200'
              }`}
            >
              {room.name}
            </button>
          ))}
        </div>
      </div>

      {/* Main chat area */}
      <div className="flex-1 flex flex-col bg-white">
        {/* Search bar */}
        <div className="p-4 border-b">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search messages..."
            className="w-full px-4 py-2 rounded-lg border focus:outline-none focus:border-blue-500"
          />
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`mb-4 ${
                message.user_id === session?.user?.id
                  ? 'ml-auto'
                  : 'mr-auto'
              }`}
            >
              <div className="flex items-start gap-2">
                <img
                  src={userProfiles[message.user_id]?.avatar_url || 'https://via.placeholder.com/40'}
                  alt="avatar"
                  className="w-8 h-8 rounded-full"
                />
                <div>
                  <div
                    className={`max-w-xs md:max-w-md rounded-lg p-3 ${
                      message.user_id === session?.user?.id
                        ? 'bg-blue-500 text-white'
                        : 'bg-gray-200 text-gray-800'
                    }`}
                  >
                    {message.file_url ? (
                      message.file_type?.startsWith('image/') ? (
                        <img src={message.file_url} alt="shared" className="max-w-full rounded" />
                      ) : (
                        <a
                          href={message.file_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 underline"
                        >
                          Download file
                        </a>
                      )
                    ) : (
                      message.content
                    )}
                  </div>
                  <div className="text-xs text-gray-500 mt-1 flex items-center gap-2">
                    <span>{format(new Date(message.created_at), 'HH:mm')}</span>
                    <div className="flex gap-1">
                      {['👍', '❤️', '😄', '😢', '😠'].map(reaction => (
                        <button
                          key={reaction}
                          onClick={() => handleReaction(message.id, reaction)}
                          className="hover:bg-gray-100 rounded px-1"
                        >
                          {reaction}
                        </button>
                      ))}
                    </div>
                  </div>
                  <div className="flex gap-1 mt-1">
                    {reactions
                      .filter(r => r.message_id === message.id)
                      .map((r, i) => (
                        <span key={i} className="bg-gray-100 rounded px-1 text-sm">
                          {r.reaction}
                        </span>
                      ))}
                  </div>
                </div>
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* Typing indicator */}
        {typingUsers.length > 0 && (
          <div className="px-4 py-2 text-sm text-gray-500">
            {typingUsers
              .map(userId => userProfiles[userId]?.name || 'Someone')
              .join(', ')}{' '}
            is typing...
          </div>
        )}

        {/* Message input */}
        <form onSubmit={handleSubmit} className="p-4 border-t">
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200"
            >
              📎
            </button>
            <input
              type="file"
              ref={fileInputRef}
              onChange={(e) => e.target.files?.[0] && handleFileUpload(e.target.files[0])}
              className="hidden"
            />
            <input
              type="text"
              value={newMessage}
              onChange={(e) => {
                setNewMessage(e.target.value);
                handleTyping(e.target.value.length > 0);
              }}
              placeholder="Type a message..."
              className="flex-1 rounded-lg border border-gray-300 p-2 focus:outline-none focus:border-blue-500"
            />
            <button
              type="submit"
              className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors"
            >
              Send
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}