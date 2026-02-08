import React, { useState } from 'react';
import { Form, Input, Button, message } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons';
import { register } from '../services/api';
import './Login.css'; // Reusing Login styles for consistency

const Register = ({ onRegisterSuccess, onCancel }) => {
    const [loading, setLoading] = useState(false);

    const onFinish = async (values) => {
        setLoading(true);
        try {
            await register(values.username, values.email, values.password);
            message.success('Registration successful! Please login.');
            onRegisterSuccess();
        } catch (error) {
            console.error('Registration error:', error);

            let errorMsg = 'Registration failed. Please try again.';

            // Handle Django Rest Framework error format: { field: [error1, error2] }
            if (error.response && error.response.data) {
                const data = error.response.data;
                const firstKey = Object.keys(data)[0];
                if (firstKey && Array.isArray(data[firstKey])) {
                    errorMsg = data[firstKey][0];
                } else if (typeof data === 'object') {
                    // Fallback for other structures
                    errorMsg = Object.values(data)[0];
                }
            }

            message.error(errorMsg);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="login-container">
            <div className="login-card">
                <div className="login-header">
                    <h1 className="login-title">Register</h1>
                    <p className="login-subtitle">Create a new account</p>
                </div>

                <Form
                    name="register_form"
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
                        name="email"
                        rules={[
                            { required: true, message: 'Please input your Email!' },
                            { type: 'email', message: 'Please enter a valid email!' }
                        ]}
                    >
                        <Input
                            prefix={<MailOutlined />}
                            placeholder="Email"
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
                            Register
                        </Button>
                        <div style={{ marginTop: 16, textAlign: 'center' }}>
                            <a className="register-link" onClick={onCancel} style={{ cursor: 'pointer' }}>
                                Already have an account? Login
                            </a>
                        </div>
                    </Form.Item>
                </Form>
            </div>
        </div>
    );
};

export default Register;
