import React from 'react';
import ReactDOM from 'react-dom';
import { Route, BrowserRouter, Routes } from 'react-router-dom';
import Page from './components/Page';

import Home from './routes/Home';
import Visuals from './routes/Visuals';

import NavigationBar from './components/Navbar/NavigationBar.jsx';
import Footer from './components/Footer/Footer.jsx';

ReactDOM.render(
  <React.StrictMode>
    <BrowserRouter>
      <NavigationBar />
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
        <Route
          exact
          path='/visuals'
          element={
            <Page title='Visuals'>
              <Visuals />
            </Page>
          }
        />
      </Routes>
      <Footer />
    </BrowserRouter>
  </React.StrictMode>,
  document.getElementById('root')
);
