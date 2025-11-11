
export default function ChatLog({ messages }) {
    // Функція для програвання аудіо
    const playAudio = (audioUrl) => {
        if (audioUrl) {
            const audioObj = new Audio(audioUrl);
            audioObj.play().catch(e => console.error("Помилка відтворення аудіо:", e));
        }
    };

    return (
        <>
        <div className="bg-gray-100 p-4 rounded-md mt-4">
            {messages.length === 0 && (
                <p className="text-gray-500 text-center">Історія чату порожня. Почніть розмову!</p>
            )}

            {messages.map((m, i) => (
                <div key={i} className="mb-4 p-3 border-b border-gray-200 last:border-b-0">
                    <p className="font-semibold text-gray-700"><strong>User:</strong> {m.user}</p>
                    <p><strong>AI:</strong> {m.ai}</p>
                </div>
            ))}
        </div>
        </>
    );
}