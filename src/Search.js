// Import necessary React components and hooks
import React, { useEffect, useState, useCallback } from 'react';
import { Link, useLocation } from 'react-router-dom';

// Import styles and external dependencies
import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';

// Import images
import algoRhythm1 from './images/algo_rhythm1.png';
import algoRhythm2 from './images/algo_rhythm2.png';
import algoRhythm3 from './images/algo_rhythm3.png';

// Functional component for displaying search results
const Result = () => {
    // Extract the 'word' from the location state
    const { state } = useLocation();
    const { word } = state;

    // State variables
    const [wordState, setWordState] = useState(word);
    const [error, setError] = useState(null);
    const [data, setData] = useState(null);
    const [inputText, setInputText] = useState("");

    // Handle input change
    const handleInputChange = useCallback((e) => {
        setInputText(e.target.value);
    }, []);

    // Handle button click
    const handleButtonClick = () => {
        console.log('Button clicked!');
        console.log(inputText);
        setData(null); // Clear the data
        setWordState(inputText);
        setInputText("");
    };

    // Fetch data when the component mounts or when 'wordState' changes
    useEffect(() => {
        setError(null);

        // Check if the input is empty before making a request
        if (wordState.trim() === "") {
            return;
        }

        console.log('Fetching data...');

        // Fetch data from the server
        fetch(`http://algorhythmz.pythonanywhere.com/${wordState}`, {
            method: 'POST',
        })
            .then((res) => {
                if (!res.ok) {
                    throw new Error(`HTTP error! Status: ${res.status}`);
                }
                return res.json();
            })
            .then((responseData) => {
                console.log('Data received:', responseData);
                setData(responseData);
            })
            .catch((err) => {
                console.error('Error:', err.message);
                setError(err.message);
                // Handle error gracefully, e.g., show a user-friendly message
            });
    }, [wordState]);

    // Render error message if there is an error
    if (error) {
        return (
            <div className="centered">
                <p>Error: {error}</p>
            </div>
        );
    }

    // Render loading message while data is being fetched
    if (data === null && !error) {
        return (
            <div className="centered">
                <div className="loading">
                    <div className="spinner"></div>
                    <p>Loading...</p>
                </div>
            </div>
        );
    }

    // Render search result
    return (
        <div className="Result">
            <header className="Result-header">
                <h3>
                    {/* Link to home with a black color */}
                    <Link to="/" style={{ color: 'black' }}>
                        ALGORHYTHMZ
                    </Link>
                    <div className="search-bar">
                        {/* Input for search */}
                        <input
                            onChange={handleInputChange}
                            value={inputText}
                            name="q"
                            type="text"
                            inputMode="search"
                            placeholder="Search..."
                        />
                        {/* Button for triggering the search */}
                        <button
                            className="btn btn-lg btn-outline-dark search-button"
                            onClick={handleButtonClick}
                        >
                            Search
                        </button>
                    </div>
                </h3>
            </header>

            {/* Display album image based on data.image value */}
            <img
                className="Album-image"
                id="image"
                alt="Algo Rhythm"
                src={
                    process.env.PUBLIC_URL +
                    (data.image === 1
                        ? algoRhythm1
                        : data.image === 2
                            ? algoRhythm2
                            : algoRhythm3)
                }
            />

            {/* Display song title and subtitle */}
            <div className="Song-title">{wordState}</div>
            <div className="Song-subtitle">produced by ALGORHYTHMZ</div>

            {/* Display song lyrics if data is an array */}
            <div className="Song-lyrics">
                {Array.isArray(data) &&
                    data.map((item, index) => <div key={index}>{item}</div>)}
            </div>
        </div>
    );
};

export default Result;
