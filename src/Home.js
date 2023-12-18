import React from 'react';
import logo from './logo.svg';
import './App.css';
import { useState } from "react";
import { Link } from 'react-router-dom';
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap/dist/js/bootstrap.bundle.min.js"

const Home = () => {
    const [inputText, setInputText] = useState("");
    const handleChange = (e) => {
        setInputText(e.target.value);
    };
    return (
        <div className="Home">
            <header className="App-header">
                <a href="/">
                    <h3 style={{ color: 'black' }}> ALGORHYTHMZ</h3>
                </a>
            </header >
            <div><img src={logo} className="App-logo" alt="logo" /></div>
            <p id="info-text">What do you want to rap about?</p>
            <p id="info-text">***One word only!***</p>
            <input onChange={handleChange} value={inputText} name="q" type="text" inputMode="search" style={{ width: '500px', height: "30px", "borderRadius": "10px", fontFamily: "sans-serif" }} />
            <h3>
                <Link className="btn btn-lg btn-outline-dark" to="/search" state={{ word: inputText }} >
                    Start
                </Link>
            </h3>
            <p id="info-text">Your lyrics are right here, waiting for you!</p>
        </div >
    );
};

export default Home;