// Sports2D style drawing functions for React
// Matches the Python visualization exactly

const COLORS = ['#FF0000', '#0000FF', '#FFFF00', '#FF00FF', '#00FFFF', '#000000', '#FFFFFF'];

const SKELETON_CONNECTIONS = [
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
  
  // Center connections
  ['neck', 'hip_center']
];

export function drawSports2DVisualization(ctx, poseData, displayOptions) {
  if (!poseData || !poseData.persons) return;

  poseData.persons.forEach((person, idx) => {
    const color = COLORS[idx % COLORS.length];
    
    // Draw skeleton
    if (displayOptions.showSkeleton) {
      drawSkeleton(ctx, person.keypoints, color);
    }
    
    // Draw keypoints
    if (displayOptions.showKeypoints) {
      drawKeypoints(ctx, person.keypoints);
    }
    
    // Draw bounding box
    if (displayOptions.showBoundingBox) {
      drawBoundingBox(ctx, person.keypoints, person.person_id, color);
    }
    
    // Draw angles on body
    if (displayOptions.showAnglesOnBody) {
      drawAnglesOnBody(ctx, person, color);
    }
  });
}

function drawSkeleton(ctx, keypoints, color) {
  ctx.strokeStyle = color;
  ctx.lineWidth = 2;
  
  SKELETON_CONNECTIONS.forEach(([start, end]) => {
    if (keypoints[start] && keypoints[end]) {
      const startKp = keypoints[start];
      const endKp = keypoints[end];
      
      if (startKp.confidence > 0.3 && endKp.confidence > 0.3) {
        ctx.beginPath();
        ctx.moveTo(startKp.x, startKp.y);
        ctx.lineTo(endKp.x, endKp.y);
        ctx.stroke();
      }
    }
  });
}

function drawKeypoints(ctx, keypoints) {
  Object.values(keypoints).forEach(kp => {
    if (kp.confidence > 0.3) {
      // Color based on confidence (red to green)
      const hue = kp.confidence * 120; // 0 (red) to 120 (green)
      ctx.fillStyle = `hsl(${hue}, 100%, 50%)`;
      
      ctx.beginPath();
      ctx.arc(kp.x, kp.y, 5, 0, 2 * Math.PI);
      ctx.fill();
      
      // White border
      ctx.strokeStyle = 'white';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.arc(kp.x, kp.y, 6, 0, 2 * Math.PI);
      ctx.stroke();
    }
  });
}

function drawBoundingBox(ctx, keypoints, personId, color) {
  const validPoints = Object.values(keypoints).filter(kp => kp.confidence > 0.3);
  if (validPoints.length === 0) return;
  
  const xs = validPoints.map(kp => kp.x);
  const ys = validPoints.map(kp => kp.y);
  
  const minX = Math.min(...xs) - 20;
  const minY = Math.min(...ys) - 20;
  const maxX = Math.max(...xs) + 20;
  const maxY = Math.max(...ys) + 20;
  
  // Draw box
  ctx.strokeStyle = color;
  ctx.lineWidth = 2;
  ctx.strokeRect(minX, minY, maxX - minX, maxY - minY);
  
  // Draw person ID label
  ctx.fillStyle = color;
  ctx.fillRect(minX, minY - 25, 80, 25);
  
  ctx.fillStyle = 'white';
  ctx.font = 'bold 14px Arial';
  ctx.fillText(`Person ${personId}`, minX + 5, minY - 8);
}

function drawAnglesOnBody(ctx, person, color) {
  const keypoints = person.keypoints;
  
  // Draw joint angles
  drawJointAngles(ctx, person.angles.joint_angles, keypoints, color);
  
  // Draw segment angles
  drawSegmentAngles(ctx, person.angles.segment_angles, keypoints);
}

