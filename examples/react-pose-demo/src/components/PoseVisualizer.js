import React, { useRef, useEffect } from 'react';
import styled from 'styled-components';

const CanvasContainer = styled.div`
  position: relative;
  display: inline-block;
  margin: 20px 0;
`;

const Canvas = styled.canvas`
  border: 1px solid #ddd;
  max-width: 100%;
  height: auto;
`;

const InfoPanel = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 10px;
  max-width: 350px;
  max-height: 100%;
  overflow-y: auto;
  font-size: 12px;
`;

const PersonSection = styled.div`
  margin-bottom: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.3);
  padding-bottom: 10px;
`;

const AngleItem = styled.div`
  display: flex;
  align-items: center;
  margin: 5px 0;
  padding-left: 20px;
`;

const AngleName = styled.span`
  width: 120px;
  color: #ccc;
`;

const AngleValue = styled.span`
  width: 60px;
  color: ${props => props.color || '#fff'};
  font-weight: bold;
`;

const ProgressBar = styled.div`
  width: 100px;
  height: 10px;
  background: #333;
  margin-left: 10px;
  position: relative;
  border: 1px solid #555;
`;

const ProgressFill = styled.div`
  height: 100%;
  background: ${props => props.color || '#0f0'};
  width: ${props => props.percent}%;
