import { useState } from "react";
import axios from "axios";

export default function ChatBox() {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState("");

  const askAI = async () => {
    const res = await axios.post("http://127.0.0.1:8000/ask", { query });
    setResponse(res.data.answer);
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow-md">
      <h2 className="text-xl font-semibold mb-4">Ask the Analyst AI</h2>
      <textarea
        rows="3"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className="w-full border rounded p-2 mb-3"
        placeholder="Ask about revenue growth, assets, or liabilities..."
      />
      <button onClick={askAI} className="bg-blue-600 text-white px-4 py-2 rounded">
        Ask
      </button>
      {response && (
        <div className="mt-3 bg-gray-50 p-3 rounded border">{response}</div>
      )}
    </div>
  );
}
