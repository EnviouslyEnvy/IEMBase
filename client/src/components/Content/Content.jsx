import React from 'react';

import styles from './css/Content.module.css';

const Content = ({ title, hr = false, children }) => {
  return (
    <>
      <h1 className={styles.ContentTitle}>{title}</h1>
      {hr && <hr className='ContentTitleHr' />}
      <p className={styles.ContentText}>{children}</p>
    </>
  );
};

export default Content;
