// Person 3 → Display results (color, text, meaning)
import React from 'react';

const ResultDisplay = ({ results }) => {
  if (!results) return null;

  return (
    <div className="card mt-4">
      <div className="card-body">
        <h5>Analysis Results</h5>
        <p><strong>Detected Colors:</strong> {results.colors.join(', ')}</p>
        <p><strong>Text Description:</strong> {results.text}</p>
        <p><strong>Meaning/Interpretation:</strong> {results.meaning}</p>
      </div>
    </div>
  );
};

export default ResultDisplay;