import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import styled from 'styled-components';
import PoseVisualizer from './PoseVisualizer';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  gap: 20px;
`;

const UploadSection = styled.div`
  border: 2px dashed #ccc;
  border-radius: 10px;
  padding: 40px;
  text-align: center;
  background: #fafafa;
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    border-color: #4CAF50;
    background: #f0f8f0;
  }
`;

const HiddenInput = styled.input`
  display: none;
`;

const VideoPlayer = styled.video`
  max-width: 100%;
  max-height: 400px;
  margin: 20px auto;
  display: block;
  border: 1px solid #ddd;
  border-radius: 5px;
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
  background: ${props => props.variant === 'secondary' ? '#666' : '#4CAF50'};
  color: white;
  border: none;
  padding: 10px 20px;
  font-size: 16px;
  border-radius: 5px;
  cursor: pointer;
  transition: background 0.3s;

  &:hover {
    background: ${props => props.variant === 'secondary' ? '#555' : '#45a049'};
  }

  &:disabled {
    background: #ccc;
    cursor: not-allowed;
  }
`;

const ProgressBar = styled.div`
  width: 100%;
  height: 20px;
  background: #e0e0e0;
  border-radius: 10px;
  overflow: hidden;
  margin: 20px 0;
`;

const Progress = styled.div`
  height: 100%;
  background: #4CAF50;
  width: ${props => props.percent}%;
  transition: width 0.3s;
`;

const FrameInfo = styled.div`
  text-align: center;
  font-size: 14px;
  color: #666;
  margin: 10px 0;
`;

const CheckboxLabel = styled.label`
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
`;

const SkipFramesInput = styled.input`
  width: 60px;
  padding: 5px;
  border: 1px solid #ccc;
  border-radius: 3px;
