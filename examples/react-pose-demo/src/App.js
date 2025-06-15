import React, { useState, useRef, useCallback } from 'react';
import axios from 'axios';
import styled from 'styled-components';
import Webcam from 'react-webcam';
import PoseVisualizer from './components/PoseVisualizer';
import ImageUploader from './components/ImageUploader';
import VideoProcessor from './components/VideoProcessor';
import WebcamCapture from './components/WebcamCapture';

const API_URL = 'http://localhost:8000';

const Container = styled.div`
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  font-family: Arial, sans-serif;
`;

const Header = styled.h1`
  text-align: center;
  color: #333;
  margin-bottom: 30px;
`;

const TabContainer = styled.div`
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
  border-bottom: 2px solid #e0e0e0;
`;

const Tab = styled.button`
  padding: 10px 20px;
  border: none;
  background: ${props => props.active ? '#4CAF50' : '#f0f0f0'};
  color: ${props => props.active ? 'white' : '#666'};
  cursor: pointer;
  font-size: 16px;
  border-radius: 5px 5px 0 0;
  transition: all 0.3s;

  &:hover {
    background: ${props => props.active ? '#45a049' : '#e0e0e0'};
  }
`;

const Content = styled.div`
  background: #f9f9f9;
  padding: 20px;
  border-radius: 0 0 10px 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
`;

const StatusMessage = styled.div`
  padding: 10px;
  margin: 10px 0;
  border-radius: 5px;
  background: ${props => props.error ? '#ffebee' : '#e8f5e9'};
  color: ${props => props.error ? '#c62828' : '#2e7d32'};
  display: ${props => props.show ? 'block' : 'none'};
`;

function App() {
  const [activeTab, setActiveTab] = useState('image');
  const [status, setStatus] = useState({ show: false, error: false, message: '' });
  const [apiHealth, setApiHealth] = useState(null);

  // Check API health on mount
  React.useEffect(() => {
    checkApiHealth();
  }, []);

  const checkApiHealth = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/health`);
      setApiHealth(response.data);
      setStatus({
        show: true,
        error: false,
        message: `API is running! Model: ${response.data.model}, Version: ${response.data.version}`
      });
      setTimeout(() => setStatus({ show: false }), 3000);
    } catch (error) {
      setApiHealth(null);
      setStatus({
        show: true,
        error: true,
        message: 'Cannot connect to API. Make sure it\'s running on http://localhost:8000'
      });
    }
  };

  const handleError = (error) => {
    setStatus({
      show: true,
      error: true,
      message: error.message || 'An error occurred'
    });
    setTimeout(() => setStatus({ show: false }), 5000);
  };

  const handleSuccess = (message) => {
    setStatus({
      show: true,
      error: false,
      message
    });
    setTimeout(() => setStatus({ show: false }), 3000);
  };

  return (
    <Container>
      <Header>Pose Analyzer - Sports2D Style Visualization</Header>
      
      <StatusMessage show={status.show} error={status.error}>
        {status.message}
      </StatusMessage>

      <TabContainer>
        <Tab active={activeTab === 'image'} onClick={() => setActiveTab('image')}>
          Image Analysis
        </Tab>
        <Tab active={activeTab === 'video'} onClick={() => setActiveTab('video')}>
          Video Analysis
        </Tab>
        <Tab active={activeTab === 'webcam'} onClick={() => setActiveTab('webcam')}>
          Webcam Live
        </Tab>
      </TabContainer>

      <Content>
        {activeTab === 'image' && (
          <ImageUploader 
            apiUrl={API_URL}
            onError={handleError}
            onSuccess={handleSuccess}
          />
        )}
        
        {activeTab === 'video' && (
          <VideoProcessor 
            apiUrl={API_URL}
            onError={handleError}
            onSuccess={handleSuccess}
          />
        )}
        
        {activeTab === 'webcam' && (
          <WebcamCapture 
            apiUrl={API_URL}
            onError={handleError}
            onSuccess={handleSuccess}
          />
        )}
      </Content>
    </Container>
  );
}

export default App;