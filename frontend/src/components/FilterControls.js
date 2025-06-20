import React, { useState } from 'react';

const FilterControls = ({ filters, onFilterChange, onSearch, loading }) => {
  const [includeInput, setIncludeInput] = useState('');
  const [excludeInput, setExcludeInput] = useState('');

  const addIncludeWord = () => {
    if (includeInput.trim() && !filters.includeWords.includes(includeInput.trim())) {
      onFilterChange({
        ...filters,
        includeWords: [...filters.includeWords, includeInput.trim()]
      });
      setIncludeInput('');
    }
  };

  const addExcludeWord = () => {
    if (excludeInput.trim() && !filters.excludeWords.includes(excludeInput.trim())) {
      onFilterChange({
        ...filters,
        excludeWords: [...filters.excludeWords, excludeInput.trim()]
      });
      setExcludeInput('');
    }
  };

  const removeIncludeWord = (word) => {
    onFilterChange({
      ...filters,
      includeWords: filters.includeWords.filter(w => w !== word)
    });
  };

  const removeExcludeWord = (word) => {
    onFilterChange({
      ...filters,
      excludeWords: filters.excludeWords.filter(w => w !== word)
    });
  };

  return (
    <div className="filter-controls">
      <div className="filter-section">
        <h3>Include Words (Required)</h3>
        <div className="filter-input-group">
          <input 
            type="text"
            value={includeInput}
            onChange={(e) => setIncludeInput(e.target.value)}
            placeholder="Add word to include..."
            onKeyPress={(e) => e.key === 'Enter' && addIncludeWord()}
          />
          <button type="button" onClick={addIncludeWord}>Add</button>
        </div>
        <div className="filter-tags">
          {filters.includeWords.map(word => (
            <span key={word} className="filter-tag include-tag">
              {word}
              <button onClick={() => removeIncludeWord(word)}>×</button>
            </span>
          ))}
        </div>
      </div>

      <div className="filter-section">
        <h3>Exclude Words (Optional)</h3>
        <div className="filter-input-group">
          <input 
            type="text"
            value={excludeInput}
            onChange={(e) => setExcludeInput(e.target.value)}
            placeholder="Add word to exclude..."
            onKeyPress={(e) => e.key === 'Enter' && addExcludeWord()}
          />
          <button type="button" onClick={addExcludeWord}>Add</button>
        </div>
        <div className="filter-tags">
          {filters.excludeWords.map(word => (
            <span key={word} className="filter-tag exclude-tag">
              {word}
              <button onClick={() => removeExcludeWord(word)}>×</button>
            </span>
          ))}
        </div>
      </div>

      <div className="search-section">
        <button 
          className="search-button"
          onClick={onSearch}
          disabled={loading || filters.includeWords.length === 0}
        >
          {loading ? 'Searching...' : 'Search'}
        </button>
      </div>
    </div>
  );
};

export default FilterControls;
