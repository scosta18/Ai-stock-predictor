import React, { useState } from 'react';
import StockInput from './components/StockInput';
import StockChart from './components/StockChart';
import ReasoningBox from './components/Reasoning';
import PredictionTable from './components/PredictionTable';
import { fetchStockData, fetchPrediction, fetchReasoning } from './services/api';
import './App.css';

function App(){
const[symbol, setSymbol] = useState('');
const[historical, setHistorical] = useState([]);
const[prediction, setPrediction] = useState([]);
const[reasoning, setReasoning] = useState('');

const handleSearch =async (stockSymbol) => {
  setSymbol(stockSymbol);
  const hist = await fetchStockData(stockSymbol);
  const pred = await fetchPrediction(stockSymbol);
  const reason = await fetchReasoning(stockSymbol);

  console.log('Reasoning Data:', reason); 

  setHistorical(hist);
  setPrediction(pred);
  setReasoning(reason);
};

return(
  <div className="App">
    <h1>NextTick</h1>
    <StockInput onSearch={handleSearch}/>
    <StockChart 
    historical = {historical.slice(-7)} 
    prediction={prediction} 
    />
    <PredictionTable prediction={prediction} />
    <ReasoningBox text={reasoning} />
  </div>
);
}

export default App;