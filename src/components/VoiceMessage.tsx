import { useState, useRef } from 'react';
import { useVoiceRecorder } from 'react-use-voice-recorder';
import { MicrophoneIcon, StopIcon } from '@heroicons/react/24/outline';
import { motion } from 'framer-motion';

interface VoiceMessageProps {
  onRecordingComplete: (blob: Blob) => void;
}

export default function VoiceMessage({ onRecordingComplete }: VoiceMessageProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const timerRef = useRef<NodeJS.Timeout>();

  const { startRecording, stopRecording } = useVoiceRecorder({
    onStop: (blob) => {
      onRecordingComplete(blob);
      setRecordingTime(0);
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    },
  });

  const handleStartRecording = () => {
    setIsRecording(true);
    startRecording();
    
    // Start timer
    timerRef.current = setInterval(() => {
      setRecordingTime((prev) => prev + 1);
    }, 1000);
  };

  const handleStopRecording = () => {
    setIsRecording(false);
    stopRecording();
    
    if (timerRef.current) {
      clearInterval(timerRef.current);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="flex items-center gap-2">
      {isRecording ? (
        <motion.button
          initial={{ scale: 1 }}
          animate={{ scale: [1, 1.1, 1] }}
          transition={{ repeat: Infinity, duration: 1 }}
          onClick={handleStopRecording}
          className="p-2 bg-red-500 text-white rounded-full hover:bg-red-600"
        >
          <StopIcon className="w-6 h-6" />
        </motion.button>
      ) : (
        <button
          onClick={handleStartRecording}
          className="p-2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800"
        >
          <MicrophoneIcon className="w-6 h-6" />
        </button>
      )}
      
      {isRecording && (
        <motion.div
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          className="text-sm text-red-500 font-medium"
        >
          Recording... {formatTime(recordingTime)}
        </motion.div>
      )}
    </div>
  );
}