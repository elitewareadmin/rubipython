import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import WaveSurfer from 'wavesurfer.js';
import { supabase } from '../lib/supabase';

interface RubiDeviceProps {
  onMessage: (message: string) => void;
  onVoiceCommand: (command: string) => void;
}

export default function RubiDevice({ onMessage, onVoiceCommand }: RubiDeviceProps) {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [audioUrl, setAudioUrl] = useState('');
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
        responsive: true,
        height: 60,
      });
    }

    return () => {
      wavesurferRef.current?.destroy();
    };
  }, []);

  const startListening = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      chunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (e) => {
        chunksRef.current.push(e.data);
      };

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(chunksRef.current, { type: 'audio/webm' });
        const audioUrl = URL.createObjectURL(audioBlob);
        setAudioUrl(audioUrl);
        
        if (wavesurferRef.current) {
          wavesurferRef.current.load(audioUrl);
        }

        // Upload to Supabase
        const fileName = `voice_${Date.now()}.webm`;
        const { data, error } = await supabase.storage
          .from('voice-commands')
          .upload(fileName, audioBlob);

        if (error) {
          console.error('Error uploading voice command:', error);
          return;
        }

        // Process voice command
        const response = await fetch('/api/process-voice', {
          method: 'POST',
          body: JSON.stringify({ audioUrl: data.path }),
          headers: { 'Content-Type': 'application/json' },
        });

        const { transcript } = await response.json();
        setTranscript(transcript);
        onVoiceCommand(transcript);
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
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
          Rubi Assistant
        </h2>
        <motion.button
          whileTap={{ scale: 0.95 }}
          onClick={isListening ? stopListening : startListening}
          className={`px-6 py-3 rounded-full font-medium ${
            isListening
              ? 'bg-red-500 text-white'
              : 'bg-blue-500 text-white'
          }`}
        >
          {isListening ? 'Stop Listening' : 'Start Listening'}
        </motion.button>
      </div>

      <div className="space-y-4">
        {isListening && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center text-gray-600 dark:text-gray-300"
          >
            Listening...
          </motion.div>
        )}

        <div ref={waveformRef} className="w-full" />

        {transcript && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg"
          >
            <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">
              Transcript
            </h3>
            <p className="text-gray-900 dark:text-white">{transcript}</p>
          </motion.div>
        )}

        {audioUrl && (
          <audio controls src={audioUrl} className="w-full mt-4" />
        )}
      </div>
    </motion.div>
  );
}