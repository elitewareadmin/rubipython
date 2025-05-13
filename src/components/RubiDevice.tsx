import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import WaveSurfer from 'wavesurfer.js';
import { supabase } from '../lib/supabase';
import { MicrophoneIcon, StopIcon } from '@heroicons/react/24/outline';

interface RubiDeviceProps {
  onMessage: (message: string) => void;
  onVoiceCommand: (command: string) => void;
}

export default function RubiDevice({ onMessage, onVoiceCommand }: RubiDeviceProps) {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [response, setResponse] = useState('');
  const [audioUrl, setAudioUrl] = useState('');
  const [processing, setProcessing] = useState(false);
  const [provider, setProvider] = useState<'groq' | 'llama'>('groq');
  const waveformRef = useRef<HTMLDivElement>(null);
  const wavesurferRef = useRef<WaveSurfer>();
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  useEffect(() => {
    if (waveformRef.current) {
      wavesurferRef.current = WaveSurfer.create({
        container: waveformRef.current,
        waveColor: '#4F46E5',
        progressColor: '#818CF8',
        cursorColor: '#4F46E5',
        barWidth: 2,
        barRadius: 3,
        height: 60,
      });
    }

    return () => {
      wavesurferRef.current?.destroy();
    };
  }, []);

  const processWithAI = async (text: string) => {
    try {
      const response = await fetch(`${import.meta.env.VITE_SUPABASE_URL}/functions/v1/llama`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${import.meta.env.VITE_SUPABASE_ANON_KEY}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          prompt: text,
          provider 
        }),
      });

      const data = await response.json();
      return data.response;
    } catch (error) {
      console.error('Error calling AI:', error);
      return 'Sorry, I encountered an error processing your request.';
    }
  };

  const startListening = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      chunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (e) => {
        chunksRef.current.push(e.data);
      };

      mediaRecorderRef.current.onstop = async () => {
        setProcessing(true);
        const audioBlob = new Blob(chunksRef.current, { type: 'audio/webm' });
        const audioUrl = URL.createObjectURL(audioBlob);
        setAudioUrl(audioUrl);
        
        if (wavesurferRef.current) {
          wavesurferRef.current.load(audioUrl);
        }

        try {
          // Upload to Supabase Storage
          const fileName = `voice_${Date.now()}.webm`;
          const { data, error } = await supabase.storage
            .from('voice-commands')
            .upload(`public/${fileName}`, audioBlob);

          if (error) throw error;

          // Get public URL
          const { data: { publicUrl } } = supabase.storage
            .from('voice-commands')
            .getPublicUrl(`public/${fileName}`);

          // Process voice command
          const response = await fetch(`${import.meta.env.VITE_SUPABASE_URL}/functions/v1/process-voice`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${import.meta.env.VITE_SUPABASE_ANON_KEY}`,
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ audioUrl: publicUrl }),
          });

          const result = await response.json();
          setTranscript(result.transcript);
          onVoiceCommand(result.transcript);

          // Process with AI
          const aiResponse = await processWithAI(result.transcript);
          setResponse(aiResponse);

        } catch (error) {
          console.error('Error processing voice command:', error);
          setTranscript('Error processing voice command. Please try again.');
        } finally {
          setProcessing(false);
        }
      };

      mediaRecorderRef.current.start();
      setIsListening(true);
    } catch (error) {
      console.error('Error accessing microphone:', error);
    }
  };

  const stopListening = () => {
    if (mediaRecorderRef.current && isListening) {
      mediaRecorderRef.current.stop();
      setIsListening(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-lg"
    >
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <motion.div
            animate={isListening ? { scale: [1, 1.2, 1] } : {}}
            transition={{ repeat: Infinity, duration: 1 }}
            className="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center"
          >
            {isListening ? (
              <StopIcon className="w-6 h-6 text-white" />
            ) : (
              <MicrophoneIcon className="w-6 h-6 text-white" />
            )}
          </motion.div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              Rubi Assistant
            </h2>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              {isListening ? 'Listening...' : 'Click to start'}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <select
            value={provider}
            onChange={(e) => setProvider(e.target.value as 'groq' | 'llama')}
            className="px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option value="groq">Groq</option>
            <option value="llama">Llama</option>
          </select>
          <motion.button
            whileTap={{ scale: 0.95 }}
            onClick={isListening ? stopListening : startListening}
            className={`px-6 py-3 rounded-full font-medium ${
              isListening
                ? 'bg-red-500 text-white'
                : 'bg-blue-500 text-white'
            }`}
          >
            {isListening ? 'Stop' : 'Start'}
          </motion.button>
        </div>
      </div>

      <div className="space-y-4">
        <div ref={waveformRef} className="w-full" />

        {processing && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center text-gray-600 dark:text-gray-300"
          >
            Processing voice command...
          </motion.div>
        )}

        {transcript && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg"
          >
            <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">
              You said:
            </h3>
            <p className="text-gray-900 dark:text-white">{transcript}</p>
          </motion.div>
        )}

        {response && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-blue-50 dark:bg-blue-900/30 p-4 rounded-lg"
          >
            <h3 className="text-sm font-medium text-blue-500 dark:text-blue-400 mb-2">
              Rubi's response:
            </h3>
            <p className="text-gray-900 dark:text-white">{response}</p>
          </motion.div>
        )}

        {audioUrl && (
          <audio controls src={audioUrl} className="w-full mt-4" />
        )}
      </div>
    </motion.div>
  );
}
