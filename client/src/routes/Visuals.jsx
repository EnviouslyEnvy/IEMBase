import React, { useState, useEffect } from 'react';
import NormalizedScoresChart from './NormalizedScoresChart'; // Assuming you have this component

const Visuals = () => {
  const [iems, setIems] = useState([]);

  useEffect(() => {
    fetch('https://iembase-backend.onrender.com/data/all')
      .then((response) => response.json())
      .then((data) => {
        // Sort the data by normalizedFloat in descending order and take the top 15
        const sortedData = data
          .sort((a, b) => b.normalizedFloat - a.normalizedFloat)
          .slice(0, 15);
        setIems(sortedData);
      })
      .catch((error) => {
        console.error('Error fetching data: ', error);
      });
  }, []);

  return (
    <div>
      <h1>Top 15 IEMs</h1>
      <NormalizedScoresChart iems={iems} />
    </div>
  );
};

export default Visuals;
