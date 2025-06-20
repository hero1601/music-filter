import React from 'react';

const SongCard = ({ song }) => {
  const formatMatchedLine = (line) => {
    // Handle different data types
    if (!line) return '';
    
    // If it's already a string, process it
    if (typeof line === 'string') {
      return line.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
    }
    
    // If it's an object with a text property
    if (typeof line === 'object' && line.text) {
      return line.text.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
    }
    
    // If it's an object with a line property
    if (typeof line === 'object' && line.line) {
      return line.line.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
    }
    
    // Convert to string as fallback
    try {
      const stringLine = String(line);
      return stringLine.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
    } catch (error) {
      console.error('Error formatting line:', line, error);
      return '';
    }
  };

  console.log(song.matched_lines)

  return (
    <div className="song-card">
      <div className="song-header">
        <h3>{song.title} - {song.artist}</h3>
        {song.external_link && (
          <a 
            href={song.external_link} 
            target="_blank" 
            rel="noopener noreferrer"
            className="song-link"
          >
            View Song
          </a>
        )}
      </div>
      
      {song.matched_lines && song.matched_lines.length > 0 && (
        <div className="matched-lines">
          <h4>Matched Lines:</h4>
          <ul>
            {song.matched_lines.slice(0,3).map((line, i) => (
              <li 
                key={i} 
                dangerouslySetInnerHTML={{ 
                  __html: line.lyric_line
                }} 
              />
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default SongCard;