function drawJointAngles(ctx, jointAngles, keypoints, color) {
  const jointMappings = {
    'right_ankle': ['right_knee', 'right_ankle', 'right_foot_index'],
    'left_ankle': ['left_knee', 'left_ankle', 'left_foot_index'],
    'right_knee': ['right_hip', 'right_knee', 'right_ankle'],
    'left_knee': ['left_hip', 'left_knee', 'left_ankle'],
    'right_hip': ['right_knee', 'right_hip', 'neck'],
    'left_hip': ['left_knee', 'left_hip', 'neck'],
    'right_shoulder': ['right_elbow', 'right_shoulder', 'neck'],
    'left_shoulder': ['left_elbow', 'left_shoulder', 'neck'],
    'right_elbow': ['right_shoulder', 'right_elbow', 'right_wrist'],
    'left_elbow': ['left_shoulder', 'left_elbow', 'left_wrist']
  };
  
  Object.entries(jointAngles).forEach(([angleName, angleValue]) => {
    if (angleValue === null) return;
    
    const points = jointMappings[angleName];
    if (!points) return;
    
    const [p1Name, p2Name, p3Name] = points;
    if (!keypoints[p1Name] || !keypoints[p2Name] || !keypoints[p3Name]) return;
    
    const p1 = keypoints[p1Name];
    const p2 = keypoints[p2Name]; // Joint point
    const p3 = keypoints[p3Name];
    
    if (p1.confidence < 0.3 || p2.confidence < 0.3 || p3.confidence < 0.3) return;
    
    // Draw angle arc
    const radius = 40;
    const v1 = { x: p1.x - p2.x, y: p1.y - p2.y };
    const v2 = { x: p3.x - p2.x, y: p3.y - p2.y };
    
    const angle1 = Math.atan2(v1.y, v1.x) * 180 / Math.PI;
    const angle2 = Math.atan2(v2.y, v2.x) * 180 / Math.PI;
    
    ctx.strokeStyle = '#00FF00';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(p2.x, p2.y, radius, 
            Math.min(angle1, angle2) * Math.PI / 180, 
            Math.max(angle1, angle2) * Math.PI / 180);
    ctx.stroke();
    
    // Draw angle value
    const textOffset = {
      x: (v1.x + v2.x) / 2,
      y: (v1.y + v2.y) / 2
    };
    const length = Math.sqrt(textOffset.x * textOffset.x + textOffset.y * textOffset.y);
    if (length > 0) {
      textOffset.x = textOffset.x / length * (radius + 20);
      textOffset.y = textOffset.y / length * (radius + 20);
    }
    
    const textX = p2.x + textOffset.x;
    const textY = p2.y + textOffset.y;
    
    // Background for text
    ctx.fillStyle = 'black';
    ctx.fillRect(textX - 15, textY - 12, 30, 16);
    
    // Draw text
    ctx.fillStyle = '#00FF00';
    ctx.font = '12px Arial';
    ctx.textAlign = 'center';
    ctx.fillText(Math.round(angleValue) + '°', textX, textY);
  });
}

function drawSegmentAngles(ctx, segmentAngles, keypoints) {
  const segmentMappings = {
    'right_foot': ['right_foot_index', 'right_heel'],
    'left_foot': ['left_foot_index', 'left_heel'],
    'right_shank': ['right_knee', 'right_ankle'],
    'left_shank': ['left_knee', 'left_ankle'],
    'right_thigh': ['right_hip', 'right_knee'],
    'left_thigh': ['left_hip', 'left_knee'],
    'trunk': ['hip_center', 'neck'],
    'right_arm': ['right_shoulder', 'right_elbow'],
    'left_arm': ['left_shoulder', 'left_elbow'],
    'right_forearm': ['right_elbow', 'right_wrist'],
    'left_forearm': ['left_elbow', 'left_wrist']
  };
  
  Object.entries(segmentAngles).forEach(([angleName, angleValue]) => {
    if (angleValue === null) return;
    
    const points = segmentMappings[angleName];
    if (!points) return;
    
    const [p1Name, p2Name] = points;
    if (!keypoints[p1Name] || !keypoints[p2Name]) return;
    
    const p1 = keypoints[p1Name];
    const p2 = keypoints[p2Name];
    
    if (p1.confidence < 0.3 || p2.confidence < 0.3) return;
    
    // Calculate midpoint
    const midX = (p1.x + p2.x) / 2;
    const midY = (p1.y + p2.y) / 2;
    
    // Draw horizontal reference line
    ctx.strokeStyle = 'white';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(midX - 20, midY);
    ctx.lineTo(midX + 20, midY);
    ctx.stroke();
    
    // Draw segment direction line
    const dx = p1.x - p2.x;
    const dy = p1.y - p2.y;
    const length = Math.sqrt(dx * dx + dy * dy);
    if (length > 0) {
      const dirX = dx / length * 20;
      const dirY = dy / length * 20;
      
      ctx.strokeStyle = 'white';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(midX, midY);
      ctx.lineTo(midX + dirX, midY + dirY);
      ctx.stroke();
    }
    
    // Draw angle value
    ctx.fillStyle = 'white';
    ctx.font = '12px Arial';
    ctx.textAlign = 'left';
    ctx.fillText(Math.round(angleValue) + '°', midX + 25, midY + 5);
  });
}