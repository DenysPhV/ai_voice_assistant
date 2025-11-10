import { useState, useRef } from "react";
import axios from "axios";

export default function VoiceRecorder({ onResponse }) {
  const [recording, setRecording] = useState(false);
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      mediaRecorder.onstop = async () => {
        const blob = new Blob(chunksRef.current, { type: "audio/webm" });
        const file = new File([blob], "audio.webm", { type: "audio/webm" });
        const formData = new FormData();
        formData.append("file", file);

        try {
          const res = await axios.post("http://localhost:8000/api/voice", formData, {
            headers: { "Content-Type": "multipart/form-data" },
          });

           // 🔍 Безпечне розпакування відповіді
          const text = res?.data?.text ?? "Немає тексту у відповіді 😕";
          const audio = res?.data?.audio ?? null;

          if (!audio) {
            console.warn("⚠️ Бекенд не повернув поле 'audio'. Відповідь:", res.data);
            onResponse("🎙️ Ваш запит", text, null);
          }

          const cleanAudioUrl = `http://localhost:8000${audio.startsWith("/") ? audio : "/" + audio}`;
          onResponse("🎙️ Ваш запит", text, cleanAudioUrl);
          
          // Програємо аудіовідповідь
          const audioObj = new Audio(cleanAudioUrl);
          audioObj.play();

        } catch (err) {
          console.error("❌ Помилка надсилання файлу:", err);
          onResponse("🎙️ Ваш запит", "Помилка під час надсилання аудіо ⚠️", null);
        } finally {
          // Зупиняємо всі треки мікрофона
          stream.getTracks().forEach(track => track.stop());
        }
      };

      mediaRecorder.start();
      setRecording(true);
      console.log("🎙️ Запис почався...");
    } catch (err) {
      console.error("Не вдалося отримати доступ до мікрофона:", err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
      mediaRecorderRef.current.stop();
      setRecording(false);
      console.log("⏹️ Запис зупинено");
    } else {
      console.warn("⚠️ MediaRecorder не активний");
    }
  };

  return (
    <div className="flex flex-col items-center mb-4">
      <button
        onClick={recording ? stopRecording : startRecording}
        className={`px-6 py-3 text-white rounded-full ${
          recording ? "bg-red-500" : "bg-green-500"
        }`}
      >
        {recording ? "⏹️ Stop Recording" : "🎙️ Start Recording"}
      </button>
    </div>
  );
}
