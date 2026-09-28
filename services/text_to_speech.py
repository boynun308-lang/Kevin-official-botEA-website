import edge_tts

# Native mapping for high quality natural voices
VOICE_MAPPING = {
    "Khmer": {"male": "km-KH-PisethNeural", "female": "km-KH-SreymomNeural"},
    "English": {"male": "en-US-ChristopherNeural", "female": "en-US-AriaNeural"},
    "Chinese": {"male": "zh-CN-YunxiNeural", "female": "zh-CN-XiaoxiaoNeural"},
    "Thai": {"male": "th-TH-NiwatNeural", "female": "th-TH-PremwadeeNeural"},
    "Vietnamese": {"male": "vi-VN-HoaiMyNeural", "female": "vi-VN-MaiNeural"},
    "Korean": {"male": "ko-KR-InJoonNeural", "female": "ko-KR-SunHiNeural"},
    "Japanese": {"male": "ja-JP-KeitaNeural", "female": "ja-JP-NanamiNeural"},
    "Indonesian": {"male": "id-ID-ArdiNeural", "female": "id-ID-GadisNeural"},
}

async def generate_tts(text: str, language: str, gender: str, output_path: str):
    voice = VOICE_MAPPING.get(language, VOICE_MAPPING["English"])[gender.lower()]
    
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)
