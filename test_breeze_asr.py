import sys
import logging
from faster_whisper import WhisperModel

logging.basicConfig(level=logging.INFO)

print("Loading model WizardForest/faster-whisper-Breeze-ASR-26-int8 on CPU...")
try:
    # Use device="cpu" and compute_type="int8" to run on CPU with low memory
    model = WhisperModel(
        "WizardForest/faster-whisper-Breeze-ASR-26-int8",
        device="cpu",
        compute_type="int8"
    )
    print("SUCCESS: Model loaded successfully!")
except Exception as e:
    print(f"FAILED to load model: {e}")
    sys.exit(1)
