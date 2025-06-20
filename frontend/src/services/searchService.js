import axios from 'axios';
import config from '../config';

export const searchSongs = async (includeQuery, excludeWords = []) => {
  try {
    const params = new URLSearchParams();
    
    // Add the include parameter (required)
    params.append('include', includeQuery);
    
    // Add exclude parameters (each word as separate parameter for FastAPI List[str])
    excludeWords.forEach(word => {
      params.append('exclude', word);
    });

    const response = await axios.get(`${config.BACKEND_URL}/semantic-search?${params.toString()}`);
    
    return response.data.results || response.data || [];
  } catch (error) {
    console.error('Search service error:', error);
    throw error;
  }
};
