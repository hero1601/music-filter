import React, { useState } from 'react';
import axios from 'axios';
import config from './config';

function App() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);


  const search = async () => {
    const res = await axios.get(`${config.BACKEND_URL}/search`, {
      params: { query }
    });
    setResults(res.data.results);
  };

  return (
    <div className="App">
      <h1>Lyrics Search</h1>
      <input value={query} onChange={e => setQuery(e.target.value)} />
      <button onClick={search}>Search</button>
      <div>
        {results.map(song => (
          <div key={song.id}>
            <h3>{song.title} - {song.artist}</h3>
            <ul>
              {song.matched_lines.map((line, i) => (
                <li key={i} dangerouslySetInnerHTML={{ __html: line.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>") }} />
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
