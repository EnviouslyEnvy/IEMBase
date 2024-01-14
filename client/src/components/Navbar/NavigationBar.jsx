import React from 'react';
import { Navbar, Container, Nav } from 'react-bootstrap';
import { Link } from 'react-router-dom';

import styles from './NavigationBar.module.css';

const NavigationBar = () => {
  return (
    <Navbar
      collapseOnSelect
      expand='lg'
      variant='dark'
      fixed='top'
      className={styles.NavigationBar}
    >
      <Container className={styles.NavigationBarContainer} fluid>
        <Nav className={`${styles.Navigation} justify-content-end`}>
          <Nav.Link as={Link} className={styles.NavigationBarLink} to='/'>
            Home
          </Nav.Link>
          <Nav.Link
            as={Link}
            className={styles.NavigationBarLink}
            to='/visuals'
          >
            Visuals
          </Nav.Link>
        </Nav>
      </Container>
    </Navbar>
  );
};

export default NavigationBar;
