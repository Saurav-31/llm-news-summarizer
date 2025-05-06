import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Card,
  CardContent,
  Grid,
  CircularProgress,
  Box,
  Chip,
  Alert,
  Button,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import axios from 'axios';

// Styled components
const StyledCard = styled(Card)(({ theme }) => ({
  transition: 'transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out',
  borderRadius: '12px',
  '&:hover': {
    transform: 'translateY(-4px)',
    boxShadow: '0 8px 24px rgba(0,0,0,0.12)',
  },
}));

const StyledButton = styled(Button)(({ theme }) => ({
  transition: 'all 0.2s ease-in-out',
  '&:hover': {
    transform: 'scale(1.05)',
  },
}));

function App() {
  const [trends, setTrends] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchTrends = async () => {
    try {
      setLoading(true);
      setError(null);
      console.log('Fetching trends...');
      const response = await axios.get('http://localhost:8000/api/trends');
      console.log('Received trends:', response.data);
      setTrends(response.data);
    } catch (err) {
      console.error('Error fetching trends:', err);
      setError(err.response?.data?.detail || 'Failed to fetch trends. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTrends();
    // Refresh trends every 5 hours
    const interval = setInterval(fetchTrends, 300000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh" sx={{ bgcolor: '#f5f5f5' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box display="flex" flexDirection="column" justifyContent="center" alignItems="center" minHeight="100vh" gap={2} sx={{ bgcolor: '#f5f5f5' }}>
        <Alert severity="error" sx={{ maxWidth: 600 }}>
          {error}
        </Alert>
        <Button variant="contained" onClick={fetchTrends}>
          Retry
        </Button>
      </Box>
    );
  }

  return (
    <Box sx={{ bgcolor: '#f5f5f5', minHeight: '100vh', py: 4 }}>
      <Container maxWidth="lg">
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
          <Typography 
            variant="h4" 
            component="h1" 
            gutterBottom
            sx={{ 
              fontFamily: 'Inter, sans-serif',
              fontWeight: 600,
            }}
          >
            LLM News Analysis
          </Typography>
          <StyledButton variant="outlined" onClick={fetchTrends}>
            Refresh
          </StyledButton>
        </Box>
        <Grid container spacing={4}>
          {trends.map((trend, index) => (
            <Grid item xs={12} md={6} key={index}>
              <StyledCard elevation={2}>
                <CardContent>
                  <Box display="flex" alignItems="flex-start" mb={2}>
                    <Typography 
                      variant="h5" 
                      component="h2" 
                      sx={{ 
                        flexGrow: 1,
                        fontFamily: 'Inter, sans-serif',
                        fontWeight: 500,
                      }}
                    >
                      {trend.trend}
                    </Typography>
                    <Typography 
                      variant="caption" 
                      color="text.secondary"
                      sx={{ 
                        fontFamily: 'Inter, sans-serif',
                        ml: 2,
                        whiteSpace: 'nowrap',
                      }}
                    >
                      {new Date().toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric'
                      })}
                    </Typography>
                  </Box>
                  {trend.error ? (
                    <Alert severity="error" sx={{ mt: 2 }}>
                      {trend.error}
                    </Alert>
                  ) : (
                    <Typography 
                      variant="body1" 
                      color="text.secondary"
                      sx={{ 
                        fontFamily: 'Inter, sans-serif',
                        lineHeight: 1.6,
                      }}
                    >
                      {trend.summary}
                    </Typography>
                  )}
                </CardContent>
              </StyledCard>
            </Grid>
          ))}
        </Grid>
      </Container>
    </Box>
  );
}

export default App; 