import React, { useRef, useEffect } from 'react'
import Chart from 'chart.js/auto'

const ScatterComparisonChart = ({ iems }) => {
  const chartRef = useRef(null)

  useEffect(() => {
    if (iems.length > 0 && chartRef.current) {
      const ctx = chartRef.current.getContext('2d')
      
      // Filter out items with invalid scores
      const validIems = iems.filter(iem => 
        !isNaN(iem.toneFloat) && 
        !isNaN(iem.techFloat) && 
        iem.toneFloat !== null && 
        iem.techFloat !== null
      )
      
      // Create color mapping based on overall score using Nord colors
      const getPointColor = (normalizedScore) => {
        if (normalizedScore >= 8) return '#a3be8c' // nord14 (aurora green) for excellent
        if (normalizedScore >= 6.5) return '#88c0d0' // nord8 (frost blue) for good
        if (normalizedScore >= 5) return '#ebcb8b' // nord13 (aurora yellow) for average
        return '#bf616a' // nord11 (aurora red) for poor
      }
      
      const chart = new Chart(ctx, {
        type: 'scatter',
        data: {
          datasets: [{
            label: 'IEMs by Tone vs Technical Performance',
            data: validIems.map(iem => ({
              x: iem.toneFloat,
              y: iem.techFloat,
              model: iem.model,
              overall: iem.normalizedFloat
            })),
            backgroundColor: validIems.map(iem => getPointColor(iem.normalizedFloat)),
            borderColor: validIems.map(iem => getPointColor(iem.normalizedFloat)),
            borderWidth: 2,
            pointRadius: 6,
            pointHoverRadius: 8
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              labels: {
                color: '#e5e9f0', // nord5
                font: { size: 12, weight: '600' },
                generateLabels: () => [
                  { text: 'Excellent (8.0+)', fillStyle: '#a3be8c', strokeStyle: '#a3be8c' },
                  { text: 'Good (6.5-7.9)', fillStyle: '#88c0d0', strokeStyle: '#88c0d0' },
                  { text: 'Average (5.0-6.4)', fillStyle: '#ebcb8b', strokeStyle: '#ebcb8b' },
                  { text: 'Poor (<5.0)', fillStyle: '#bf616a', strokeStyle: '#bf616a' }
                ]
              }
            },
            tooltip: {
              backgroundColor: 'rgba(46, 52, 64, 0.95)', // nord0
              titleColor: '#e5e9f0', // nord5
              bodyColor: '#d8dee9', // nord4
              borderColor: 'rgba(136, 192, 208, 0.3)', // nord8
              borderWidth: 1,
              cornerRadius: 8,
              callbacks: {
                title: (context) => context[0].raw.model,
                label: (context) => [
                  `Tone Score: ${context.parsed.x.toFixed(1)}`,
                  `Tech Score: ${context.parsed.y.toFixed(1)}`,
                  `Overall: ${context.raw.overall.toFixed(1)}`
                ]
              }
            }
          },
          scales: {
            x: {
              type: 'linear',
              position: 'bottom',
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
                text: 'Tone Score',
                color: '#e5e9f0', // nord5
                font: { size: 12, weight: '600' }
              }
            },
            y: {
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
                text: 'Technical Score',
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

export default ScatterComparisonChart 