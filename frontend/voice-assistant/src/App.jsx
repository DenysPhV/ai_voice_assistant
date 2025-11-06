import { useState } from 'react'
// import reactLogo from './assets/react.svg'
// import viteLogo from '/vite.svg'
import VoiceRecorder from './components/VoiceRecorder';
import ChatLog from './components/ChatLog';
import './App.css'

function App() {
  const [chat, setChat] = useState([]);

  const handleResponse = (userText, aiText, audioUrl) => {
    setChat(prev => [...prev, { user: userText, ai: aiText, audio: audioUrl }]);
  };

  return (
    <>
      <div className="p-6 max-w-3xl mx-auto">
        <h1 className="text-3xl font-bold mb-4 text-center">Voice AI Assistant</h1>
        <VoiceRecorder onResponse={handleResponse} />
        <ChatLog messages={chat} />
        </div>
    </>
  )
}

export default App;
