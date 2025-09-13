import React from 'react';
import './PredictionTable.css'; // Assuming you have some CSS for styling

function PredictionTable({ prediction }) {
  if (!prediction || prediction.length === 0) {
    return null;
  }

  return (
    <div className="prediction-container">
      <h3>7-Day Stock Price Prediction</h3>
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Predicted Close</th>
          </tr>
        </thead>
        <tbody>
          {prediction.map((entry, index) => (
            <tr key={index}>
              <td>{entry.date}</td>
              <td>${entry.predicted_close}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default PredictionTable;
