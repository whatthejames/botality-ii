import sys 
import os
sys.path.append('.')
sys.path.append('..')
from fastapi import FastAPI
from providers.tts_provider import tts, save_audio
from pydantic import BaseModel, Field
from fastapi.responses import StreamingResponse
from io import BytesIO
from typing import Literal

app = FastAPI()

class Data(BaseModel):
  voice: str = Field(None, description='String with speaker model name')
  text: str = Field(None, description='String with text that you want to hear')
  response: Literal['file', 'path'] = Field(None, description='String with value "file" or "path", changes the output format to either the path to the recorded audio or the file itself.')


@app.post("/")
async def read_root(rqdata: Data):
  status, data = await tts(rqdata.voice, rqdata.text)
  if status:
    if rqdata.response == 'file':
      bytes = BytesIO(open(data, mode='rb').read())
      os.remove(data)
      response = StreamingResponse(bytes, media_type='audio/wav')
      response.headers["Content-Disposition"] = f"inline; filename=record.wav"
      return response
    return {"data": data}
  else:
    return {"error": data}

if __name__ == "__main__":
  import uvicorn
  uvicorn.run(app, host="0.0.0.0", port=7077)
  