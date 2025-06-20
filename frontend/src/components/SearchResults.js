import React from 'react';
import SongCard from './SongCard';

const SearchResults = ({ results, loading }) => {
  if (loading) {
    return <div className="loading">Searching...</div>;
  }

  if (results.length === 0) {
    return <div className="no-results">No results found</div>;
  }

  return (
    <div className="search-results">
      <h2>Results ({results.length})</h2>
      {results.map(song => (
        <SongCard key={song.id} song={song} />
      ))}
    </div>
  );
};

export default SearchResults;