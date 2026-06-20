import requests

url = "http://localhost:8080/v1/audio/speech"
payload = {
    "model": "MediaTek-Research/BreezyVoice",
    "input": "逐家好，我是一個會說台語的助理，真高興認識你！",
    "voice": "default"
}

print(f"Sending request to {url}...")
try:
    response = requests.post(url, json=payload, timeout=600)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        output_path = "/home/pipadmin/BreezyVoice/results/speech_test.wav"
        with open(output_path, "wb") as f:
            f.write(response.content)
        print(f"SUCCESS: Audio file saved to {output_path}")
    else:
        print(f"FAILED: {response.text}")
except Exception as e:
    print(f"ERROR: {e}")
