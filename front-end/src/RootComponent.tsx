import * as React from 'react'
import { BrowserRouter as Router, Route, Routes } from 'react-router'
import HomePage from './pages/HomePage'
import NotFoundPage from './pages/NotFoundPage'
import { ROUTES } from './resources/routes-constants'
import './styles/main.sass'
import { AppBar, Box, Container, CssBaseline, Divider, Drawer, IconButton, List, ListItem, ListItemButton, ListItemIcon, ListItemText, Toolbar, Typography } from '@mui/material'
import { DirectionsSubwayFilled, MenuRounded } from '@mui/icons-material'

const drawerWidth = 240;

export default function RootComponent() {
    const [mobileOpen, setMobileOpen] = React.useState(false);
    const [isClosing, setIsClosing] = React.useState(false);

    const handleDrawerClose = () => {
        setIsClosing(true);
        setMobileOpen(false);
    }

    const handleDrawerTransitionEnd = () => {
        setIsClosing(false);
    }

    const handleDrawerToggle = () => {
        if (!isClosing) {
            setMobileOpen(!mobileOpen)
        }
    }

    const drawer = (
        <div>
            <Toolbar />
            <Divider />
            <List>
                {['Transit Map', 'Service Status', 'Accessibility'].map((text, index) => (
                    <ListItem key={text} disablePadding>
                        <ListItemButton>
                            <ListItemText primary={text} />
                        </ListItemButton>
                    </ListItem>
                ))}
            </List>
        </div>
    );

    return (

        <Box sx={{ display: 'flex'}}>
            <CssBaseline />
            <AppBar
                position='fixed'
                sx={{
                    width: { sm: `calc(100% - ${drawerWidth}px)` },
                    ml: { sm: `${drawerWidth}px` },
                }}
            >
                <Toolbar>
                    <IconButton
                        color='inherit'
                        aria-label='open drawer'
                        edge='start'
                        onClick={handleDrawerToggle}
                        sx={{
                            mr: 2,
                            display: { sm: 'none' }
                        }}>
                        <MenuRounded />
                    </IconButton>
                    <DirectionsSubwayFilled />
                    <Typography variant='h6' noWrap component={'div'}>
                        MetroDiver
                    </Typography>
                </Toolbar>
            </AppBar>

            <Box
                component={'nav'}
                sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
            >
                <Drawer
                    variant='temporary'
                    open={mobileOpen}
                    onTransitionEnd={handleDrawerTransitionEnd}
                    onClose={handleDrawerClose}
                    sx={{
                        display: { xs: 'block', sm: 'none' },
                        '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
                    }}
                    slotProps={{
                        root: {
                            keepMounted: true,
                        },
                    }}
                >
                    {drawer}
                </Drawer>
                <Drawer
                    variant="permanent"
                    sx={{
                        display: { xs: 'none', sm: 'block' },
                        '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
                    }}
                    open
                >
                    {drawer}
                </Drawer>
            </Box>
            <Box
                component="main"
                sx={{ flexGrow: 1, p: 3, width: { sm: `calc(100% - ${drawerWidth}px)`, overflow: 'auto'} }}
            >
                <Router>
                    <Routes>
                        <Route path="*" element={<NotFoundPage />} />
                        <Route path={ROUTES.HOMEPAGE_ROUTE} element={<HomePage />} />
                    </Routes>
                </Router>
            </Box>
        </ Box>

    )
}
