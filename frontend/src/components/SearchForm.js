import React from 'react';

const SearchForm = ({ query, onQueryChange, onSearch, loading }) => {
  const handleSubmit = (e) => {
    e.preventDefault();
    onSearch();
  };

  return (
    <form onSubmit={handleSubmit} className="search-form">
      <div className="search-input-group">
        <input 
          type="text"
          value={query} 
          onChange={(e) => onQueryChange(e.target.value)}
          placeholder="Search for songs..."
          disabled={loading}
        />
        <button 
          type="submit" 
          disabled={loading || !query.trim()}
        >
          {loading ? 'Searching...' : 'Search'}
        </button>
      </div>
    </form>
  );
};

export default SearchForm;
