import React from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend } from 'recharts';
import './StockChart.css';


function StockChart({ historical, prediction }) {
  const data = [
    ...historical.map(d => ({
      date: d.Date,
      close: d.Close,
      predicted: null
    })),
    ...prediction.map(p => ({
      date: p.date,
      close: null,
      predicted: p.predicted_close
    }))
  ];

  return (
    <div className="chart-container">
      <LineChart width={800} height={400} data={data}>
        <XAxis dataKey="date" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="close" stroke="#8884d8" name="Actual" />
        <Line type="monotone" dataKey="predicted" stroke="#82ca9d" name="Predicted" />
      </LineChart>
    </div>
  );
  
}

export default StockChart;
// This component uses the Recharts library to create a line chart that displays both the actual and predicted stock prices over time. The data is passed as props from the parent component (App.js).