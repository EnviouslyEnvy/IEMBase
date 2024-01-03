import React from 'react';
import ReactDOM from 'react-dom';
import { Route, BrowserRouter, Routes } from 'react-router-dom';
import Page from './components/Page';

import Home from './routes/Home';

ReactDOM.render(
  <React.StrictMode>
    <BrowserRouter basename={'/iembase'}>
      <Routes>
        <Route
          exact
          path='/'
          element={
            <Page title='Home'>
              <Home />
            </Page>
          }
        />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>,
  document.getElementById('root')
);