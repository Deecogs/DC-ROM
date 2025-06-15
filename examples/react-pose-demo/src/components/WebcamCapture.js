import React, { useState, useRef, useCallback, useEffect } from 'react';
import Webcam from 'react-webcam';
import axios from 'axios';
import styled from 'styled-components';
import PoseVisualizer from './PoseVisualizer';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  gap: 20px;
`;

const WebcamContainer = styled.div`
  position: relative;
  max-width: 800px;
  margin: 0 auto;
`;

const Controls = styled.div`
  display: flex;
  gap: 20px;
  align-items: center;
  justify-content: center;
  margin: 20px 0;
  flex-wrap: wrap;
`;

const Button = styled.button`
  background: ${props => props.variant === 'danger' ? '#f44336' : '#4CAF50'};
  color: white;
  border: none;
  padding: 10px 20px;
  font-size: 16px;
  border-radius: 5px;
  cursor: pointer;
  transition: background 0.3s;

  &:hover {
    background: ${props => props.variant === 'danger' ? '#da190b' : '#45a049'};
  }

  &:disabled {
    background: #ccc;
    cursor: not-allowed;
  }
`;

const StatusIndicator = styled.div`
  position: absolute;
  top: 10px;
  right: 10px;
  padding: 5px 10px;
  background: ${props => props.active ? '#4CAF50' : '#666'};
  color: white;
  border-radius: 5px;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 5px;
`;

const StatusDot = styled.div`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: ${props => props.active ? '#fff' : '#999'};
  animation: ${props => props.active ? 'pulse 1s infinite' : 'none'};

  @keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
  }
`;

const CheckboxLabel = styled.label`
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
`;

const FpsDisplay = styled.div`
  position: absolute;
  top: 10px;
  left: 10px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 5px 10px;
  border-radius: 5px;
  font-size: 12px;
`;

const ResultsContainer = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-top: 20px;
`;

const ResultSection = styled.div`
  border: 1px solid #ddd;
  border-radius: 10px;
  padding: 20px;
  background: #fafafa;
`;

function WebcamCapture({ apiUrl, onError, onSuccess }) {
  const [isCapturing, setIsCapturing] = useState(false);
  const [currentResult, setCurrentResult] = useState(null);
  const [capturedImage, setCapturedImage] = useState(null);
  const [displayBody, setDisplayBody] = useState(true);
  const [displayList, setDisplayList] = useState(true);
  const [fps, setFps] = useState(0);
  const [mode, setMode] = useState('snapshot'); // 'snapshot' or 'realtime'
  
  const webcamRef = useRef(null);
  const intervalRef = useRef(null);
  const lastFrameTime = useRef(Date.now());
  const frameCount = useRef(0);

  const capture = useCallback(async () => {
    const imageSrc = webcamRef.current.getScreenshot();
    if (!imageSrc) return;

    // Convert base64 to blob
    const base64Response = await fetch(imageSrc);
    const blob = await base64Response.blob();
    
    const formData = new FormData();
    formData.append('file', blob, 'webcam.jpg');
    
    try {
      const response = await axios.post(`${apiUrl}/api/analyze/image`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 5000
      });
      
      setCurrentResult(response.data);
      setCapturedImage(imageSrc);
      
      // Calculate FPS
      frameCount.current++;
      const now = Date.now();
      const elapsed = now - lastFrameTime.current;
      if (elapsed >= 1000) {
        setFps(Math.round(frameCount.current * 1000 / elapsed));
        frameCount.current = 0;
        lastFrameTime.current = now;
      }
      
    } catch (error) {
      console.error('Error analyzing frame:', error);
      if (mode === 'snapshot') {
        onError({ message: 'Failed to analyze image' });
      }
    }
  }, [apiUrl, mode, onError]);

  const handleSnapshot = () => {
    setMode('snapshot');
    capture();
    onSuccess('Snapshot captured and analyzed!');
  };

  const startRealtime = () => {
    setMode('realtime');
    setIsCapturing(true);
    frameCount.current = 0;
    lastFrameTime.current = Date.now();
    
    // Capture at ~10 FPS
    intervalRef.current = setInterval(() => {
      capture();
    }, 100);
    
    onSuccess('Real-time analysis started!');
  };

  const stopRealtime = () => {
    setIsCapturing(false);
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    setFps(0);
  };

  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  const getDisplayAngles = () => {
    const angles = [];
    if (displayBody) angles.push('body');
    if (displayList) angles.push('list');
    return angles;
  };

  const videoConstraints = {
    width: 1280,
    height: 720,
    facingMode: "user"
  };

  return (
    <Container>
      <WebcamContainer>
        <Webcam
          ref={webcamRef}
          screenshotFormat="image/jpeg"
          videoConstraints={videoConstraints}
          style={{ width: '100%', borderRadius: '10px' }}
        />
        
        {isCapturing && (
          <>
            <StatusIndicator active>
              <StatusDot active />
              LIVE
            </StatusIndicator>
            <FpsDisplay>
              Analysis FPS: {fps}
            </FpsDisplay>
          </>
        )}
      </WebcamContainer>

      <Controls>
        <Button onClick={handleSnapshot} disabled={isCapturing}>
          Take Snapshot
        </Button>
        
        {!isCapturing ? (
          <Button onClick={startRealtime}>
            Start Real-time Analysis
          </Button>
        ) : (
          <Button onClick={stopRealtime} variant="danger">
            Stop Real-time
          </Button>
        )}
        
        <CheckboxLabel>
          <input
            type="checkbox"
            checked={displayBody}
            onChange={(e) => setDisplayBody(e.target.checked)}
          />
          Show angles on body
        </CheckboxLabel>
        
        <CheckboxLabel>
          <input
            type="checkbox"
            checked={displayList}
            onChange={(e) => setDisplayList(e.target.checked)}
          />
          Show angle list
        </CheckboxLabel>
      </Controls>

      {currentResult && (
        <ResultsContainer>
          <ResultSection>
            <h3>Live Webcam</h3>
            <WebcamContainer>
              <Webcam
                ref={webcamRef}
                screenshotFormat="image/jpeg"
                videoConstraints={videoConstraints}
                style={{ width: '100%', borderRadius: '10px' }}
              />
            </WebcamContainer>
          </ResultSection>
          
          <ResultSection>
            <h3>Pose Analysis</h3>
            {capturedImage && (
              <PoseVisualizer
                image={capturedImage}
                result={currentResult}
                displayAngles={getDisplayAngles()}
              />
            )}
          </ResultSection>
        </ResultsContainer>
      )}
    </Container>
  );
}

export default WebcamCapture;