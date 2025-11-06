export default function ChatLog({ messages }) {
    return (
        <>
        <div className="bg-gray-100 p-4 rounded-md mt-4">
            {messages.map((m, i) => (
                <div key={i} className="mb-3">
                    <p><strong>User:</strong> {m.user}</p>
                    <p><strong>AI:</strong> {m.ai}</p>
                </div>
            ))}
        </div>
        </>
    );
}