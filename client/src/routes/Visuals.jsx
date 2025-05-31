import React, { useState, useEffect } from 'react'
import { Container, Row, Col, Card, Nav } from 'react-bootstrap'
import config from '../config'
import TopIEMsChart from '../components/Charts/TopIEMsChart'
import WorstIEMsChart from '../components/Charts/WorstIEMsChart'
import ScoreDistributionChart from '../components/Charts/ScoreDistributionChart'
import ScatterComparisonChart from '../components/Charts/ScatterComparisonChart'
import RadarComparisonChart from '../components/Charts/RadarComparisonChart'
import styles from './css/Visuals.module.css'
import Content from '../components/Content/Content'

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
            <Col lg={6}>
              <Card className={styles.chartCard}>
                <Card.Header className={styles.cardHeader}>
                  <h5>🏆 Top 15 IEMs by Overall Score</h5>
                </Card.Header>
                <Card.Body>
                  <TopIEMsChart iems={topIems} />
                </Card.Body>
              </Card>
            </Col>
            <Col lg={6}>
              <Card className={styles.chartCard}>
                <Card.Header className={styles.cardHeader}>
                  <h5>💀 Bottom 15 IEMs by Overall Score</h5>
                </Card.Header>
                <Card.Body>
                  <WorstIEMsChart iems={worstIems} />
                </Card.Body>
              </Card>
            </Col>
          </Row>
        )
      
      case 'distribution':
        return (
          <Row className="g-4">
            <Col xl={12}>
              <Card className={styles.chartCard}>
                <Card.Header className={styles.cardHeader}>
                  <h5>📊 Score Distribution Analysis</h5>
                </Card.Header>
                <Card.Body>
                  <ScoreDistributionChart iems={allIems} />
                </Card.Body>
              </Card>
            </Col>
          </Row>
        )
      
      case 'comparison':
        return (
          <Row className="g-4">
            <Col lg={6}>
              <Card className={styles.chartCard}>
                <Card.Header className={styles.cardHeader}>
                  <h5>🎯 Tone vs Technical Performance</h5>
                </Card.Header>
                <Card.Body>
                  <ScatterComparisonChart iems={allIems} />
                </Card.Body>
              </Card>
            </Col>
            <Col lg={6}>
              <Card className={styles.chartCard}>
                <Card.Header className={styles.cardHeader}>
                  <h5>🕸️ Top 8 IEMs Radar Comparison</h5>
                </Card.Header>
                <Card.Body>
                  <RadarComparisonChart iems={topIems.slice(0, 8)} />
                </Card.Body>
              </Card>
            </Col>
          </Row>
        )
      
      default:
        return null
    }
  }

  return (
    <Container className={styles.visualsContainer} fluid>
      <Content title="IEM Data Visualizations" />
      
      <div className={styles.statsOverview}>
        <Row className="text-center">
          <Col md={3}>
            <div className={styles.statCard}>
              <h3>{allIems.length}</h3>
              <p>Total IEMs</p>
            </div>
          </Col>
          <Col md={3}>
            <div className={styles.statCard}>
              <h3>{topIems.length > 0 ? topIems[0]?.normalizedFloat?.toFixed(1) : '-'}</h3>
              <p>Highest Score</p>
            </div>
          </Col>
          <Col md={3}>
            <div className={styles.statCard}>
              <h3>{worstIems.length > 0 ? worstIems[0]?.normalizedFloat?.toFixed(1) : '-'}</h3>
              <p>Lowest Score</p>
            </div>
          </Col>
          <Col md={3}>
            <div className={styles.statCard}>
              <h3>{allIems.length > 0 ? (allIems.reduce((sum, iem) => sum + iem.normalizedFloat, 0) / allIems.length).toFixed(1) : '-'}</h3>
              <p>Average Score</p>
            </div>
          </Col>
        </Row>
      </div>

      <Nav variant="pills" className={styles.tabNavigation}>
        <Nav.Item>
          <Nav.Link 
            active={activeTab === 'overview'} 
            onClick={() => setActiveTab('overview')}
            className={styles.navLink}
          >
            📈 Overview
          </Nav.Link>
        </Nav.Item>
        <Nav.Item>
          <Nav.Link 
            active={activeTab === 'distribution'} 
            onClick={() => setActiveTab('distribution')}
            className={styles.navLink}
          >
            📊 Distribution
          </Nav.Link>
        </Nav.Item>
        <Nav.Item>
          <Nav.Link 
            active={activeTab === 'comparison'} 
            onClick={() => setActiveTab('comparison')}
            className={styles.navLink}
          >
            🔄 Comparison
          </Nav.Link>
        </Nav.Item>
      </Nav>

      <div className={styles.tabContent}>
        {renderTabContent()}
      </div>
    </Container>
  )
}

export default Visuals
