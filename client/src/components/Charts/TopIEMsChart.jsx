import React, { useRef, useEffect } from 'react'
import Chart from 'chart.js/auto'

const TopIEMsChart = ({ iems }) => {
  const chartRef = useRef(null)

  useEffect(() => {
    if (iems.length > 0 && chartRef.current) {
      const ctx = chartRef.current.getContext('2d')
      
      const chart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: iems.map(iem => iem.model.length > 20 ? iem.model.substring(0, 17) + '...' : iem.model),
          datasets: [
            {
              label: 'Overall Score',
              data: iems.map(iem => iem.normalizedFloat),
              backgroundColor: '#8fbcbb', // nord7
              borderColor: '#88c0d0', // nord8
              borderWidth: 0,
              borderRadius: 6,
              borderSkipped: false,
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              labels: {
                color: '#e5e9f0', // nord5
                font: { size: 12, weight: '600' }
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
                title: (context) => iems[context[0].dataIndex].model,
                label: (context) => `Score: ${context.parsed.y.toFixed(1)}`
              }
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
              }
            },
            x: {
              grid: {
                display: false
              },
              ticks: {
                color: '#d8dee9', // nord4
                font: { size: 10 },
                maxRotation: 45,
                minRotation: 45
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

export default TopIEMsChart 