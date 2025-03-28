import React, { useState } from "react";
import axios from "axios";

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [message, setMessage] = useState("");
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false); // Tracks loading state

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setMessage("❌ Please select a file first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);
    setLoading(true);

    try {
      const response = await axios.post("http://127.0.0.1:8000/upload/", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setMessage(`✅ Success: ${response.data.message}`);
    } catch (error) {
      console.error("Upload error:", error);
      setMessage("❌ Error uploading file. Check console for details.");
    } finally {
      setLoading(false);
    }
  };

  const handleChat = async () => {
    if (!query) {
      setAnswer("❌ Please enter a question.");
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post("http://127.0.0.1:8000/chat/", new URLSearchParams({ query }), {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      });

      setAnswer(`🤖 AI: ${response.data.answer}`);
    } catch (error) {
      console.error("Chat error:", error);
      setAnswer("❌ Error fetching AI response. Check console.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "20px", textAlign: "center", maxWidth: "600px", margin: "auto" }}>
      <h1>🤖 AI Chatbot</h1>
      <p>Upload a PDF and ask questions!</p>

      {/* PDF Upload */}
      <input type="file" accept="application/pdf" onChange={handleFileChange} />
      <button onClick={handleUpload} disabled={loading}>
        {loading ? "Uploading..." : "Upload PDF"}
      </button>
      <p>{message}</p>

      {/* Chat Section */}
      <div style={{ marginTop: "20px" }}>
        <input
          type="text"
          placeholder="Ask a question about the PDF..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button onClick={handleChat} disabled={loading}>
          {loading ? "Thinking..." : "Ask AI"}
        </button>
      </div>

      {/* AI Response */}
      {answer && (
        <div style={{ marginTop: "20px", padding: "10px", border: "1px solid #ddd", background: "#f9f9f9" }}>
          <strong>AI Answer:</strong>
          <p>{answer}</p>
        </div>
      )}
    </div>
  );
}

export default App;
