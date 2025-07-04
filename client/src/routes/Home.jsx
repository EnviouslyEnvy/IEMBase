import React, { useState, useEffect } from 'react';
import { Container } from 'react-bootstrap';
import config from '../config';

// CSS
import styles from './css/Home.module.css';
import IEMCard from '../components/IEMCard/IEMCard';

const Home = () => {
  const [iems, setIems] = useState([]);

  useEffect(() => {
    fetch(`${config.API_BASE_URL}/data/all`)
      .then((response) => response.json())
      .then((data) => {
        setIems(data);
      })
      .catch((error) => {
        console.error('Error fetching data: ', error);
      });
  }, []);

  return (
    <Container className={styles.containerFluid} fluid>
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
