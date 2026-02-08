import React, { useState } from 'react';
import { Form, Input, Button, message } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { login } from '../services/api';
import './Login.css';

const MoleculeIcon = () => (
    <div className="molecule-icon-container">
        <svg className="molecule-svg" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L12 12M12 12L4 16M12 12L20 16M4 16L4 22M20 16L20 22M4 16L2 12M20 16L22 12" strokeLinecap="round" strokeLinejoin="round" />
            <circle cx="12" cy="12" r="3" fill="#10B981" fillOpacity="0.2" stroke="none" />
            <circle cx="12" cy="2" r="1.5" fill="#10B981" />
            <circle cx="4" cy="16" r="1.5" fill="#10B981" />
            <circle cx="20" cy="16" r="1.5" fill="#10B981" />
        </svg>
    </div>
);

const Login = ({ onLogin, onRegisterClick }) => {
    const [loading, setLoading] = useState(false);

    const onFinish = async (values) => {
        setLoading(true);
        try {
            await login(values.username, values.password);
            message.success('Login successful!');
            onLogin();
        } catch (error) {
            console.error('Login error:', error);
            message.error('Invalid username or password');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="login-container">
            <div className="login-card">
                <div className="login-header">
                    <MoleculeIcon />
                    <h1 className="login-title">Sign In</h1>
                    <p className="login-subtitle">Chemical Visualizer</p>
                </div>

                <Form
                    name="login_form"
                    onFinish={onFinish}
                    className="login-form"
                    layout="vertical"
                    size="large"
                >
                    <Form.Item
                        name="username"
                        rules={[{ required: true, message: 'Please input your Username!' }]}
                    >
                        <Input
                            prefix={<UserOutlined />}
                            placeholder="Username"
                            className="custom-input"
                        />
                    </Form.Item>
                    <Form.Item
                        name="password"
                        rules={[{ required: true, message: 'Please input your Password!' }]}
                    >
                        <Input.Password
                            prefix={<LockOutlined />}
                            placeholder="Password"
                            className="custom-input"
                        />
                    </Form.Item>

                    <Form.Item>
                        <Button
                            type="primary"
                            htmlType="submit"
                            className="login-button"
                            block
                            loading={loading}
                        >
                            Log in
                        </Button>
                        <div style={{ marginTop: 16, textAlign: 'center' }}>
                            <a className="register-link" onClick={onRegisterClick} style={{ cursor: 'pointer' }}>
                                Don't have an account? Register
                            </a>
                        </div>
                    </Form.Item>
                </Form>
            </div>
        </div>
    );
};

export default Login;
