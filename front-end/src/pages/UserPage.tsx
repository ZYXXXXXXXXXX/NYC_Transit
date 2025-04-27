import React, { useEffect, useState } from 'react';
import { Card, CardContent, Typography, Button, Box, Avatar, CircularProgress } from '@mui/material';
import { auth } from '../resources/Firebase';
import { signOut } from 'firebase/auth';
import { useNavigate } from 'react-router-dom';
import { getStorage, ref, uploadBytes, getDownloadURL } from 'firebase/storage';

export default function UserPage() {
  const navigate = useNavigate();
  const [user, setUser] = useState(() => auth.currentUser);
  const [username, setUsername] = useState<string | null>(null);
  const [avatarUrl, setAvatarUrl] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [loggingOut, setLoggingOut] = useState(false);

  const storage = getStorage();

  const handleLogout = async () => {
    setLoggingOut(true);
    try {
      await signOut(auth);
      localStorage.removeItem('token');
      navigate('/login');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setLoggingOut(false);
    }
  };

  const handleUploadAvatar = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!auth.currentUser) return; 
    
    const avatarRef = ref(storage, `avatars/${auth.currentUser.uid}`);
    setUploading(true);
    
    try {
      await uploadBytes(avatarRef, file);
      const downloadUrl = await getDownloadURL(avatarRef);
      setAvatarUrl(downloadUrl);

      localStorage.setItem('avatarUrl', downloadUrl);
  
    } catch (error) {
      console.error('Avatar upload error:', error);
      alert('Upload failed: ' + (error as Error).message);
    } finally {
      setUploading(false);
    }
  };

  useEffect(() => {
    const fetchAvatar = async () => {
      if (!auth.currentUser) return;
      const storage = getStorage();
      const avatarRef = ref(storage, `avatars/${auth.currentUser.uid}`);
      try {
        const url = await getDownloadURL(avatarRef);
        setAvatarUrl(url);
      } catch (error) {
        console.log('No avatar found for this user.');
      }
    };
  
    setUser(auth.currentUser);
    fetchAvatar();

    const savedUsername = localStorage.getItem('username');
    if (savedUsername) {
      setUsername(savedUsername);

    setUser(auth.currentUser);
    };

  }, []);

  console.log('currentUser:', auth.currentUser);

  if (!user) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh" p={2}>
      <Card sx={{ maxWidth: 400, width: '100%', textAlign: 'center', p: 3, boxShadow: 3 }}>
        <Avatar
          src={avatarUrl || undefined}
          sx={{ margin: '0 auto', width: 100, height: 100, mb: 2 }}
        >
          {!avatarUrl && (user.email?.charAt(0).toUpperCase() || 'U')}
        </Avatar>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Welcome, {username || user.email || 'User'}!
          </Typography>
          <Typography variant="body2" color="textSecondary">
            User ID: {user.uid}
          </Typography>

          <Box mt={2}>
            <input
              type="file"
              accept="image/*"
              id="avatar-upload"
              hidden
              onChange={handleUploadAvatar}
            />
            <label htmlFor="avatar-upload">
              <Button
                variant="outlined"
                component="span"
                fullWidth
                sx={{ mt: 2 }}
                disabled={uploading}
              >
                {uploading ? <CircularProgress size={24} color="inherit" /> : 'Upload New Avatar'}
              </Button>
            </label>
          </Box>

          <Button
            variant="contained"
            color="primary"
            fullWidth
            sx={{ mt: 2 }}
            onClick={handleLogout}
            disabled={loggingOut}
          >
            {loggingOut ? <CircularProgress size={24} color="inherit" /> : 'Logout'}
          </Button>
        </CardContent>
      </Card>
    </Box>
  );
}