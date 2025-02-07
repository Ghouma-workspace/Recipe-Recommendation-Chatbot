import React from "react";
import { marked } from "marked";

const Message = ({ text, sender }) => {
  return (
    <div className={`message ${sender}`}>
      {/* Render formatted Markdown safely */}
      <div
        className="message-text"
        dangerouslySetInnerHTML={{ __html: marked(text) }}
      />
    </div>
  );
};

export default Message;