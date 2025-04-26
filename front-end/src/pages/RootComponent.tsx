import * as React from 'react'
import HomePage from './HomePage'
import NotFoundPage from './NotFoundPage'
import LoginPage from '../pages/LoginPage'
import UserPage from '../pages/UserPage'
import { ROUTES } from '../resources/routes-constants'
import '../styles/main.sass'
import { AppBar, Box, Container, CssBaseline, Divider, Drawer, IconButton, List, ListItem, ListItemButton, ListItemIcon, ListItemText, Toolbar, Typography, Button, Snackbar, Alert } from '@mui/material'
import { DirectionsSubwayFilled, MenuRounded } from '@mui/icons-material'
import { Route, Routes, useNavigate } from 'react-router-dom'
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import ExitToAppIcon from '@mui/icons-material/ExitToApp';
import MapIcon from '@mui/icons-material/Map';
import SubwayIcon from '@mui/icons-material/Subway';
import LoginIcon from '@mui/icons-material/Login';
import StatusPage from './StatusPage'
import path from 'path'
import { useTranslation } from 'react-i18next';
import { Select, MenuItem } from '@mui/material';

const drawerWidth = 240;

export default function RootComponent() {
    const [mobileOpen, setMobileOpen] = React.useState(false);
    const [isClosing, setIsClosing] = React.useState(false);
    const [showLoginPrompt, setShowLoginPrompt] = React.useState(false)
    const { t, i18n } = useTranslation();
    const drawerItems = [
        { text: t('transitMap'),   path: ROUTES.HOMEPAGE_ROUTE,     icon: <MapIcon /> },
        { text: t('serviceStatus'),path: ROUTES.SERVICE_STATUS,     icon: <SubwayIcon /> },
        { text: t('userCenter'),   path: ROUTES.USER_PAGE_ROUTE, is_protected: true, icon: <AccountCircleIcon /> },
      ];
    const navigate = useNavigate()
    
    

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
                {drawerItems.map(({text, path, is_protected, icon}) => (
                    <ListItem key={text} disablePadding>
                        <ListItemButton onClick={() => {
                            if (is_protected) {
                                const token = localStorage.getItem('token')
                                if (token) {
                                    navigate(path)
                                } else{
                                    setShowLoginPrompt(true)
                                }
                            } else {
                                navigate(path)
                            }
                        }}>
                            {icon && <ListItemIcon>{icon}</ListItemIcon>}
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
                    <Typography 
                        variant='h6'
                        noWrap
                        component={'div'}
                        sx={{ flexGrow:1, ml:1}}>
                        MetroDiver
                    </Typography>


                    <Select
                    size="small"
                    value={i18n.language}
                    onChange={(e) => i18n.changeLanguage(e.target.value).then(() => window.location.reload())}
                    sx={{
                    mr: 1,
                    color: 'white',
                    '.MuiOutlinedInput-notchedOutline': { border: 0 },
                    '& .MuiSvgIcon-root': { color: 'white' },
                    }}
                    >
                    <MenuItem value="zh">中文</MenuItem>
                    <MenuItem value="en">English</MenuItem>
                    <MenuItem value="es">Español</MenuItem>
                    </Select>


                    <Button
                    variant="outlined"
                    color="inherit"
                    startIcon={<LoginIcon />}
                    sx={{ ml: 1 }}
                    onClick={() => { window.location.href = ROUTES.LOGIN_ROUTE; }}
                    >
                    {t('login')}
                    </Button>

                    <Button
                    variant="outlined"
                    color="inherit"
                    startIcon={<ExitToAppIcon />}
                    sx={{ ml: 1 }}
                    onClick={() => {
                    localStorage.removeItem('token');
                    window.location.href = ROUTES.HOMEPAGE_ROUTE;
                    }}>
                        {t('logout')}
                    </Button>
                </Toolbar>
            </AppBar>

            <Snackbar
                open={showLoginPrompt}
                autoHideDuration={3000}
                onClose={() => setShowLoginPrompt(false)}
                anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
            >
                <Alert severity="warning" sx={{ width: '100%' }}>
                    {t('notLoggedIn')}
                </Alert>
            </Snackbar>

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
                <Routes>
                    <Route path="*" element={<NotFoundPage />} />
                    <Route path={ROUTES.HOMEPAGE_ROUTE} element={<HomePage />} />
                    <Route path={ROUTES.LOGIN_ROUTE} element={<LoginPage />} />
                    <Route path={ROUTES.USER_PAGE_ROUTE} element={<UserPage />} /> 
                    <Route path={ROUTES.SERVICE_STATUS} element={<StatusPage />} /> 
                </Routes>
            </Box>
        </ Box>

    )
}
