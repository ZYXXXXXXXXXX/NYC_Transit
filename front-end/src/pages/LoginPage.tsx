import React from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { ROUTES } from '../resources/routes-constants'

export default function LoginPage() {
    const navigate = useNavigate()
    const location = useLocation()
    const from = location.state?.from?.pathname || ROUTES.HOMEPAGE_ROUTE

    const handleLogin = () => {
        localStorage.setItem('token', 'fake-jwt-token')  // 实际开发中来自服务器
        navigate(from, { replace: true })  // 登录成功后返回原页面
    }

    return (
        <div>
            <h2>Login</h2>
            <button onClick={handleLogin}>Click to Login</button>
        </div>
    )
}