import React, { useState } from 'react';
import './stockInput.css'; // Assuming you have some CSS for styling

function StockInput({onSearch}){
    const [input, setInput] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (input) onSearch(input.toUpperCase());
    };

    return (
        <form onSubmit={handleSubmit}>
            <input value={input} onChange={(e) => setInput(e.target.value)} placeholder='Enter stock symbol' />
            <button type='submit'>Search</button>
        </form>
    )
}

export default StockInput;
// This component is a simple input form that allows the user to enter a stock symbol and submit it.