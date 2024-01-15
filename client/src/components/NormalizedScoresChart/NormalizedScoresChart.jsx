import React, { useRef, useEffect } from 'react';
import Chart from 'chart.js/auto';

const NormalizedScoresChart = ({ iems }) => {
  const chartRef = useRef(null);

  useEffect(() => {
    if (iems.length > 0) {
      const ctx = chartRef.current.getContext('2d');
      const normalizedScoresChart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: iems.map((iem) => iem.model),
          datasets: [
            {
              label: 'Normalized Score',
              data: iems.map((iem) => iem.normalizedFloat),
              backgroundColor: 'rgba(60, 66, 81, 1)',
              borderColor: 'rgba(217, 222, 232, 1)',
              hoverBorderColor: 'rgba(148, 190, 206, 1)',
              borderWidth: 2,
            },
          ],
        },
        options: {
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                color: 'rgba(217, 222, 232, 1)',
              },
              grid: {
                color: 'rgba(60, 66, 81, 1)',
              },
            },
            x: {
              ticks: {
                color: 'rgba(217, 222, 232, 1)',
              },
              grid: {
                color: 'rgba(60, 66, 81, 1)',
              },
            },
          },
          plugins: {
            legend: {
              labels: {
                color: 'rgba(217, 222, 232, 1)',
              },
            },
          },
        },
      });

      // Cleanup on unmount
      return () => normalizedScoresChart.destroy();
    }
  }, [iems]); // Dependency array to re-run the effect when iems updates

  return <canvas ref={chartRef} />;
};

export default NormalizedScoresChart;
