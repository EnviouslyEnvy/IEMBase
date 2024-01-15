import React from 'react';

import styles from './Content.module.css';

const Content = ({ title, children }) => {
  return (
    <>
      <h1 className={styles.ContentTitle}>{title}</h1>
      <p className={styles.ContentText}>{children}</p>
    </>
  );
};

export default Content;
