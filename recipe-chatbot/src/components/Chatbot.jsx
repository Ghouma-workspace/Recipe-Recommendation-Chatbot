import React, { useState } from "react";
import axios from "axios";
import Message from "./Message";

const Chatbot = () => {
  const [messages, setMessages] = useState([]); // Stores chat messages
  const [input, setInput] = useState(""); // Stores user input

  // Handle sending a message
  const handleSend = async () => {
    if (input.trim() === "") return;

    // Add user message to the chat
    setMessages((prev) => [...prev, { text: input, sender: "user" }]);
    setInput(""); // Clear input field

    try {
      // Call your backend API
      const YOUR_API_URL = "http://127.0.0.1:5000/chat";
      const response = await axios.post(YOUR_API_URL, {
        message: input,
      });

      // Add bot response to the chat
      setMessages((prev) => [
        ...prev,
        { text: response.data.response, sender: "bot" },
      ]);
    } catch (error) {
      console.error("Error fetching response from the API:", error);
      setMessages((prev) => [
        ...prev,
        { text: "Sorry, something went wrong. Please try again.", sender: "bot" },
      ]);
    }
  };

  return (
    <div className="chatbot">
      <div className="messages">
        {messages.map((msg, index) => (
          <Message key={index} text={msg.text} sender={msg.sender} />
        ))}
      </div>
      <div className="input-area">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === "Enter" && handleSend()}
          placeholder="Type your message..."
        />
        <button onClick={handleSend}>Send</button>
      </div>
    </div>
  );
};

export default Chatbot;