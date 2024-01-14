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
              label: 'Normalized Scores',
              data: iems.map((iem) => iem.normalizedFloat),
              backgroundColor: 'rgba(47, 52, 63, 1)',
              borderColor: 'rgba(60, 66, 81, 1)',
              borderWidth: 1,
            },
          ],
        },
        options: {
          scales: {
            y: {
              beginAtZero: true,
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
