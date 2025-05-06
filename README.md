# LLM News Scraper

This application fetches news articles, analyzes them using OpenAI's GPT-3.5, and presents the information in a modern web interface.

## Features

- Real-time news article fetching
- AI-powered analysis of news content
- Modern, responsive web interface
- Interactive data visualization
- Real-time updates

## Tech Stack

### Frontend
- React.js
- Material-UI
- Chart.js for data visualization
- Axios for API calls

### Backend
- FastAPI
- OpenAI API integration
- News API integration
- SQLite database

## Setup Instructions

1. Clone the repository
2. Install dependencies:
   ```bash
   # Backend
   cd backend
   pip install -r requirements.txt

   # Frontend
   cd frontend
   npm install
   ```

3. Set up environment variables:
   - Create a `.env` file in the backend directory
   - Add your OpenAI API key and News API key

4. Start the application:
   ```bash
   # Using Docker Compose
   docker-compose up

   # Or manually
   # Backend
   cd backend
   uvicorn main:app --reload

   # Frontend
   cd frontend
   npm start
   ```

## Architecture

- The application uses News API to fetch news articles
- OpenAI's GPT-3.5 is used for analyzing the content
- The backend processes and stores the data
- The frontend provides an interactive interface for users

## Contributing

Feel free to submit issues and enhancement requests! 