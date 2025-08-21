import React, { useState } from 'react';

const DeepSearchButton = ({ setResults }) => {
  const [loading, setLoading] = useState(false);

  const handleDeepSearch = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/deepsearch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: 'sample query' }),
      });
      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error('DeepSearch error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <button onClick={handleDeepSearch} disabled={loading}>
      {loading ? 'Searching...' : 'DeepSearch'}
    </button>
  );
};

export default DeepSearchButton;