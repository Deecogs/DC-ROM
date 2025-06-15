import React, { useState } from 'react';
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

const PreviewImage = styled.img`
  max-width: 300px;
  max-height: 300px;
  margin: 20px auto;
  display: block;
  border: 1px solid #ddd;
  border-radius: 5px;
`;

const Button = styled.button`
  background: #4CAF50;
  color: white;
  border: none;
  padding: 10px 30px;
  font-size: 16px;
  border-radius: 5px;
  cursor: pointer;
  transition: background 0.3s;

  &:hover {
    background: #45a049;
  }

  &:disabled {
    background: #ccc;
    cursor: not-allowed;
  }
`;

const Controls = styled.div`
  display: flex;
  gap: 20px;
  align-items: center;
  justify-content: center;
  margin: 20px 0;
`;

const CheckboxLabel = styled.label`
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
`;

const ResultSection = styled.div`
  margin-top: 30px;
`;

const JsonView = styled.pre`
  background: #f5f5f5;
  padding: 15px;
  border-radius: 5px;
  overflow: auto;
  max-height: 400px;
  font-size: 12px;
`;

function ImageUploader({ apiUrl, onError, onSuccess }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [displayBody, setDisplayBody] = useState(true);
  const [displayList, setDisplayList] = useState(true);
  const [showJson, setShowJson] = useState(false);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file && file.type.startsWith('image/')) {
      setSelectedFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreviewUrl(reader.result);
      };
      reader.readAsDataURL(file);
      setResult(null);
    } else {
      onError({ message: 'Please select a valid image file' });
    }
  };

  const analyzeImage = async () => {
    if (!selectedFile) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await axios.post(`${apiUrl}/api/analyze/image`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 30000
      });

      setResult(response.data);
      onSuccess(`Analysis complete! Detected ${response.data.frame_metrics.detected_persons} person(s)`);
    } catch (error) {
      console.error('Error:', error);
      onError({ 
        message: error.response?.data?.detail || 'Failed to analyze image' 
      });
    } finally {
      setLoading(false);
    }
  };

  const getDisplayAngles = () => {
    const angles = [];
    if (displayBody) angles.push('body');
    if (displayList) angles.push('list');
    return angles;
  };

  return (
    <Container>
      <UploadSection onClick={() => document.getElementById('file-input').click()}>
        <HiddenInput
          id="file-input"
          type="file"
          accept="image/*"
          onChange={handleFileSelect}
        />
        
        {previewUrl ? (
          <PreviewImage src={previewUrl} alt="Preview" />
        ) : (
          <>
            <h3>Click to upload an image</h3>
            <p>or drag and drop</p>
            <p style={{ color: '#666', fontSize: '14px' }}>
              Supported formats: JPG, PNG, GIF
            </p>
          </>
        )}
      </UploadSection>

      {selectedFile && (
        <Controls>
          <Button onClick={analyzeImage} disabled={loading}>
            {loading ? 'Analyzing...' : 'Analyze Pose'}
          </Button>
          
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
          
          {result && (
            <CheckboxLabel>
              <input
                type="checkbox"
                checked={showJson}
                onChange={(e) => setShowJson(e.target.checked)}
              />
              Show JSON
            </CheckboxLabel>
          )}
        </Controls>
      )}

      {result && (
        <ResultSection>
          <PoseVisualizer
            image={previewUrl}
            result={result}
            displayAngles={getDisplayAngles()}
          />
          
          {showJson && (
            <>
              <h3>API Response (JSON)</h3>
              <JsonView>{JSON.stringify(result, null, 2)}</JsonView>
            </>
          )}
        </ResultSection>
      )}
    </Container>
  );
}

export default ImageUploader;