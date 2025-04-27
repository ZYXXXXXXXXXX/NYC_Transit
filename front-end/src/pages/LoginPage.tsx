import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { auth } from '../resources/Firebase'; // Initiate firebase
import { ROUTES } from '../resources/routes-constants';
import { TextField, Button, Typography, Box, Alert, Tabs, Tab, CircularProgress } from '@mui/material';
import { createUserWithEmailAndPassword, signInWithEmailAndPassword } from 'firebase/auth';
import { sendEmailVerification } from 'firebase/auth';

function parseFirebaseError(error: unknown): string {
  if (typeof error === 'object' && error !== null && 'code' in error) {
    const code = (error as { code: string }).code;
    switch (code) {
      case 'auth/email-already-in-use':
        return 'This email is already registered.';
      case 'auth/invalid-email':
        return 'Invalid email address.';
      case 'auth/weak-password':
        return 'Password must be at least 6 characters.';
      case 'auth/user-not-found':
        return 'No user found with this email.';
      case 'auth/wrong-password':
        return 'Incorrect password.';
      case 'auth/network-request-failed':
        return 'Network error. Please try again.';
      default:
        return 'Something went wrong. Please try again.';
    }
  }
  return 'An unknown error occurred.';
}

export default function LoginPage() {
    const navigate = useNavigate();
    const location = useLocation();
    const from = location.state?.from?.pathname || ROUTES.HOMEPAGE_ROUTE;
  
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const [successMessage, setSuccessMessage] = useState('');
    const [loading, setLoading] = useState(false);
    const [mode, setMode] = useState('login');
  
    const handleLogin = async () => {
      if (!email || !password) {
        setError('Please fill in all fields.');
        return;
      }
      setLoading(true);
      try {
        const userCredential = await signInWithEmailAndPassword(auth, email, password);
        const user = userCredential.user;
    
        if (!user.emailVerified) {
          await user.reload();
          if (!user.emailVerified) {
            setError('Email not verified. Please check your inbox.');
            return;
          }
        }
    
        const idToken = await user.getIdToken();
        localStorage.setItem('token', idToken);
        navigate(from, { replace: true });
      } catch (error) {
        setError(parseFirebaseError(error));
      } finally {
        setLoading(false);
      }
    };

    const handleResendVerification = async () => {
      const user = auth.currentUser;
      if (user && !user.emailVerified) {
        await sendEmailVerification(user);
        setSuccessMessage('Verification email resent. Please check your inbox.');
      }
    };
  
    const handleRegister = async () => {
      if (!email || !password || !confirmPassword) {
        setError('Please fill in all fields.');
        return;
      }
      if (password !== confirmPassword) {
        setError('Passwords do not match.');
        return;
      }
      setLoading(true);
      try {
        const userCredential = await createUserWithEmailAndPassword(auth, email, password);
        const user = userCredential.user;
    
        await sendEmailVerification(user);
        localStorage.setItem('username', username);
        setSuccessMessage('Registration successful! A verification email has been sent to your email address. Please check your inbox or spam folder.');

        setEmail('');
        setPassword('');
        setConfirmPassword('');
        setMode('login');
      } catch (error) {
        setError(parseFirebaseError(error));
      } finally {
        setLoading(false);
      }
    };
  
    return (
      <Box
        display="flex"
        flexDirection="column"
        alignItems="center"
        justifyContent="center"
        minHeight="100vh"
        padding={2}
      >
        <Box position="absolute" top={16} left={16}>
          <Typography variant="h6" color="primary">
            MetroDiver
          </Typography>
        </Box>
  
        <Typography variant="h4" gutterBottom>
          {mode === 'login' ? 'Welcome back' : 'New user?'}
        </Typography>
  
        <Tabs
          value={mode}
          onChange={(e, newValue) => {
            setMode(newValue);
            setError('');
            setEmail('');
            setPassword('');
            setConfirmPassword('');
          }}
          sx={{ mb: 2 }}
        >
          <Tab label="Login" value="login" />
          <Tab label="Register" value="register" />
        </Tabs>

        {successMessage && (
          <Alert severity="success" sx={{ mb: 2, width: '100%', maxWidth: 400 }}>
            {successMessage}
          </Alert>
        )}
  
        {error && (
          <Alert severity="error" sx={{ mb: 2, width: '100%', maxWidth: 400 }}>
            {error}
          </Alert>
        )}
  
        <Box
          component="form"
          onSubmit={(e) => {
            e.preventDefault();
            mode === 'login' ? handleLogin() : handleRegister();
          }}
          noValidate
          autoComplete="off"
          sx={{ width: '100%', maxWidth: 400 }}
        >
          {mode === 'register' && (
          <TextField
            label="Username"
            variant="outlined"
            fullWidth
            margin="normal"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          )}
          <TextField
            label="Email"
            variant="outlined"
            fullWidth
            margin="normal"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <TextField
            label="Password"
            variant="outlined"
            fullWidth
            type="password"
            margin="normal"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {mode === 'register' && (
            <TextField
              label="Confirm Password"
              variant="outlined"
              fullWidth
              type="password"
              margin="normal"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
            />
          )}
  
          <Button
            variant="contained"
            color="primary"
            fullWidth
            size="large"
            sx={{ mt: 2, position: 'relative' }}
            type="submit"
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} color="inherit" /> : (mode === 'login' ? 'Login' : 'Register')}
          </Button>

          {error === 'Email not verified. Please check your inbox.' && (
            <Button
              variant="outlined"
              onClick={handleResendVerification}
              fullWidth
              sx={{ mt: 2 }}
            >
              Resend Verification Email
            </Button>
          )}

        </Box>
      </Box>
    );
  }