import React, { useRef, useEffect } from 'react'
import Chart from 'chart.js/auto'

const PricePerformanceChart = ({ iems }) => {
  const chartRef = useRef(null)

  useEffect(() => {
    if (iems.length > 0 && chartRef.current) {
      const ctx = chartRef.current.getContext('2d')
      
      // Filter items with valid price and score data
      const validIems = iems.filter(iem => 
        !isNaN(iem.normalizedFloat) && 
        !isNaN(iem.price) && 
        iem.price !== null && 
        iem.price > 0 &&
        iem.normalizedFloat !== null
      )
      
      // Create price ranges for better visualization
      const priceRanges = [
        { min: 0, max: 100, label: '$0-100', color: 'rgba(46, 204, 113, 0.7)' },
        { min: 100, max: 300, label: '$100-300', color: 'rgba(52, 152, 219, 0.7)' },
        { min: 300, max: 600, label: '$300-600', color: 'rgba(241, 196, 15, 0.7)' },
        { min: 600, max: 1200, label: '$600-1200', color: 'rgba(230, 126, 34, 0.7)' },
        { min: 1200, max: Infinity, label: '$1200+', color: 'rgba(231, 76, 60, 0.7)' }
      ]
      
      const datasets = priceRanges.map(range => {
        const iemsInRange = validIems.filter(iem => 
          iem.price >= range.min && iem.price < range.max
        )
        
        return {
          label: range.label,
          data: iemsInRange.map(iem => ({
            x: iem.price,
            y: iem.normalizedFloat,
            model: iem.model
          })),
          backgroundColor: range.color,
          borderColor: range.color.replace('0.7', '1'),
          borderWidth: 2,
          pointRadius: 5,
          pointHoverRadius: 7
        }
      }).filter(dataset => dataset.data.length > 0) // Only include ranges with data
      
      const chart = new Chart(ctx, {
        type: 'scatter',
        data: { datasets },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              labels: {
                color: '#e8e9f0',
                font: { size: 12, weight: '600' },
                usePointStyle: true,
                pointStyle: 'circle'
              }
            },
            tooltip: {
              backgroundColor: 'rgba(26, 26, 46, 0.95)',
              titleColor: '#e8e9f0',
              bodyColor: '#b8bcc8',
              borderColor: 'rgba(148, 190, 206, 0.3)',
              borderWidth: 1,
              cornerRadius: 8,
              callbacks: {
                title: (context) => context[0].raw.model,
                label: (context) => [
                  `Price: $${context.parsed.x.toLocaleString()}`,
                  `Score: ${context.parsed.y.toFixed(1)}`,
                  `Value: ${(context.parsed.y / (context.parsed.x / 100)).toFixed(2)} points per $100`
                ]
              }
            }
          },
          scales: {
            x: {
              type: 'logarithmic',
              grid: {
                color: 'rgba(255, 255, 255, 0.1)',
                lineWidth: 1
              },
              ticks: {
                color: '#b8bcc8',
                font: { size: 11 },
                callback: (value) => `$${value.toLocaleString()}`
              },
              title: {
                display: true,
                text: 'Price (USD, log scale)',
                color: '#e8e9f0',
                font: { size: 12, weight: '600' }
              }
            },
            y: {
              grid: {
                color: 'rgba(255, 255, 255, 0.1)',
                lineWidth: 1
              },
              ticks: {
                color: '#b8bcc8',
                font: { size: 11 }
              },
              title: {
                display: true,
                text: 'Overall Score',
                color: '#e8e9f0',
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

export default PricePerformanceChart 