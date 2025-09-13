import axios from 'axios';

const BASE_URL = 'http://127.0.0.1:8000';

export const fetchStockData = async (symbol) => {
  const res = await axios.get(`${BASE_URL}/stock/${symbol}`);
  return res.data;
};

export const fetchPrediction = async (symbol) => {
  const res = await axios.get(`${BASE_URL}/predict/${symbol}`);
  return res.data;
};

export const fetchReasoning = async (symbol) => {
  const res = await axios.get(`${BASE_URL}/reasoning/${symbol}`);
  return res.data;
};
