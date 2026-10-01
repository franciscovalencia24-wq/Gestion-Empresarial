export async function initVolatilityChart() {
  const chartDom = document.getElementById('volatility-chart');
  if (!chartDom) return;

  const myChart = echarts.init(chartDom, 'dark');
  
  try {
    const response = await fetch('/data/sp500_history.json');
    const data = await response.json();
    
    // Convert UNIX timestamps to formatted dates
    const dates = [];
    const prices = [];
    
    data.forEach(item => {
      const dateObj = new Date(item.date * 1000);
      const year = dateObj.getFullYear();
      const month = String(dateObj.getMonth() + 1).padStart(2, '0');
      dates.push(`${year}-${month}`);
      prices.push(item.price.toFixed(2));
    });

    // Historical Events (Crisis & Bull Runs)
    const historicalEvents = [
      {
        name: 'Guerra del Golfo\nRecesión',
        coord: ['1990-10', 304],
        value: '-20%',
        symbolSize: 45,
        itemStyle: { color: '#ef4444' },
        label: { show: true, position: 'bottom', formatter: '{b}\n{c}', color: '#ef4444', fontWeight: 'bold', fontSize: 12, backgroundColor: 'rgba(10,17,31,0.7)', padding: 4, borderRadius: 4 }
      },
      {
        name: 'Boom de los 90s',
        coord: ['1999-12', 1469],
        value: '+380%',
        symbolSize: 40,
        itemStyle: { color: '#10b981' },
        label: { show: true, position: 'top', formatter: '{b}\n{c}', color: '#10b981', fontWeight: 'bold', fontSize: 12, backgroundColor: 'rgba(10,17,31,0.7)', padding: 4, borderRadius: 4 }
      },
      {
        name: 'Torres Gemelas',
        coord: ['2002-09', 815],
        value: '-49%',
        symbolSize: 45,
        itemStyle: { color: '#ef4444' },
        label: { show: true, position: 'bottom', formatter: '{b}\n{c}', color: '#ef4444', fontWeight: 'bold', fontSize: 12, backgroundColor: 'rgba(10,17,31,0.7)', padding: 4, borderRadius: 4 }
      },
      {
        name: 'Recuperación',
        coord: ['2007-07', 1553],
        value: '+100%',
        symbolSize: 40,
        itemStyle: { color: '#10b981' },
        label: { show: true, position: 'top', formatter: '{b}\n{c}', color: '#10b981', fontWeight: 'bold', fontSize: 12, backgroundColor: 'rgba(10,17,31,0.7)', padding: 4, borderRadius: 4 }
      },
      {
        name: 'Crisis Subprime',
        coord: ['2009-02', 735],
        value: '-56%',
        symbolSize: 55,
        itemStyle: { color: '#ef4444' },
        label: { show: true, position: 'bottom', formatter: '{b}\n{c}', color: '#ef4444', fontWeight: 'bold', fontSize: 12, backgroundColor: 'rgba(10,17,31,0.7)', padding: 4, borderRadius: 4 }
      },
      {
        name: 'Bull Market',
        coord: ['2019-12', 3230],
        value: '+400%',
        symbolSize: 45,
        itemStyle: { color: '#10b981' },
        label: { show: true, position: 'top', formatter: '{b}\n{c}', color: '#10b981', fontWeight: 'bold', fontSize: 12, backgroundColor: 'rgba(10,17,31,0.7)', padding: 4, borderRadius: 4 }
      },
      {
        name: 'COVID-19',
        coord: ['2020-03', 2584],
        value: '-34%',
        symbolSize: 50,
        itemStyle: { color: '#ef4444' },
        label: { show: true, position: 'bottom', formatter: '{b}\n{c}', color: '#ef4444', fontWeight: 'bold', fontSize: 12, backgroundColor: 'rgba(10,17,31,0.7)', padding: 4, borderRadius: 4 }
      },
      {
        name: 'Estímulos',
        coord: ['2021-12', 4766],
        value: '+114%',
        symbolSize: 40,
        itemStyle: { color: '#10b981' },
        label: { show: true, position: 'top', formatter: '{b}\n{c}', color: '#10b981', fontWeight: 'bold', fontSize: 12, backgroundColor: 'rgba(10,17,31,0.7)', padding: 4, borderRadius: 4 }
      },
      {
        name: 'Guerra/Inflación',
        coord: ['2022-10', 3871],
        value: '-25%',
        symbolSize: 45,
        itemStyle: { color: '#ef4444' },
        label: { show: true, position: 'bottom', formatter: '{b}\n{c}', color: '#ef4444', fontWeight: 'bold', fontSize: 12, backgroundColor: 'rgba(10,17,31,0.7)', padding: 4, borderRadius: 4 }
      },
      {
        name: 'Boom de IA',
        coord: ['2024-06', 5460],
        value: '+60%',
        symbolSize: 45,
        itemStyle: { color: '#10b981' },
        label: { show: true, position: 'top', formatter: '{b}\n{c}', color: '#10b981', fontWeight: 'bold', fontSize: 12, backgroundColor: 'rgba(10,17,31,0.7)', padding: 4, borderRadius: 4 }
      }
    ];

    const option = {
      backgroundColor: 'transparent',
      title: {
        text: 'Evolución Histórica S&P 500 y Eventos de Mercado',
        left: 'center',
        textStyle: {
          color: '#f8fafc',
          fontSize: 16,
          fontFamily: 'Inter'
        }
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'cross' },
        backgroundColor: 'rgba(10, 17, 31, 0.9)',
        borderColor: '#334155',
        textStyle: { color: '#f8fafc' }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '8%',
        top: '12%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: dates,
        axisLine: { lineStyle: { color: '#475569' } },
        axisLabel: { color: '#94a3b8' }
      },
      yAxis: {
        type: 'value',
        scale: true,
        splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } },
        axisLabel: {
          color: '#94a3b8',
          formatter: '${value}'
        }
      },
      dataZoom: [
        {
          type: 'inside',
          start: 0,
          end: 100
        },
        {
          start: 0,
          end: 100,
          borderColor: 'transparent',
          fillerColor: 'rgba(197, 160, 89, 0.2)',
          textStyle: { color: '#94a3b8' }
        }
      ],
      series: [
        {
          name: 'S&P 500',
          type: 'line',
          data: prices,
          itemStyle: { color: '#C5A059' },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(197, 160, 89, 0.4)' },
              { offset: 1, color: 'rgba(197, 160, 89, 0.0)' }
            ])
          },
          markPoint: {
            symbol: 'pin',
            label: {
              show: true,
              color: '#fff',
              fontSize: 12,
              formatter: '{c}'
            },
            data: historicalEvents,
            tooltip: {
              formatter: function (params) {
                const isPositive = params.value.includes('+');
                const valColor = isPositive ? '#10b981' : '#ef4444';
                const valLabel = isPositive ? 'Alza aprox:' : 'Caída aprox:';
                return '<div style="padding:4px; max-width:200px; white-space:normal;">' +
                       '<strong style="color:#C5A059; font-size:14px;">' + params.name.replace('\n', '<br/>') + '</strong><br/>' +
                       '<span style="color:' + valColor + '; font-weight:bold;">' + valLabel + ' ' + params.value + '</span><br/>' +
                       '<span style="color:#94a3b8; font-size:12px;">Fecha: ' + params.data.coord[0] + '</span>' +
                       '</div>';
              }
            }
          }
        }
      ]
    };

    myChart.setOption(option);
    
    window.addEventListener('resize', () => {
      myChart.resize();
    });

  } catch (err) {
    console.error('Error loading chart data:', err);
  }
}
