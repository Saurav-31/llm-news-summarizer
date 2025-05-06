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
import axios from 'axios';

function App() {
  const [trends, setTrends] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchTrends = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get('http://localhost:8000/api/trends');
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
    // Refresh trends every 5 minutes
    const interval = setInterval(fetchTrends, 300000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box display="flex" flexDirection="column" justifyContent="center" alignItems="center" minHeight="100vh" gap={2}>
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
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Typography variant="h4" component="h1" gutterBottom>
          LLM News Analysis
        </Typography>
        <Button variant="outlined" onClick={fetchTrends}>
          Refresh
        </Button>
      </Box>
      <Grid container spacing={3}>
        {trends.map((trend, index) => (
          <Grid item xs={12} md={6} key={index}>
            <Card elevation={3}>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <Typography variant="h5" component="h2" sx={{ flexGrow: 1 }}>
                    {trend.trend}
                  </Typography>
                  <Chip
                    label={`${trend.tweet_count} tweets`}
                    color="primary"
                    size="small"
                  />
                </Box>
                {trend.error ? (
                  <Alert severity="error" sx={{ mt: 2 }}>
                    {trend.error}
                  </Alert>
                ) : (
                  <Typography variant="body1" color="text.secondary">
                    {trend.summary}
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Container>
  );
}

export default App; 