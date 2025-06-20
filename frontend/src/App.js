import React, { useState } from 'react';
import FilterControls from './components/FilterControls';
import SearchResults from './components/SearchResults';
import { searchSongs } from './services/searchService';

function App() {
  const [results, setResults] = useState([]);
  const [filters, setFilters] = useState({
    includeWords: [],
    excludeWords: []
  });
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    // All include words combined
    const allIncludeWords = filters.includeWords
      .filter(word => word && word.trim())
      .join(' ')
      .trim();
    
    console.log('Include words:', filters.includeWords);
    console.log('Combined include:', allIncludeWords);
    console.log('Exclude words:', filters.excludeWords);
    
    if (!allIncludeWords) {
      alert('Please add at least one word to include');
      return;
    }
    
    setLoading(true);
    try {
      const searchResults = await searchSongs(allIncludeWords, filters.excludeWords);
      setResults(searchResults);
    } catch (error) {
      console.error('Search failed:', error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
  };

  return (
    <div className="App">
      <h1>Semantic Music Search</h1>
      
      <FilterControls 
        filters={filters}
        onFilterChange={handleFilterChange}
        onSearch={handleSearch}
        loading={loading}
      />
      
      <SearchResults 
        results={results}
        loading={loading}
      />
    </div>
  );
}

export default App;