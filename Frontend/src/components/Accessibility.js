// Person 4 → Text-to-speech, large text features
import React, { useState } from 'react';

const Accessibility = ({ textToRead }) => {
  const [fontSize, setFontSize] = useState(1); // em units

  const speak = () => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(textToRead);
      speechSynthesis.speak(utterance);
    } else {
      alert('Text-to-speech not supported in this browser.');
    }
  };

  return (
    <div className="mt-4">
      <h5>Accessibility Options</h5>
      <button onClick={speak} className="btn btn-info me-2">Read Aloud</button>
      <button onClick={() => setFontSize(prev => prev + 0.5)} className="btn btn-info me-2">Increase Text Size</button>
      <button onClick={() => setFontSize(prev => Math.max(1, prev - 0.5))} className="btn btn-info">Decrease Text Size</button>
      <style>{`.large-text { font-size: ${fontSize}em; }`}</style>
    </div>
  );
};

export default Accessibility;