import React, { useEffect, useState } from 'react';
import { Layout, Row, Col, Typography, message, Spin, Button } from 'antd';
import { FilePdfOutlined, LogoutOutlined } from '@ant-design/icons';
import UploadCSV from '../components/UploadCSV';
import EquipmentTable from '../components/EquipmentTable';
import Charts from '../components/Charts';
import History from '../components/History';
import { getSummary, getHistory, downloadReport } from '../services/api';
import './Dashboard.css';

const { Header, Content, Footer } = Layout;
const { Title } = Typography;

const Dashboard = ({ onLogout }) => {
    const [summary, setSummary] = useState(null);
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchData = async () => {
        setLoading(true);
        try {
            const [summaryData, historyData] = await Promise.all([
                getSummary().catch(() => null),
                getHistory()
            ]);

            if (summaryData) {
                setSummary(summaryData);
            }
            setHistory(historyData);
        } catch (error) {
            console.error(error);
            message.error('Failed to load initial data');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const handleUploadSuccess = () => {
        fetchData();
    };

    const handleHistoryClick = (item) => {
        setSummary(item);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const handleDownloadReport = async () => {
        if (!summary || !summary.id) {
            message.warning("No dataset loaded to generate report for.");
            return;
        }
        try {
            const blob = await downloadReport(summary.id);
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `report_${summary.filename.replace('.csv', '')}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.remove();
            message.success("Report downloaded successfully!");
        } catch (error) {
            console.error("Download failed", error);
            message.error("Failed to download report.");
        }
    };

    return (
        <Layout className="clean-layout">
            <Header className="clean-header">
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    {/* Optional: Add small molecule icon here if desired */}
                    <Title level={4} className="header-title">
                        Chemical Equipment Visualizer
                    </Title>
                </div>
                <div style={{ marginLeft: 'auto', display: 'flex', gap: '16px' }}>
                    {summary && (
                        <Button
                            type="primary"
                            icon={<FilePdfOutlined />}
                            onClick={handleDownloadReport}
                            style={{ borderRadius: '8px' }}
                        >
                            Download Report
                        </Button>
                    )}
                    <Button
                        type="text"
                        icon={<LogoutOutlined />}
                        onClick={onLogout}
                        style={{ color: '#64748B' }}
                    >
                        Logout
                    </Button>
                </div>
            </Header>
            <Content style={{ padding: '0 50px', marginTop: 32 }}>
                <div className="site-layout-content">
                    <Row gutter={[24, 24]}>
                        {/* Left Column: Upload & History */}
                        <Col xs={24} lg={6}>
                            <UploadCSV onUploadSuccess={handleUploadSuccess} />
                            <History history={history} onItemClick={handleHistoryClick} />
                        </Col>

                        {/* Right Column: Charts & Table */}
                        <Col xs={24} lg={18}>
                            {loading ? (
                                <div style={{ textAlign: 'center', padding: 50 }}>
                                    <Spin size="large" />
                                </div>
                            ) : summary ? (
                                <>
                                    <Charts summary={summary} />
                                    <EquipmentTable data={summary.data} loading={loading} />
                                </>
                            ) : (
                                <div style={{ textAlign: 'center', padding: 50 }}>
                                    <Typography.Text type="secondary">
                                        No data available. Upload a CSV file to get started.
                                    </Typography.Text>
                                </div>
                            )}
                        </Col>
                    </Row>
                </div>
            </Content>
            <Footer style={{ textAlign: 'center' }}>
                Chemical Equipment Visualizer ©{new Date().getFullYear()}
            </Footer>
        </Layout>
    );
};

export default Dashboard;
