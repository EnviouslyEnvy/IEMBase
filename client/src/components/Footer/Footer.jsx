import React from 'react';
import './Footer.css'; // Make sure to import the CSS file

const Footer = () => {
  return (
    <div className='footer'>
      <div className='footer-half'>
        <p>
          This is a averaged list of IEMs that have received multiple reviews
          with curated comments.
          <br />
          <br />
          The sources of reviews, scores, and authors of comments are listed
          here!
          <br />
          Please check out all the sources listed, as this content could not be
          given to you without them.
        </p>
      </div>
      <div className='footer-half'>
        <p>
          <a
            href='https://www.audiodiscourse.com/p/antdroid-iem-ranking-list.html'
            target='_blank'
            rel='noopener noreferrer'
          >
            ant - Antdroid -
            https://www.audiodiscourse.com/p/antdroid-iem-ranking-list.html
          </a>
          <a
            href='https://crinacle.com/rankings/iems/'
            target='_blank'
            rel='noopener noreferrer'
          >
            ief - Crinacle - https://crinacle.com/rankings/iems/
          </a>
          <a
            href='https://docs.google.com/spreadsheets/d/1HFCuUzWdheP5qbxIJhyezJ53hvwM0wMrptVxKo49AFI/edit'
            target='_blank'
            rel='noopener noreferrer'
          >
            giz - GizAudio -
            https://docs.google.com/spreadsheets/d/1HFCuUzWdheP5qbxIJhyezJ53hvwM0wMrptVxKo49AFI/edit
          </a>
          <a
            href='https://docs.google.com/spreadsheets/d/1pUCELfWO-G33u82H42J8G_WX1odnOYBJsBNbVskQVt8/edit'
            target='_blank'
            rel='noopener noreferrer'
          >
            cog - Precogvision -
            https://docs.google.com/spreadsheets/d/1pUCELfWO-G33u82H42J8G_WX1odnOYBJsBNbVskQVt8/edit
          </a>
        </p>
      </div>
    </div>
  );
};

export default Footer;