`;

function VideoProcessor({ apiUrl, onError, onSuccess }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [videoUrl, setVideoUrl] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [currentFrame, setCurrentFrame] = useState(0);
  const [totalFrames, setTotalFrames] = useState(0);
  const [results, setResults] = useState([]);
  const [currentResult, setCurrentResult] = useState(null);
  const [displayBody, setDisplayBody] = useState(true);
  const [displayList, setDisplayList] = useState(true);
  const [skipFrames, setSkipFrames] = useState(5);
  const [paused, setPaused] = useState(false);
  
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const processingRef = useRef(false);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file && file.type.startsWith('video/')) {
      setSelectedFile(file);
      const url = URL.createObjectURL(file);
      setVideoUrl(url);
      setResults([]);
      setCurrentResult(null);
      setCurrentFrame(0);
      setTotalFrames(0);
    } else {
      onError({ message: 'Please select a valid video file' });
    }
  };

  const startProcessing = async () => {
    if (!selectedFile || !videoRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    
    // Set canvas size
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    // Calculate total frames
    const fps = 30; // Approximate
    const duration = video.duration;
    const estimatedFrames = Math.floor(duration * fps);
    setTotalFrames(estimatedFrames);
    
    setProcessing(true);
    processingRef.current = true;
    const frameResults = [];
    
    video.currentTime = 0;
    let frameCount = 0;

    const processFrame = async () => {
      if (!processingRef.current || video.ended) {
        setProcessing(false);
        if (frameResults.length > 0) {
          onSuccess(`Processed ${frameResults.length} frames`);
        }
        return;
      }

      if (!paused && frameCount % skipFrames === 0) {
        // Draw current frame to canvas
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        // Convert canvas to blob
        canvas.toBlob(async (blob) => {
          if (!blob) return;
          
          const formData = new FormData();
          formData.append('file', blob, 'frame.jpg');
          
          try {
            const response = await axios.post(`${apiUrl}/api/analyze/image`, formData, {
              headers: { 'Content-Type': 'multipart/form-data' },
              timeout: 10000
            });
            
            const result = {
              ...response.data,
              video_frame_number: frameCount,
              video_timestamp: video.currentTime
            };
            
            frameResults.push(result);
            setResults([...frameResults]);
            setCurrentResult(result);
          } catch (error) {
            console.error(`Error processing frame ${frameCount}:`, error);
          }
          
          setCurrentFrame(frameCount);
        }, 'image/jpeg', 0.8);
      }
      
      // Seek to next frame
      frameCount++;
      const nextTime = frameCount / fps;
      
      if (nextTime < duration && processingRef.current) {
        video.currentTime = nextTime;
        setTimeout(processFrame, 100); // Give time for seek
      } else {
        setProcessing(false);
        processingRef.current = false;
        onSuccess(`Processing complete! Analyzed ${frameResults.length} frames`);
      }
    };

    // Start processing
    video.addEventListener('seeked', processFrame, { once: true });
    video.currentTime = 0;
  };

  const stopProcessing = () => {
    processingRef.current = false;
    setProcessing(false);
    setPaused(false);
  };

  const togglePause = () => {
    setPaused(!paused);
  };

  const getCurrentFrameImage = () => {
    if (!videoRef.current || !canvasRef.current) return null;
    
    const video = videoRef.current;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0);
    
    return canvas.toDataURL('image/jpeg');
  };

  const getDisplayAngles = () => {
    const angles = [];
    if (displayBody) angles.push('body');
    if (displayList) angles.push('list');
    return angles;
  };

  const downloadResults = () => {
    const dataStr = JSON.stringify(results, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = 'pose_analysis_results.json';
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  return (
    <Container>
      <UploadSection onClick={() => document.getElementById('video-input').click()}>
        <HiddenInput
          id="video-input"
          type="file"
          accept="video/*"
          onChange={handleFileSelect}
        />
        
        {videoUrl ? (
          <VideoPlayer ref={videoRef} src={videoUrl} controls />
        ) : (
          <>
            <h3>Click to upload a video</h3>
            <p>or drag and drop</p>
            <p style={{ color: '#666', fontSize: '14px' }}>
              Supported formats: MP4, AVI, MOV
            </p>
          </>
        )}
      </UploadSection>

      <canvas ref={canvasRef} style={{ display: 'none' }} />

      {selectedFile && (
        <>
          <Controls>
            {!processing ? (
              <Button onClick={startProcessing}>
                Start Analysis
              </Button>
            ) : (
              <>
                <Button onClick={togglePause} variant="secondary">
                  {paused ? 'Resume' : 'Pause'}
                </Button>
                <Button onClick={stopProcessing} variant="secondary">
                  Stop
                </Button>
              </>
            )}
            
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <label>Process every</label>
              <SkipFramesInput
                type="number"
                min="1"
                max="30"
                value={skipFrames}
                onChange={(e) => setSkipFrames(parseInt(e.target.value) || 1)}
                disabled={processing}
              />
              <span>frames</span>
            </div>
            
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
            
            {results.length > 0 && (
              <Button onClick={downloadResults} variant="secondary">
                Download Results (JSON)
              </Button>
            )}
          </Controls>

          {processing && (
            <>
              <ProgressBar>
                <Progress percent={(currentFrame / totalFrames) * 100} />
              </ProgressBar>
              <FrameInfo>
                Processing frame {currentFrame} of ~{totalFrames} 
                ({results.length} frames analyzed)
              </FrameInfo>
            </>
          )}

          {currentResult && (
            <div>
              <h3>Current Frame Analysis</h3>
              <FrameInfo>
                Frame: {currentResult.video_frame_number} | 
                Time: {currentResult.video_timestamp?.toFixed(2)}s | 
                Persons: {currentResult.frame_metrics.detected_persons}
              </FrameInfo>
              
              <PoseVisualizer
                image={getCurrentFrameImage()}
                result={currentResult}
                displayAngles={getDisplayAngles()}
              />
            </div>
          )}
        </>
      )}
    </Container>
  );
}

export default VideoProcessor;