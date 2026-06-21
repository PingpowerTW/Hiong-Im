import os
import sys
from contextlib import asynccontextmanager
from io import BytesIO

import soundfile as sf
import torch
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

# Attempt to import OmniVoice
try:
    from omnivoice.models.omnivoice import OmniVoice
except ImportError:
    print("WARNING: 'omnivoice' package is not installed. Please install it using 'pip install omnivoice'")
    OmniVoice = None


class Settings(BaseSettings):
    model_path: str = Field(
        default="MERaLiON/MERaLiON-OmniVoice-Hokkien-TTS",
        description="Specifies the model used for Hokkien speech synthesis.",
    )


class SpeechRequest(BaseModel):
    model: str = ""
    input: str = Field(
        description="The content that will be synthesized into Hokkien speech.",
        examples=["你食飽未"],
    )
    response_format: str = ""
    speed: float = 1.0


@asynccontextmanager
async def lifespan(app: FastAPI):
    if OmniVoice is None:
        raise RuntimeError("Please install omnivoice first: pip install omnivoice")
    
    app.state.settings = Settings()
    
    # Auto detect GPU or CPU
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    
    print(f"Loading Hokkien OmniVoice model '{app.state.settings.model_path}' on {device}...")
    app.state.model = OmniVoice.from_pretrained(
        app.state.settings.model_path,
        device_map=device,
        dtype=dtype,
    )
    yield
    del app.state.model


app = FastAPI(lifespan=lifespan, root_path="/v1")


@app.post("/audio/speech")
async def speech_endpoint(request: Request, payload: SpeechRequest):
    model = request.app.state.model
    print(f"Synthesizing to Hokkien: '{payload.input}'")
    
    # Generate audio: language 'nan' stands for Min Nan / Taiwanese Hokkien
    audios = model.generate(text=payload.input, language="nan")
    audio_data = audios[0]
    
    # Save the raw numpy audio array to a WAV buffer
    audio_buffer = BytesIO()
    sf.write(audio_buffer, audio_data, model.sampling_rate, format="WAV")
    audio_buffer.seek(0)
    
    return StreamingResponse(
        audio_buffer,
        media_type="audio/wav",
        headers={"Content-Disposition": "attachment; filename=output.wav"},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_omnivoice:app", host="0.0.0.0", port=8080)
