import React, { useState, useEffect } from 'react';
import { Col, Container, Row } from 'react-bootstrap';

// CSS
import styles from './css/Home.module.css';
import IEMCard from '../components/IEMCard/IEMCard';

const Home = () => {
  const [iems, setIems] = useState([]);

  useEffect(() => {
    fetch('https://iembase-backend.onrender.com/data/all')
      .then((response) => response.json())
      .then((data) => {
        setIems(data);
      })
      .catch((error) => {
        console.error('Error fetching data: ', error);
      });
  }, []);

  return (
    <Container
      style={{
        display: 'flex',
        clear: 'both',
        flexWrap: 'wrap',
        paddingLeft: '3rem',
        paddingRight: '3rem',
        paddingTop: '1.5rem',
        paddingBottom: '1.5rem',
        margin: 0,
        justifyContent: 'space-between',
      }}
      fluid
    >
      {iems.map((iem, index) => (
        <IEMCard
          key={index}
          model={iem.model}
          normalized={iem.normalizedFloat}
          tone={iem.toneFloat}
          tech={iem.techFloat}
          preference={iem.preferenceFloat}
          maxcomment={iem.maxComments}
          mincomment={iem.minComments}
          maxlist={iem.maxList}
          minlist={iem.minList}
        />
      ))}
    </Container>
  );
};

export default Home;
