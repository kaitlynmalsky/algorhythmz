import logo from './logo.svg';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <label>
          Text input: <input name="myInput" />
        </label>
      </header>
    </div>
  );
}

export default App;
