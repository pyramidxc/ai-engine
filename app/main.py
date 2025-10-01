from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Attack Path Engine")

class InputHost(BaseModel):
    hostname: str
    open_ports: list[int] = []
    vulnerabilities: list[str] = []

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/attack-path")
def attack_path(host: InputHost):
    return {"attack_path": ["Example: check open ports 22 and 80"]}
