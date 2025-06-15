// Example React code to consume the Pose Analyzer API

// 1. Single Image Analysis
async function analyzeImage(imageFile) {
    const formData = new FormData();
    formData.append('file', imageFile);
    
    try {
        const response = await fetch('http://localhost:8000/api/analyze/image', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) throw new Error('Analysis failed');
        
        const result = await response.json();
        console.log('Analysis result:', result);
        
        // Process result
        displayPose(result);
        
    } catch (error) {
        console.error('Error:', error);
    }
}

// 2. Video Analysis
async function analyzeVideo(videoFile, startTime, endTime) {
    const formData = new FormData();
    formData.append('file', videoFile);
    
    const params = new URLSearchParams();
    if (startTime) params.append('start_time', startTime);
    if (endTime) params.append('end_time', endTime);
    params.append('skip_frames', '1');
    
    try {
        const response = await fetch(`http://localhost:8000/api/analyze/video?${params}`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) throw new Error('Analysis failed');
        
        const result = await response.json();
        console.log('Video analysis result:', result);
        
        // Process frames
        result.frames.forEach(frame => {
            displayPose(frame);
        });
        
    } catch (error) {
        console.error('Error:', error);
    }
}

// 3. Real-time WebSocket Streaming
function startRealtimeAnalysis(videoStream) {
    const ws = new WebSocket('ws://localhost:8000/ws');
    
    ws.onopen = () => {
        console.log('WebSocket connected');
    };
    
    ws.onmessage = (event) => {
        const result = JSON.parse(event.data);
        console.log('Real-time result:', result);
        
        // Update visualization in real-time
        displayPose(result);
    };
    
    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
    };
    
    ws.onclose = () => {
        console.log('WebSocket disconnected');
    };
    
    // Send frames from video stream
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    function sendFrame() {
        if (ws.readyState === WebSocket.OPEN) {
            canvas.width = videoStream.videoWidth;
            canvas.height = videoStream.videoHeight;
            ctx.drawImage(videoStream, 0, 0);
            
            canvas.toBlob((blob) => {
                if (blob) {
                    ws.send(blob);
                }
            }, 'image/jpeg', 0.9);
        }
    }
    
    // Send frames at 30 FPS
    const intervalId = setInterval(sendFrame, 1000 / 30);
    
    return {
        stop: () => {
            clearInterval(intervalId);
            ws.close();
        }
    };
}

// 4. Display Pose on Canvas
function displayPose(frameData) {
    const canvas = document.getElementById('poseCanvas');
    const ctx = canvas.getContext('2d');
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    frameData.persons.forEach(person => {
        // Draw skeleton
        drawSkeleton(ctx, person.keypoints);
        
        // Draw angles
        drawAngles(ctx, person.angles, person.keypoints);
        
        // Display metrics
        displayMetrics(person.metrics);
    });
}

function drawSkeleton(ctx, keypoints) {
    // Define connections
    const connections = [
        ['left_shoulder', 'right_shoulder'],
        ['left_shoulder', 'left_elbow'],
        ['left_elbow', 'left_wrist'],
        ['right_shoulder', 'right_elbow'],
        ['right_elbow', 'right_wrist'],
        ['left_shoulder', 'left_hip'],
        ['right_shoulder', 'right_hip'],
        ['left_hip', 'right_hip'],
        ['left_hip', 'left_knee'],
        ['left_knee', 'left_ankle'],
        ['right_hip', 'right_knee'],
        ['right_knee', 'right_ankle']
    ];
    
    // Draw connections
    ctx.strokeStyle = '#00ff00';
    ctx.lineWidth = 2;
    
    connections.forEach(([start, end]) => {
        if (keypoints[start] && keypoints[end] && 
            keypoints[start].confidence > 0.3 && keypoints[end].confidence > 0.3) {
            ctx.beginPath();
            ctx.moveTo(keypoints[start].x, keypoints[start].y);
            ctx.lineTo(keypoints[end].x, keypoints[end].y);
            ctx.stroke();
        }
    });
    
    // Draw keypoints
    Object.entries(keypoints).forEach(([name, point]) => {
        if (point.confidence > 0.3) {
            ctx.fillStyle = `rgba(255, 0, 0, ${point.confidence})`;
            ctx.beginPath();
            ctx.arc(point.x, point.y, 5, 0, 2 * Math.PI);
            ctx.fill();
        }
    });
}

