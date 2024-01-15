import React, { useState, useEffect } from 'react';
import { Container } from 'react-bootstrap';
import NormalizedScoresChart from '../components/NormalizedScoresChart/NormalizedScoresChart'; // Assuming you have this component
import styles from './css/Home.module.css';
import Content from '../components/Content/Content';

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
    <Container className={styles.containerFluid} fluid>
      <Content title='Top 15 IEMs by Normalized Score' hr={true}></Content>
      <NormalizedScoresChart iems={iems} />
    </Container>
  );
};

export default Visuals;
