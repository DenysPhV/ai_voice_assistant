import { useState } from 'react';
import axios from 'axios';


export default function VoiceRecorder({ onResponse }) {
    const [recording, setRecording] = useState(false);
    let mediaRecorder;
    
    const startRecording = async () => {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        
        const chunks = [];
        mediaRecorder.ondataavailable = e => chunks.push(e.data);
        mediaRecorder.onstop = async () => {
            const blob = new Blob(chunks, { type: 'audio/webm' });
            const file = new File([blob], 'input.webm');
            const formData = new FormData();
            formData.append('file', file);
            const res = await axios.post('http://localhost:8000/api/voice', formData);
            const { text, audio } = res.data;
            onResponse('🎙️', text, `http://localhost:8000/${audio}`);
            const audioObj = new Audio(`http://localhost:8000/${audio}`);
            audioObj.play();
        };
        mediaRecorder.start();
        setRecording(true);
    };
    
    const stopRecording = () => {
        mediaRecorder.stop();
        setRecording(false);
    };
    
    return (
       <div className="flex flex-col items-center mb-4">
         <button onClick={recording ? stopRecording : startRecording}
         className={`px-6 py-3 text-white rounded-full ${recording ? 'bg-red-500' : 'bg-green-500'}`}
         >
            {recording ? 'Stop Recording' : 'Start Recording'}
            </button>
       </div>
    );
}