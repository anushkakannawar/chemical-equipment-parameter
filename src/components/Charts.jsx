import React from 'react';
import { Card, Row, Col } from 'antd';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
    ArcElement,
    PointElement,
    LineElement,
} from 'chart.js';
import { Bar, Pie } from 'react-chartjs-2';

// Register ChartJS components
ChartJS.register(
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
    ArcElement,
    PointElement,
    LineElement
);

const Charts = ({ summary }) => {
    if (!summary) return null;

    const { type_distribution, avg_flowrate, avg_pressure, avg_temperature } = summary;

    // 1. Equipment Type Distribution Chart (Pie Chart covers "Distribution" well)
    const typeLabels = Object.keys(type_distribution || {});
    const typeValues = Object.values(type_distribution || {});

    // Lyna Palette for Pie Chart (Green/Lime theme)
    const lynaPalette = [
        '#076653', // Deep Green
        '#E3EF26', // Lime
        '#0C342C', // Forest Green
        '#E2FBCE', // Pale Green (Light Accent)
        '#2E8B57', // Sea Green (Bridge)
        '#9ACD32', // Yellow Green (Bridge)
    ];

    const distributionData = {
        labels: typeLabels,
        datasets: [
            {
                label: 'Count',
                data: typeValues,
                backgroundColor: lynaPalette.slice(0, typeValues.length),
                borderWidth: 1,
                borderColor: '#FFFDEE', // Cream border
            },
        ],
    };

    // 2. Equipment Parameter Averages (Bar Chart)
    const averagesData = {
        labels: ['Flowrate', 'Pressure', 'Temperature'],
        datasets: [
            {
                label: 'Average Value',
                data: [avg_flowrate, avg_pressure, avg_temperature],
                backgroundColor: '#076653', // Deep Green
                borderColor: '#0C342C',
                borderWidth: 1,
                borderRadius: 4, // Rounded bars
                hoverBackgroundColor: '#E3EF26', // Lime on hover
            },
        ],
    };

    const options = {
        responsive: true,
        plugins: {
            legend: {
                position: 'top',
                labels: {
                    font: {
                        family: "'Inter', sans-serif",
                    },
                    color: '#64748B' // Slate 500
                }
            },
            title: {
                display: false,
            }
        },
        scales: {
            y: {
                grid: {
                    color: '#F1F5F9' // Very light slate grid
                },
                ticks: {
                    color: '#64748B',
                    font: {
                        family: "'Inter', sans-serif",
                    }
                }
            },
            x: {
                grid: {
                    display: false
                },
                ticks: {
                    color: '#64748B',
                    font: {
                        family: "'Inter', sans-serif",
                    }
                }
            }
        }
    };

    const pieOptions = {
        responsive: true,
        plugins: {
            legend: {
                position: 'right',
                labels: {
                    font: {
                        family: "'Inter', sans-serif",
                    },
                    color: '#64748B',
                    generateLabels: (chart) => {
                        const data = chart.data;
                        if (data.labels.length && data.datasets.length) {
                            return data.labels.map((label, i) => {
                                const meta = chart.getDatasetMeta(0);
                                const style = meta.controller.getStyle(i);
                                const value = data.datasets[0].data[i];
                                const total = data.datasets[0].data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1) + '%';

                                return {
                                    text: `${label} - ${percentage}`,
                                    fillStyle: style.backgroundColor,
                                    strokeStyle: style.borderColor,
                                    lineWidth: style.borderWidth,
                                    hidden: isNaN(data.datasets[0].data[i]) || meta.data[i].hidden,
                                    index: i
                                };
                            });
                        }
                        return [];
                    }
                }
            }
        }
    };

    return (
        <div style={{ marginBottom: 20 }}>
            <Row gutter={[24, 24]}>
                <Col xs={24} md={12}>
                    <Card title="Equipment Type Distribution" bordered={false}>
                        <Pie data={distributionData} options={pieOptions} />
                    </Card>
                </Col>
                <Col xs={24} md={12}>
                    <Card title="Parameter Averages" bordered={false}>
                        <Bar data={averagesData} options={options} />
                    </Card>
                </Col>
            </Row>
        </div>
    );
};

export default Charts;
