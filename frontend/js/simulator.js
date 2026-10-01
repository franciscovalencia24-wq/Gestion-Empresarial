export function initSimulator() {
  const chartDom = document.getElementById('simulator-echart');
  if (!chartDom) return;
  
  const myChart = echarts.init(chartDom, 'dark');
  
  const simInitial = document.getElementById('sim-initial');
  const simMonthly = document.getElementById('sim-monthly');
  const simYears = document.getElementById('sim-years');
  const simRisk = document.getElementById('sim-risk');
  const simReturn = document.getElementById('sim-return');
  const simInflation = document.getElementById('sim-inflation');
  
  const valInitial = document.getElementById('val-initial');
  const valMonthly = document.getElementById('val-monthly');
  const valYears = document.getElementById('val-years');
  
  // Default expected returns based on the risk profiles
  const profiles = {
    muy_conservador: 3.5,
    conservador: 4.5,
    cauteloso: 6.0,
    moderado: 7.5,
    decidido: 9.0,
    agresivo: 11.0
  };
  
  // When risk profile changes, update the return input
  simRisk.addEventListener('change', () => {
    if (profiles[simRisk.value]) {
      simReturn.value = profiles[simRisk.value];
    }
    updateChart();
  });
  
  function updateChart() {
    const P = parseFloat(simInitial.value);
    const PMT = parseFloat(simMonthly.value);
    const years = parseInt(simYears.value);
    const rateNominal = parseFloat(simReturn.value) / 100;
    const rateInflation = parseFloat(simInflation.value) / 100;
    
    // Update labels formatting in CLP
    valInitial.innerText = P.toLocaleString('es-CL');
    valMonthly.innerText = PMT.toLocaleString('es-CL');
    valYears.innerText = years;
    
    // Approximate real return rate adjusted for inflation
    const rateReal = (1 + rateNominal) / (1 + rateInflation) - 1;
    
    const yearsArray = [];
    const dataNominal = [];
    const dataReal = [];
    
    let currentNominal = P;
    let currentReal = P;
    
    for (let i = 0; i <= years; i++) {
      yearsArray.push(`Año ${i}`);
      dataNominal.push(Math.round(currentNominal));
      dataReal.push(Math.round(currentReal));
      
      // Calculate next year
      currentNominal = currentNominal * (1 + rateNominal) + (PMT * 12);
      currentReal = currentReal * (1 + rateReal) + (PMT * 12);
    }
    
    const option = {
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'axis',
        confine: true,
        formatter: function(params) {
          let html = `<strong>${params[0].name}</strong><br/>`;
          params.forEach(p => {
            html += `<span style="color:${p.color}">●</span> ${p.seriesName}: $${p.value.toLocaleString('es-CL')}<br/>`;
          });
          const diff = params[0].value - params[1].value;
          if (diff > 0) {
            html += `<hr style="border-color: rgba(255,255,255,0.1); margin: 4px 0;"/><span style="color: #ef4444; font-size: 12px;">-$${diff.toLocaleString('es-CL')} (Efecto Inflación)</span>`;
          }
          return html;
        }
      },
      legend: {
        data: ['Capital Nominal Proyectado', 'Poder Adquisitivo (Ajustado por Inflación)'],
        textStyle: { color: '#94a3b8' },
        top: 0
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        top: '15%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: yearsArray,
        axisLine: { lineStyle: { color: '#475569' } },
        axisLabel: { color: '#94a3b8' }
      },
      yAxis: {
        type: 'value',
        splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } },
        axisLabel: {
          color: '#94a3b8',
          formatter: function(value) {
            if (value >= 1000000) {
              return '$' + (value / 1000000).toFixed(0) + 'M';
            }
            if (value >= 1000) {
              return '$' + (value / 1000).toFixed(0) + 'k';
            }
            return '$' + value;
          }
        }
      },
      series: [
        {
          name: 'Capital Nominal Proyectado',
          type: 'line',
          data: dataNominal,
          itemStyle: { color: '#C5A059' },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(197, 160, 89, 0.5)' },
              { offset: 1, color: 'rgba(197, 160, 89, 0.0)' }
            ])
          },
          symbol: 'circle',
          symbolSize: 8
        },
        {
          name: 'Poder Adquisitivo (Ajustado por Inflación)',
          type: 'line',
          data: dataReal,
          itemStyle: { color: '#64748b' },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(100, 116, 139, 0.3)' },
              { offset: 1, color: 'rgba(100, 116, 139, 0.0)' }
            ])
          },
          symbol: 'circle',
          symbolSize: 6
        }
      ]
    };
    
    myChart.setOption(option);
  }
  
  // Event listeners
  simInitial.addEventListener('input', updateChart);
  simMonthly.addEventListener('input', updateChart);
  simYears.addEventListener('input', updateChart);
  simReturn.addEventListener('input', updateChart);
  simInflation.addEventListener('input', updateChart);
  
  // Initial render
  updateChart();
  
  window.addEventListener('resize', () => {
    myChart.resize();
  });
}