`;

class PoseVisualizer extends React.Component {
  constructor(props) {
    super(props);
    this.canvasRef = React.createRef();
    this.colors = [
      [255, 0, 0], [0, 0, 255], [255, 255, 0], 
      [255, 0, 255], [0, 255, 255], [128, 0, 128]
    ];
  }

  componentDidMount() {
    this.drawPose();
  }

  componentDidUpdate(prevProps) {
    if (prevProps.image !== this.props.image || prevProps.result !== this.props.result) {
      this.drawPose();
    }
  }

  drawPose = () => {
    const canvas = this.canvasRef.current;
    if (!canvas || !this.props.image) return;

    const ctx = canvas.getContext('2d');
    const img = new Image();
    
    img.onload = () => {
      canvas.width = img.width;
      canvas.height = img.height;
      
      // Draw image
      ctx.drawImage(img, 0, 0);
      
      // Draw pose if result exists
      if (this.props.result && this.props.result.persons) {
        this.props.result.persons.forEach((person, idx) => {
          const color = this.colors[idx % this.colors.length];
          this.drawPerson(ctx, person, color, idx);
        });
      }
      
      // Draw frame info
      if (this.props.result) {
        this.drawFrameInfo(ctx, this.props.result);
      }
    };
    
    img.src = this.props.image;
  };

  drawPerson = (ctx, person, color, personIdx) => {
    const colorStr = `rgb(${color[0]}, ${color[1]}, ${color[2]})`;
    
    // Draw skeleton
    this.drawSkeleton(ctx, person.keypoints, colorStr);
    
    // Draw keypoints
    this.drawKeypoints(ctx, person.keypoints);
    
    // Draw bounding box
    this.drawBoundingBox(ctx, person.keypoints, person.person_id, colorStr);
    
    // Draw angles on body if enabled
    if (this.props.displayAngles.includes('body')) {
      this.drawAnglesOnBody(ctx, person, colorStr);
    }
  };

  drawSkeleton = (ctx, keypoints, color) => {
    const connections = [
      // Face
      ['left_ear', 'left_eye'], ['right_ear', 'right_eye'],
      ['left_eye', 'nose'], ['right_eye', 'nose'],
      
      // Arms
      ['left_shoulder', 'left_elbow'], ['left_elbow', 'left_wrist'],
      ['right_shoulder', 'right_elbow'], ['right_elbow', 'right_wrist'],
      
      // Torso
      ['left_shoulder', 'right_shoulder'],
      ['left_shoulder', 'left_hip'], ['right_shoulder', 'right_hip'],
      ['left_hip', 'right_hip'],
      
      // Legs
      ['left_hip', 'left_knee'], ['left_knee', 'left_ankle'],
      ['right_hip', 'right_knee'], ['right_knee', 'right_ankle'],
      
      // Feet
      ['left_ankle', 'left_heel'], ['left_ankle', 'left_foot_index'],
      ['left_heel', 'left_foot_index'],
      ['right_ankle', 'right_heel'], ['right_ankle', 'right_foot_index'],
      ['right_heel', 'right_foot_index'],
      
      // Center
      ['neck', 'hip_center']
    ];

    ctx.strokeStyle = color;
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
  };

  drawKeypoints = (ctx, keypoints) => {
    Object.values(keypoints).forEach(kp => {
      if (kp.confidence > 0.3) {
        // Color based on confidence (red to green)
        const green = Math.floor(255 * kp.confidence);
        const red = Math.floor(255 * (1 - kp.confidence));
        
        ctx.fillStyle = `rgb(${red}, ${green}, 0)`;
        ctx.beginPath();
        ctx.arc(kp.x, kp.y, 5, 0, 2 * Math.PI);
        ctx.fill();
        
        // White border
        ctx.strokeStyle = 'white';
        ctx.lineWidth = 1;
        ctx.stroke();
      }
    });
  };

  drawBoundingBox = (ctx, keypoints, personId, color) => {
    const validPoints = Object.values(keypoints)
      .filter(kp => kp.confidence > 0.3)
      .map(kp => [kp.x, kp.y]);
    
    if (validPoints.length === 0) return;
    
    const xs = validPoints.map(p => p[0]);
    const ys = validPoints.map(p => p[1]);
    
    const minX = Math.min(...xs) - 20;
    const minY = Math.min(...ys) - 20;
    const maxX = Math.max(...xs) + 20;
    const maxY = Math.max(...ys) + 20;
    
    // Draw box
    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    ctx.strokeRect(minX, minY, maxX - minX, maxY - minY);
    
    // Draw label
    const label = `Person ${personId}`;
    ctx.fillStyle = color;
    ctx.fillRect(minX, minY - 25, 80, 25);
    ctx.fillStyle = 'white';
    ctx.font = 'bold 14px Arial';
    ctx.fillText(label, minX + 5, minY - 8);
  };

  drawAnglesOnBody = (ctx, person, color) => {
    const angles = person.angles;
    
    // Draw joint angles
    Object.entries(angles.joint_angles).forEach(([name, value]) => {
      if (value !== null) {
        this.drawJointAngle(ctx, name, value, person.keypoints, color);
      }
    });
    
    // Draw segment angles
    Object.entries(angles.segment_angles).forEach(([name, value]) => {
      if (value !== null) {
        this.drawSegmentAngle(ctx, name, value, person.keypoints);
      }
    });
  };

  drawJointAngle = (ctx, angleName, angleValue, keypoints, color) => {
    const jointMappings = {
      'right_knee': ['right_hip', 'right_knee', 'right_ankle'],
      'left_knee': ['left_hip', 'left_knee', 'left_ankle'],
      'right_elbow': ['right_shoulder', 'right_elbow', 'right_wrist'],
      'left_elbow': ['left_shoulder', 'left_elbow', 'left_wrist'],
      'right_hip': ['right_knee', 'right_hip', 'neck'],
      'left_hip': ['left_knee', 'left_hip', 'neck'],
      'right_shoulder': ['right_elbow', 'right_shoulder', 'neck'],
      'left_shoulder': ['left_elbow', 'left_shoulder', 'neck']
    };

    if (!jointMappings[angleName]) return;
    
    const points = jointMappings[angleName];
    if (!points.every(p => keypoints[p] && keypoints[p].confidence > 0.3)) return;
    
    const joint = keypoints[points[1]];
    const pt1 = keypoints[points[0]];
    const pt2 = keypoints[points[2]];
    
    // Draw angle arc
    ctx.strokeStyle = '#00ff00';
    ctx.lineWidth = 2;
    
    const v1 = { x: pt1.x - joint.x, y: pt1.y - joint.y };
    const v2 = { x: pt2.x - joint.x, y: pt2.y - joint.y };
    
    const angle1 = Math.atan2(v1.y, v1.x);
    const angle2 = Math.atan2(v2.y, v2.x);
    
    ctx.beginPath();
    ctx.arc(joint.x, joint.y, 30, Math.min(angle1, angle2), Math.max(angle1, angle2));
    ctx.stroke();
    
    // Draw angle value
    const textOffset = {
      x: (v1.x + v2.x) / 2,
      y: (v1.y + v2.y) / 2
    };
    
    const length = Math.sqrt(textOffset.x * textOffset.x + textOffset.y * textOffset.y);
    if (length > 0) {
      textOffset.x = textOffset.x / length * 50;
      textOffset.y = textOffset.y / length * 50;
    }
    
    const textX = joint.x + textOffset.x;
    const textY = joint.y + textOffset.y;
    
    // Background
    ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
    ctx.fillRect(textX - 15, textY - 15, 30, 20);
    
    // Text
    ctx.fillStyle = '#00ff00';
    ctx.font = '12px Arial';
    ctx.textAlign = 'center';
    ctx.fillText(Math.round(angleValue) + '°', textX, textY);
  };

  drawSegmentAngle = (ctx, angleName, angleValue, keypoints) => {
    const segmentMappings = {
      'right_shank': ['right_knee', 'right_ankle'],
      'left_shank': ['left_knee', 'left_ankle'],
      'right_thigh': ['right_hip', 'right_knee'],
      'left_thigh': ['left_hip', 'left_knee'],
      'trunk': ['hip_center', 'neck'],
      'right_forearm': ['right_elbow', 'right_wrist'],
      'left_forearm': ['left_elbow', 'left_wrist']
    };

    if (!segmentMappings[angleName]) return;
    
    const points = segmentMappings[angleName];
    if (!points.every(p => keypoints[p] && keypoints[p].confidence > 0.3)) return;
    
    const pt1 = keypoints[points[0]];
    const pt2 = keypoints[points[1]];
    
    const midX = (pt1.x + pt2.x) / 2;
    const midY = (pt1.y + pt2.y) / 2;
    
    // Draw horizontal reference line
    ctx.strokeStyle = 'white';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(midX - 20, midY);
    ctx.lineTo(midX + 20, midY);
    ctx.stroke();
    
    // Draw angle value
    ctx.fillStyle = 'white';
    ctx.font = '12px Arial';
    ctx.textAlign = 'left';
    ctx.fillText(Math.round(angleValue) + '°', midX + 25, midY + 5);
  };

  drawFrameInfo = (ctx, result) => {
    const info = `Persons: ${result.frame_metrics.detected_persons} | Processing: ${result.processing_time_ms.toFixed(1)}ms`;
    
    ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
    ctx.fillRect(0, 0, 300, 30);
    
    ctx.fillStyle = 'white';
    ctx.font = '14px Arial';
    ctx.fillText(info, 10, 20);
  };

  render() {
    const { result, displayAngles } = this.props;
    
    return (
      <CanvasContainer>
        <Canvas ref={this.canvasRef} />
        
        {displayAngles.includes('list') && result && result.persons && (
          <InfoPanel>
            <h3 style={{ margin: '0 0 10px 0' }}>Angle Measurements</h3>
            
            {result.persons.map((person, idx) => {
              const color = this.colors[idx % this.colors.length];
              const colorStr = `rgb(${color[0]}, ${color[1]}, ${color[2]})`;
              
              return (
                <PersonSection key={person.person_id}>
                  <h4 style={{ color: colorStr, margin: '5px 0' }}>
                    Person {person.person_id}
                  </h4>
                  
                  <div style={{ marginTop: '10px' }}>
                    <strong>Joint Angles:</strong>
                    {Object.entries(person.angles.joint_angles).map(([name, value]) => (
                      value !== null && (
                        <AngleItem key={name}>
                          <AngleName>{name}:</AngleName>
                          <AngleValue color="#0f0">{value.toFixed(1)}°</AngleValue>
                          <ProgressBar>
                            <ProgressFill 
                              color="#0f0" 
                              percent={Math.min(value / 180 * 100, 100)} 
                            />
                          </ProgressBar>
                        </AngleItem>
                      )
                    ))}
                  </div>
                  
                  <div style={{ marginTop: '15px' }}>
                    <strong>Segment Angles:</strong>
                    {Object.entries(person.angles.segment_angles).map(([name, value]) => (
                      value !== null && (
                        <AngleItem key={name}>
                          <AngleName>{name}:</AngleName>
                          <AngleValue>{value.toFixed(1)}°</AngleValue>
                          <ProgressBar>
                            <ProgressFill 
                              color="#fff" 
                              percent={Math.min((value + 90) / 180 * 100, 100)} 
                            />
                          </ProgressBar>
                        </AngleItem>
                      )
                    ))}
                  </div>
                </PersonSection>
              );
            })}
          </InfoPanel>
        )}
      </CanvasContainer>
    );
  }
}

export default PoseVisualizer;