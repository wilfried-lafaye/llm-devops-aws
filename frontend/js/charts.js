/**
 * Charts Module for Air Quality Dashboard
 * Manages all Chart.js visualizations
 */

// Chart instances storage
const chartInstances = {};

// Color palette
const COLORS = {
    no2: { main: '#ef4444', light: 'rgba(239, 68, 68, 0.2)' },
    pm10: { main: '#f59e0b', light: 'rgba(245, 158, 11, 0.2)' },
    pm25: { main: '#8b5cf6', light: 'rgba(139, 92, 246, 0.2)' },
    o3: { main: '#22c55e', light: 'rgba(34, 197, 94, 0.2)' },
    regions: [
        '#3b82f6', '#ef4444', '#22c55e', '#f59e0b', '#8b5cf6',
        '#ec4899', '#14b8a6', '#f97316', '#6366f1', '#84cc16'
    ]
};

// Common chart options
const commonOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            labels: {
                color: '#94a3b8',
                font: { size: 12 }
            }
        },
        tooltip: {
            backgroundColor: '#1e293b',
            titleColor: '#f8fafc',
            bodyColor: '#94a3b8',
            borderColor: '#475569',
            borderWidth: 1,
            cornerRadius: 8,
            padding: 12
        }
    },
    scales: {
        x: {
            grid: { color: 'rgba(71, 85, 105, 0.3)' },
            ticks: { color: '#94a3b8' }
        },
        y: {
            grid: { color: 'rgba(71, 85, 105, 0.3)' },
            ticks: { color: '#94a3b8' }
        }
    }
};

/**
 * Destroy existing chart instance
 */
function destroyChart(chartId) {
    if (chartInstances[chartId]) {
        chartInstances[chartId].destroy();
        delete chartInstances[chartId];
    }
}

/**
 * Create Evolution Chart (Line chart showing pollutant trends)
 */
function createEvolutionChart(canvasId, data) {
    destroyChart(canvasId);
    
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    
    // Group data by year
    const yearData = {};
    data.forEach(record => {
        if (!yearData[record.annee]) {
            yearData[record.annee] = { no2: [], pm10: [], pm25: [], o3: [] };
        }
        if (record.no2) yearData[record.annee].no2.push(record.no2);
        if (record.pm10) yearData[record.annee].pm10.push(record.pm10);
        if (record.pm25) yearData[record.annee].pm25.push(record.pm25);
        if (record.o3) yearData[record.annee].o3.push(record.o3);
    });
    
    const years = Object.keys(yearData).sort();
    const calcAvg = arr => arr.length ? (arr.reduce((a, b) => a + b, 0) / arr.length).toFixed(1) : null;
    
    chartInstances[canvasId] = new Chart(ctx, {
        type: 'line',
        data: {
            labels: years,
            datasets: [
                {
                    label: 'NO₂',
                    data: years.map(y => calcAvg(yearData[y].no2)),
                    borderColor: COLORS.no2.main,
                    backgroundColor: COLORS.no2.light,
                    tension: 0.3,
                    fill: false
                },
                {
                    label: 'PM10',
                    data: years.map(y => calcAvg(yearData[y].pm10)),
                    borderColor: COLORS.pm10.main,
                    backgroundColor: COLORS.pm10.light,
                    tension: 0.3,
                    fill: false
                },
                {
                    label: 'PM2.5',
                    data: years.map(y => calcAvg(yearData[y].pm25)),
                    borderColor: COLORS.pm25.main,
                    backgroundColor: COLORS.pm25.light,
                    tension: 0.3,
                    fill: false
                },
                {
                    label: 'O₃',
                    data: years.map(y => calcAvg(yearData[y].o3)),
                    borderColor: COLORS.o3.main,
                    backgroundColor: COLORS.o3.light,
                    tension: 0.3,
                    fill: false
                }
            ]
        },
        options: {
            ...commonOptions,
            plugins: {
                ...commonOptions.plugins,
                title: {
                    display: false
                }
            },
            scales: {
                ...commonOptions.scales,
                y: {
                    ...commonOptions.scales.y,
                    title: {
                        display: true,
                        text: 'Concentration (µg/m³)',
                        color: '#94a3b8'
                    }
                }
            }
        }
    });
    
    return chartInstances[canvasId];
}

/**
 * Create Regions Comparison Chart (Bar chart)
 */
