import React from "react";
import Chatbot from "./components/Chatbot";
import "./App.css";

function App() {
  return (
    <div className="App">
      <h1 className="chatbot-title">
        🍽️ Recipe Recommendation Assistant 🤖
      </h1>

      <Chatbot />
    </div>
  );
}

export default App;