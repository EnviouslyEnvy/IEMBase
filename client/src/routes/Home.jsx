import React from 'react';
import { Col, Container, Row } from 'react-bootstrap';

// CSS
import styles from './css/Home.module.css';
import IEMCard from '../components/IEMCard/IEMCard';

// set up test vars
const firstIEM = {
  model: 'First IEM',
  normalized: 1,
};

const secondIEM = {
  model: 'mewndwop b2',
  normalized: 7.27,
  comments: 'when you',
  maxlist: 'see',
  minlist: 'it',
};

const thirdIEM = {
  model: 'oppoty L03',
  normalized: 4,
};

const Home = () => {
  return (
    <>
      <Container className={styles.containerFluid} fluid>
        <IEMCard
          model={firstIEM.model}
          normalized={firstIEM.normalized}
        ></IEMCard>
        <IEMCard
          model={secondIEM.model}
          normalized={secondIEM.normalized}
          comments={secondIEM.comments}
          maxlist={secondIEM.maxlist}
          minlist={secondIEM.minlist}
        ></IEMCard>
        <IEMCard
          model={thirdIEM.model}
          normalized={thirdIEM.normalized}
        ></IEMCard>
      </Container>
    </>
  );
};

export default Home;