function createRegionsChart(canvasId, data) {
    destroyChart(canvasId);
    
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    
    // Group data by region
    const regionData = {};
    data.forEach(record => {
        if (!regionData[record.region]) {
            regionData[record.region] = { no2: [], pm10: [] };
        }
        if (record.no2) regionData[record.region].no2.push(record.no2);
        if (record.pm10) regionData[record.region].pm10.push(record.pm10);
    });
    
    const regions = Object.keys(regionData).slice(0, 8); // Limit to 8 regions
    const calcAvg = arr => arr.length ? (arr.reduce((a, b) => a + b, 0) / arr.length).toFixed(1) : 0;
    
    chartInstances[canvasId] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: regions.map(r => r.length > 15 ? r.substring(0, 15) + '...' : r),
            datasets: [
                {
                    label: 'NO₂',
                    data: regions.map(r => calcAvg(regionData[r].no2)),
                    backgroundColor: COLORS.no2.main,
                    borderRadius: 4
                },
                {
                    label: 'PM10',
                    data: regions.map(r => calcAvg(regionData[r].pm10)),
                    backgroundColor: COLORS.pm10.main,
                    borderRadius: 4
                }
            ]
        },
        options: {
            ...commonOptions,
            plugins: {
                ...commonOptions.plugins,
                legend: {
                    position: 'top',
                    labels: { color: '#94a3b8' }
                }
            },
            scales: {
                ...commonOptions.scales,
                y: {
                    ...commonOptions.scales.y,
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Concentration moyenne (µg/m³)',
                        color: '#94a3b8'
                    }
                }
            }
        }
    });
    
    return chartInstances[canvasId];
}

/**
 * Create Trend Chart (Single pollutant trend)
 */
function createTrendChart(canvasId, trendData, pollutant) {
    destroyChart(canvasId);
    
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    
    const pollutantColors = COLORS[pollutant] || COLORS.no2;
    
    chartInstances[canvasId] = new Chart(ctx, {
        type: 'line',
        data: {
            labels: trendData.map(d => d.annee),
            datasets: [{
                label: pollutant.toUpperCase(),
                data: trendData.map(d => d.value),
                borderColor: pollutantColors.main,
                backgroundColor: pollutantColors.light,
                tension: 0.4,
                fill: true,
                pointBackgroundColor: pollutantColors.main,
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 5,
                pointHoverRadius: 7
            }]
        },
        options: {
            ...commonOptions,
            plugins: {
                ...commonOptions.plugins,
                legend: {
                    display: false
                }
            },
            scales: {
                ...commonOptions.scales,
                y: {
                    ...commonOptions.scales.y,
                    beginAtZero: false,
                    title: {
                        display: true,
                        text: 'Concentration moyenne (µg/m³)',
                        color: '#94a3b8'
                    }
                },
                x: {
                    ...commonOptions.scales.x,
                    title: {
                        display: true,
                        text: 'Année',
                        color: '#94a3b8'
                    }
                }
            }
        }
    });
    
    return chartInstances[canvasId];
}

/**
 * Analyze trend and return insights
 */
function analyzeTrend(trendData, pollutant) {
    if (!trendData || trendData.length < 2) {
        return "Données insuffisantes pour l'analyse.";
    }
    
    const values = trendData.filter(d => d.value != null).map(d => d.value);
    if (values.length < 2) {
        return "Données insuffisantes pour l'analyse.";
    }
    
    const firstValue = values[0];
    const lastValue = values[values.length - 1];
    const change = ((lastValue - firstValue) / firstValue * 100).toFixed(1);
    const avg = (values.reduce((a, b) => a + b, 0) / values.length).toFixed(1);
    const max = Math.max(...values).toFixed(1);
    const min = Math.min(...values).toFixed(1);
    
    const pollutantName = {
        no2: 'Dioxyde d\'azote (NO₂)',
        pm10: 'Particules PM10',
        pm25: 'Particules fines PM2.5',
        o3: 'Ozone (O₃)'
    }[pollutant] || pollutant;
    
    let trend = '';
    if (change < -10) {
        trend = `📉 Tendance à la baisse significative (${change}%)`;
    } else if (change < 0) {
        trend = `📉 Légère tendance à la baisse (${change}%)`;
    } else if (change > 10) {
        trend = `📈 Tendance à la hausse préoccupante (+${change}%)`;
    } else if (change > 0) {
        trend = `📈 Légère tendance à la hausse (+${change}%)`;
    } else {
        trend = '➡️ Concentration stable';
    }
    
    return `
**${pollutantName}**

${trend}

• Moyenne sur la période : ${avg} µg/m³
• Valeur maximale : ${max} µg/m³  
• Valeur minimale : ${min} µg/m³
• Évolution : de ${firstValue.toFixed(1)} à ${lastValue.toFixed(1)} µg/m³
    `.trim();
}

// Export functions
window.AirQualityCharts = {
    createEvolutionChart,
    createRegionsChart,
    createTrendChart,
    analyzeTrend,
    destroyChart,
    COLORS
};
