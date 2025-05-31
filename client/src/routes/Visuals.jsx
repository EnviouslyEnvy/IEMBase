import React, { useState, useEffect } from 'react'
import { Container, Row, Col, Nav } from 'react-bootstrap'
import config from '../config'
import TopIEMsChart from '../components/Charts/TopIEMsChart'
import WorstIEMsChart from '../components/Charts/WorstIEMsChart'
import ScoreDistributionChart from '../components/Charts/ScoreDistributionChart'
import ScatterComparisonChart from '../components/Charts/ScatterComparisonChart'
import RadarComparisonChart from '../components/Charts/RadarComparisonChart'
import styles from './css/Visuals.module.css'

const Visuals = () => {
  const [allIems, setAllIems] = useState([])
  const [topIems, setTopIems] = useState([])
  const [worstIems, setWorstIems] = useState([])
  const [activeTab, setActiveTab] = useState('overview')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true)
        const response = await fetch(`${config.API_BASE_URL}/data/all`)
        const data = await response.json()
        
        // Filter out items without valid scores
        const validIems = data.filter(iem => 
          iem.normalizedFloat && 
          !isNaN(iem.normalizedFloat) && 
          iem.model && 
          iem.model !== 'nan'
        )
        
        // Sort by normalized score
        const sortedData = [...validIems].sort((a, b) => b.normalizedFloat - a.normalizedFloat)
        
        setAllIems(validIems)
        setTopIems(sortedData.slice(0, 15))
        setWorstIems(sortedData.slice(-15).reverse()) // Get bottom 15, reverse to show worst first
      } catch (error) {
        console.error('Error fetching data:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchData()
  }, [])

  const renderTabContent = () => {
    if (isLoading) {
      return (
        <div className={styles.loadingContainer}>
          <div className={styles.spinner}></div>
          <p>Loading IEM data...</p>
        </div>
      )
    }

    switch (activeTab) {
      case 'overview':
        return (
          <Row className="g-4">
            <Col lg={6} className={styles.chartColumn}>
              <div className={styles.chartContainer}>
                <h5 className={styles.chartTitle}>Top 15 IEMs by Overall Score</h5>
                <TopIEMsChart iems={topIems} />
              </div>
            </Col>
            <Col lg={6} className={styles.chartColumn}>
              <div className={styles.chartContainer}>
                <h5 className={styles.chartTitle}>Bottom 15 IEMs by Overall Score</h5>
                <WorstIEMsChart iems={worstIems} />
              </div>
            </Col>
          </Row>
        )
      
      case 'distribution':
        return (
          <Row className="g-4">
            <Col xl={12} className={styles.chartColumn}>
              <div className={styles.chartContainer}>
                <h5 className={styles.chartTitle}>Score Distribution Analysis</h5>
                <ScoreDistributionChart iems={allIems} />
              </div>
            </Col>
          </Row>
        )
      
      case 'comparison':
        return (
          <Row className="g-4">
            <Col lg={6} className={styles.chartColumn}>
              <div className={styles.chartContainer}>
                <h5 className={styles.chartTitle}>Tone vs Technical Performance</h5>
                <ScatterComparisonChart iems={allIems} />
              </div>
            </Col>
            <Col lg={6} className={styles.chartColumn}>
              <div className={styles.chartContainer}>
                <h5 className={styles.chartTitle}>Top 8 IEMs Radar Comparison</h5>
                <RadarComparisonChart iems={topIems.slice(0, 8)} />
              </div>
            </Col>
          </Row>
        )
      
      default:
        return null
    }
  }

  return (
    <Container className={styles.visualsContainer} fluid>
      <div className={styles.statsOverview}>
        <div className={styles.statsRow}>
          <div className={styles.statCard}>
            <h3>{allIems.length}</h3>
            <p>Total IEMs</p>
          </div>
          <div className={styles.statCard}>
            <h3>{topIems.length > 0 ? topIems[0]?.normalizedFloat?.toFixed(1) : '-'}</h3>
            <p>Highest Score</p>
          </div>
          <div className={styles.statCard}>
            <h3>{worstIems.length > 0 ? worstIems[0]?.normalizedFloat?.toFixed(1) : '-'}</h3>
            <p>Lowest Score</p>
          </div>
          <div className={styles.statCard}>
            <h3>{allIems.length > 0 ? (allIems.reduce((sum, iem) => sum + iem.normalizedFloat, 0) / allIems.length).toFixed(1) : '-'}</h3>
            <p>Average Score</p>
          </div>
        </div>
      </div>

      <Row className={styles.tabNavigationRow}>
        <Col md={4}>
          <button 
            className={`${styles.tabButton} ${activeTab === 'overview' ? styles.active : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            Overview
          </button>
        </Col>
        <Col md={4}>
          <button 
            className={`${styles.tabButton} ${activeTab === 'distribution' ? styles.active : ''}`}
            onClick={() => setActiveTab('distribution')}
          >
            Distribution
          </button>
        </Col>
        <Col md={4}>
          <button 
            className={`${styles.tabButton} ${activeTab === 'comparison' ? styles.active : ''}`}
            onClick={() => setActiveTab('comparison')}
          >
            Comparison
          </button>
        </Col>
      </Row>

      <div className={styles.tabContent}>
        {renderTabContent()}
      </div>
    </Container>
  )
}

export default Visuals
