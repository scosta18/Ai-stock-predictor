import React from 'react';
import ReactMarkdown from 'react-markdown';
import './Reasoning.css';

function Reasoning({ text }) {
    if (!text.reasoning) {
        return null;
    }
    return (
        <div className="reasoning-box">
        <h3>Reasoning Behind Prediction</h3>
            <p>{text.reasoning}</p>
      </div>
      
    );
}

  
export default Reasoning;