function drawAngles(ctx, angles, keypoints) {
    ctx.fillStyle = '#ffff00';
    ctx.font = '14px Arial';
    
    // Display joint angles near joints
    const anglePositions = {
        'right_knee': keypoints.right_knee,
        'left_knee': keypoints.left_knee,
        'right_elbow': keypoints.right_elbow,
        'left_elbow': keypoints.left_elbow
    };
    
    Object.entries(anglePositions).forEach(([angleName, position]) => {
        if (position && angles.joint_angles[angleName] !== null) {
            ctx.fillText(
                `${angles.joint_angles[angleName]}°`,
                position.x + 10,
                position.y - 10
            );
        }
    });
}

function displayMetrics(metrics) {
    const metricsDiv = document.getElementById('metrics');
    metricsDiv.innerHTML = `
        <p>Height: ${metrics.height_pixels}px</p>
        <p>Velocity: ${metrics.velocity.x.toFixed(2)}, ${metrics.velocity.y.toFixed(2)} px/s</p>
        <p>Direction: ${metrics.movement_direction}</p>
    `;
}

// 5. React Component Example
import React, { useState, useRef, useEffect } from 'react';

function PoseAnalyzer() {
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [results, setResults] = useState(null);
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const wsRef = useRef(null);
    
    const startWebcamAnalysis = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            videoRef.current.srcObject = stream;
            
            // Start WebSocket connection
            const ws = new WebSocket('ws://localhost:8000/ws');
            wsRef.current = ws;
            
            ws.onmessage = (event) => {
                const result = JSON.parse(event.data);
                setResults(result);
                drawPoseOnCanvas(result);
            };
            
            // Send frames periodically
            const sendFrame = () => {
                if (ws.readyState === WebSocket.OPEN && videoRef.current) {
                    const canvas = document.createElement('canvas');
                    canvas.width = videoRef.current.videoWidth;
                    canvas.height = videoRef.current.videoHeight;
                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(videoRef.current, 0, 0);
                    
                    canvas.toBlob((blob) => {
                        if (blob) ws.send(blob);
                    }, 'image/jpeg', 0.9);
                }
            };
            
            setInterval(sendFrame, 100); // 10 FPS
            setIsAnalyzing(true);
            
        } catch (error) {
            console.error('Error starting webcam:', error);
        }
    };
    
    const stopAnalysis = () => {
        if (wsRef.current) {
            wsRef.current.close();
        }
        if (videoRef.current && videoRef.current.srcObject) {
            videoRef.current.srcObject.getTracks().forEach(track => track.stop());
        }
        setIsAnalyzing(false);
    };
    
    const drawPoseOnCanvas = (result) => {
        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        
        // Clear and draw video frame
        ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
        
        // Draw pose overlay
        result.persons.forEach(person => {
            drawSkeleton(ctx, person.keypoints);
            drawAngles(ctx, person.angles, person.keypoints);
        });
    };
    
    return (
        <div>
            <h1>Pose Analyzer</h1>
            
            <div style={{ position: 'relative' }}>
                <video ref={videoRef} style={{ display: 'none' }} />
                <canvas ref={canvasRef} width={640} height={480} />
            </div>
            
            <div>
                {!isAnalyzing ? (
                    <button onClick={startWebcamAnalysis}>Start Analysis</button>
                ) : (
                    <button onClick={stopAnalysis}>Stop Analysis</button>
                )}
            </div>
            
            {results && (
                <div>
                    <h3>Results:</h3>
                    <pre>{JSON.stringify(results, null, 2)}</pre>
                </div>
            )}
        </div>
    );
}

export default PoseAnalyzer;