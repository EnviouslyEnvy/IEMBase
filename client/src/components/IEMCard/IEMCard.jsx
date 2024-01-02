import React from 'react';

import styles from './IEMCard.module.css';

const IEMCard = ({
  model = 'No Model',
  normalized = 0,
  tone = 0,
  tech = 0,
  preference = 0,
  comments = 'No Comments (Default)',
  maxlist = 'nan',
  minlist = 'nan',
}) => {
  console.log({
    model,
    normalized,
    tone,
    tech,
    preference,
    comments,
    maxlist,
    minlist,
  });
  return (
    <article className={styles.IEMCard}>
      <h1>{model}</h1>
      <h4>Normalized: {normalized}</h4>
      <h4>Tone: {tone}</h4>
      <h4>Tech: {tech}</h4>
      <h4>Pref.:{preference}</h4>
      <p>
        {comments} - {maxlist} & {minlist}
      </p>
    </article>
  );
};

export default IEMCard;
