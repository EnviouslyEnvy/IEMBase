import React, { useRef, useEffect } from 'react'
import Chart from 'chart.js/auto'

const ScoreDistributionChart = ({ iems }) => {
  const chartRef = useRef(null)

  useEffect(() => {
    if (iems.length > 0 && chartRef.current) {
      const ctx = chartRef.current.getContext('2d')
      
      // Create histogram bins for score distribution
      const createHistogram = (data, bins = 20) => {
        const min = Math.min(...data)
        const max = Math.max(...data)
        const binWidth = (max - min) / bins
        const binCounts = new Array(bins).fill(0)
        const binLabels = []
        
        for (let i = 0; i < bins; i++) {
          const binStart = min + i * binWidth
          const binEnd = min + (i + 1) * binWidth
          binLabels.push(`${binStart.toFixed(1)}-${binEnd.toFixed(1)}`)
          
          data.forEach(value => {
            if (value >= binStart && (value < binEnd || (i === bins - 1 && value === binEnd))) {
              binCounts[i]++
            }
          })
        }
        
        return { labels: binLabels, counts: binCounts }
      }
      
      const normalizedScores = iems.map(iem => iem.normalizedFloat).filter(score => !isNaN(score))
      const toneScores = iems.map(iem => iem.toneFloat).filter(score => !isNaN(score))
      const techScores = iems.map(iem => iem.techFloat).filter(score => !isNaN(score))
      
      const normalizedHist = createHistogram(normalizedScores)
      const toneHist = createHistogram(toneScores)
      const techHist = createHistogram(techScores)
      
      const chart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: normalizedHist.labels,
          datasets: [
            {
              label: 'Overall Score Distribution',
              data: normalizedHist.counts,
              borderColor: '#88c0d0', // nord8
              backgroundColor: 'rgba(136, 192, 208, 0.1)', // nord8 with transparency
              fill: true,
              tension: 0.4,
              borderWidth: 3
            },
            {
              label: 'Tone Score Distribution',
              data: toneHist.counts,
              borderColor: '#b48ead', // nord15 (aurora purple)
              backgroundColor: 'rgba(180, 142, 173, 0.1)', // nord15 with transparency
              fill: true,
              tension: 0.4,
              borderWidth: 3
            },
            {
              label: 'Tech Score Distribution',
              data: techHist.counts,
              borderColor: '#81a1c1', // nord9
              backgroundColor: 'rgba(129, 161, 193, 0.1)', // nord9 with transparency
              fill: true,
              tension: 0.4,
              borderWidth: 3
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          interaction: {
            intersect: false,
            mode: 'index'
          },
          plugins: {
            legend: {
              labels: {
                color: '#e5e9f0', // nord5
                font: { size: 12, weight: '600' },
                usePointStyle: true,
                pointStyle: 'circle'
              }
            },
            tooltip: {
              backgroundColor: 'rgba(46, 52, 64, 0.95)', // nord0
              titleColor: '#e5e9f0', // nord5
              bodyColor: '#d8dee9', // nord4
              borderColor: 'rgba(136, 192, 208, 0.3)', // nord8
              borderWidth: 1,
              cornerRadius: 8
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              grid: {
                color: 'rgba(76, 86, 106, 0.3)', // nord3
                lineWidth: 1
              },
              ticks: {
                color: '#d8dee9', // nord4
                font: { size: 11 }
              },
              title: {
                display: true,
                text: 'Number of IEMs',
                color: '#e5e9f0', // nord5
                font: { size: 12, weight: '600' }
              }
            },
            x: {
              grid: {
                color: 'rgba(76, 86, 106, 0.1)', // nord3 with low opacity
                lineWidth: 1
              },
              ticks: {
                color: '#d8dee9', // nord4
                font: { size: 10 },
                maxRotation: 45,
                minRotation: 45
              },
              title: {
                display: true,
                text: 'Score Range',
                color: '#e5e9f0', // nord5
                font: { size: 12, weight: '600' }
              }
            }
          }
        }
      })

      return () => chart.destroy()
    }
  }, [iems])

  return <canvas ref={chartRef} style={{ height: '400px' }} />
}

export default ScoreDistributionChart 