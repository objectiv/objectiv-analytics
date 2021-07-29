import React from 'react';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <p>
          Edit <code>src/App.tsx</code> and save to reload.
        </p>
        <button onClick={() => eval('console.log(new Error().stack)')}>Trigger eval exception</button>
      </header>
    </div>
  );
}

export default App;
