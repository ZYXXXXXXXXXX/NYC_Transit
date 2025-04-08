import React from 'react'
import { BrowserRouter as Router, Route, Routes } from 'react-router'
import HomePage from './pages/HomePage'
import NotFoundPage from './pages/NotFoundPage'
import { ROUTES } from './resources/routes-constants'
import './styles/main.sass'
import { AppBar, CssBaseline, Toolbar, Typography } from '@mui/material'
import { DirectionsSubwayFilled } from '@mui/icons-material'

const RootComponent: React.FC = () => {
    return (

        <>

            <CssBaseline />
            <AppBar position='relative'>
                <Toolbar>
                    <DirectionsSubwayFilled />
                    <Typography variant='h6'>
                        MetroDiver
                    </Typography>
                </Toolbar>
            </AppBar>

            <Router>
                <Routes>
                    <Route path="*" element={<NotFoundPage />} />
                    <Route path={ROUTES.HOMEPAGE_ROUTE} element={<HomePage />} />
                </Routes>
            </Router>
        </>

    )
}

export default RootComponent
