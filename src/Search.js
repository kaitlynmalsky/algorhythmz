import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';
import algoRhythm1 from './images/algo_rhythm1.png';
import algoRhythm2 from './images/algo_rhythm2.png';
import algoRhythm3 from './images/algo_rhythm3.png';

const Result = () => {
    const { state } = useLocation();
    const { word } = state;
    const [data, setData] = useState(null);
    const [inputText, setInputText] = useState("");
    const handleChange = (e) => {
        setInputText(e.target.value);
    };
    useEffect(() => {
        console.log('Fetching data...');
        fetch(`http://algorhythmz.pythonanywhere.com/${word}`, {
            method: 'POST',
        })
            .then((res) => res.json())
            .then((responseData) => {
                console.log('Data received:', responseData);
                setData(responseData);
            })
            .catch((err) => console.error('Error:', err));
    }, [word]);

    if (data === null) {
        return (
            <div className="centered">
                <div className="loading">
                    <div className="spinner"></div>
                    <p>Loading...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="Result">
            <header className="Result-header">
                <a href="/">
                    <h3 style={{ color: 'black' }}> ALGORHYTHMZ <div className="search-bar">
                        <input
                            onChange={handleChange}
                            value={inputText}
                            name="q"
                            type="text"
                            inputMode="search"
                            placeholder="Search..."
                        />
                    </div></h3>
                </a>
            </header>
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
            <div className="Song-title">{word}</div>
            <div className="Song-subtitle">produced by ALGORHYTHMZ</div>

            <div className="Song-lyrics">
                <>
                    {data.map((item, index) => (
                        <div key={index}>{item}</div>
                    ))}
                </>
            </div>
        </div>
    );
};

export default Result;
