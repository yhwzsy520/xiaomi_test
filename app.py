from fastapi import FastAPI
from pydantic import BaseModel
import asyncio
import random
import math

app = FastAPI()

class NumberRequest(BaseModel):
    number: int

@app.post("/sqrt")
async def calculate_sqrt(data: NumberRequest):
    number = data.number

    # 模拟延迟100ms到150ms之间
    delay = random.uniform(0.1, 0.15)
    await asyncio.sleep(delay)

    result = math.sqrt(number)
    return {"result": result}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, workers=4)
