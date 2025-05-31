import React, { useRef, useEffect } from 'react'
import Chart from 'chart.js/auto'

const RadarComparisonChart = ({ iems }) => {
  const chartRef = useRef(null)

  useEffect(() => {
    if (iems.length > 0 && chartRef.current) {
      const ctx = chartRef.current.getContext('2d')
      
      // Filter out items with invalid scores and take only first 5 for readability
      const validIems = iems.filter(iem => 
        !isNaN(iem.normalizedFloat) && 
        !isNaN(iem.toneFloat) && 
        !isNaN(iem.techFloat) &&
        iem.normalizedFloat !== null && 
        iem.toneFloat !== null && 
        iem.techFloat !== null
      ).slice(0, 5)
      
      // Nord color scheme for different IEMs
      const colors = [
        '#88c0d0', // nord8 (frost blue)
        '#b48ead', // nord15 (aurora purple)
        '#81a1c1', // nord9 (frost blue darker)
        '#a3be8c', // nord14 (aurora green)
        '#ebcb8b'  // nord13 (aurora yellow)
      ]
      
      const borderColors = [
        '#88c0d0', // nord8
        '#b48ead', // nord15
        '#81a1c1', // nord9
        '#a3be8c', // nord14
        '#ebcb8b'  // nord13
      ]
      
      const datasets = validIems.map((iem, index) => ({
        label: iem.model.length > 15 ? iem.model.substring(0, 12) + '...' : iem.model,
        data: [
          iem.normalizedFloat,
          iem.toneFloat,
          iem.techFloat,
          iem.preferenceFloat || 0 // Use 0 if preferenceFloat is not available
        ],
        backgroundColor: colors[index] + '40', // Add transparency
        borderColor: borderColors[index],
        borderWidth: 1,
        pointBackgroundColor: borderColors[index],
        pointBorderColor: '#eceff4', // nord6 (snow storm)
        pointHoverBackgroundColor: '#eceff4', // nord6
        pointHoverBorderColor: borderColors[index],
        pointRadius: 4,
        pointHoverRadius: 6
      }))
      
      const chart = new Chart(ctx, {
        type: 'radar',
        data: {
          labels: ['Overall', 'Tone', 'Technical', 'Preference'],
          datasets: datasets
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              labels: {
                color: '#e5e9f0', // nord5
                font: { size: 11, weight: '600' },
                usePointStyle: true,
                pointStyle: 'circle'
              },
              position: 'bottom'
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
            r: {
              beginAtZero: true,
              max: 10,
              grid: {
                color: 'rgba(76, 86, 106, 0.3)', // nord3
                lineWidth: 1
              },
              angleLines: {
                color: 'rgba(76, 86, 106, 0.4)', // nord3
                lineWidth: 1
              },
              ticks: {
                color: '#d8dee9', // nord4
                font: { size: 10 },
                backdropColor: 'transparent',
                stepSize: 2
              },
              pointLabels: {
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

export default RadarComparisonChart 