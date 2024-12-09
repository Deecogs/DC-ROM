from fastapi import FastAPI

app = FastAPI()

selected_motion = "elbow_flexion"

@app.get("/select_motion/{motion}")
def select_motion(motion: str):
    global selected_motion
    selected_motion = motion
    return {"selected_motion": selected_motion}
