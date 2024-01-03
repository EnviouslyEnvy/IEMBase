import React from 'react';

import styles from './IEMCard.module.css';

const IEMCard = ({
  model = 'No Model',
  normalized = 0,
  tone = 0,
  tech = 0,
  preference = 0,
  maxcomment = 'No maxcomment (Default)',
  mincomment = 'No mincomment (Default)',
  maxlist = 'nan',
  minlist = 'nan',
}) => {
  return (
    <article className={styles.IEMCard}>
      <h1>{model}</h1>
      <h4>Normalized: {normalized}</h4>
      <h4>Tone: {tone}</h4>
      <h4>Tech: {tech}</h4>
      <h4>Pref.:{preference}</h4>
      <p>
        {maxcomment} - {maxlist}
        {'\n'}
        {mincomment} - {minlist}
      </p>
    </article>
  );
};

export default IEMCard;
