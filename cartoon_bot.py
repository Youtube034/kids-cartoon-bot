import os, io, json, random, asyncio, requests, textwrap, urllib.parse
import edge_tts
from PIL import Image, ImageDraw, ImageFont
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

from moviepy.editor import (
    AudioFileClip, ImageClip, CompositeAudioClip, concatenate_videoclips, afx
)

# 1. AI se Nayi Kids Hindi Cartoon Story Generate Karna
def generate_kids_story():
    themes = [
        "a clever little rabbit who outsmarts a greedy lion in a magical jungle",
        "a cute baby elephant who learns the power of kindness and helping friends",
        "a magical golden bird and a poor honest woodcutter",
        "two best friend monkeys who find a mysterious glowing mango tree",
        "a brave little tortoise who saves his jungle friends using wisdom"
    ]
    chosen_theme = random.choice(themes)
    
    prompt = f"""You are a popular Hindi Kids Cartoon Storyteller (like Panchatantra / Moral Stories).
Write a fun, exciting 35-second Hindi Moral Story for kids about: {chosen_theme}.
Return ONLY valid JSON in this exact format:
{{
  "title": "जादुई जंगल की कहानी 🐰🦁 | Hindi Kahani | Cartoon Moral Story #shorts #kahani",
  "description": "Bacchon ki manpasand moral story aur cartoon kahani! 🌈✨\\n#hindikahaniya #moralstories #cartoon #kidsstory #shorts",
  "scenes": [
    {{
      "tts_hindi": "एक सुंदर से जादुई जंगल में, चीकू नाम का एक बहुत ही नटखट और समझदार खरगोश रहता था।",
      "caption": "Ek sundar jaadui jungle mein,\\nChiku naam ka samajhdar khargosh rehta tha!",
      "image_prompt": "3D Pixar Disney style cute cartoon baby rabbit smiling in a vibrant colorful magical forest, bright sunny lighting, kids animation 8k, vertical 9:16"
    }},
    {{
      "tts_hindi": "एक दिन जंगल में एक लालची शेर आया, और कहने लगा कि आज से सारे मीठे फल सिर्फ मेरे हैं!",
      "caption": "Ek din wahan ek laalchi sher aaya,\\nAur saare meethe phal chura liye!",
      "image_prompt": "3D Pixar Disney style funny greedy cartoon lion roaring near a basket of glowing fruits in a colorful jungle, kids animation, vertical 9:16"
    }},
    {{
      "tts_hindi": "तभी नन्हे चीकू ने दिमाग लगाया, और शेर को नदी के पानी में उसकी ही परछाई दिखा कर डरा दिया!",
      "caption": "Tabhi Chiku ne dimaag lagaya,\\nAur sher ko paani mein parchaayi dikha kar bhaga diya!",
      "image_prompt": "3D Pixar Disney style cute cartoon rabbit pointing at a sparkling river while a funny cartoon lion looks shocked, vibrant colors, vertical 9:16"
    }},
    {{
      "tts_hindi": "शेर डर कर भाग गया और सारे जानवर खुशी से नाचने लगे! सीख, अक्लमंदी हमेशा ताकत से बड़ी होती है।",
      "caption": "Seekh: Aklmandi hamesha taakat se badi hoti hai! 🌟\\nVideo pasand aayi toh Like aur Subscribe karein!",
      "image_prompt": "3D Pixar Disney style happy cute jungle animals rabbit elephant monkey celebrating together with sparkles, colorful kids animation, vertical 9:16"
    }}
  ]
}}"""
    try:
        res = requests.post(
            "https://text.pollinations.ai/",
            json={"messages": [{"role": "user", "content": prompt}], "model": "openai", "jsonMode": True},
            timeout=25
        )
        raw = res.text.replace("```json", "").replace("```", "").strip()
        return json.loads(raw[raw.find("{"):raw.rfind("}")+1])
    except Exception:
        return json.loads(prompt[prompt.find("{"):prompt.rfind("}")+1])

# 2. 3D Cartoon Image Download + Kids Comic Subtitle Box
def create_cartoon_frame(prompt_text, caption, scene_idx, out_path):
    img = None
    encoded = urllib.parse.quote(prompt_text)
    for attempt in range(3):
        try:
            url = f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1920&nologo=true&seed={random.randint(1, 9999)}"
            r = requests.get(url, timeout=25)
            temp_img = Image.open(io.BytesIO(r.content)).convert("RGB")
            img = temp_img.resize((1080, 1920))
            break
        except Exception:
            pass

    # Fallback colorful cartoon backdrop if API is busy
    if img is None:
        colors = [(45, 140, 255), (255, 130, 60), (90, 190, 80), (160, 90, 240)]
        img = Image.new("RGB", (1080, 1920), colors[scene_idx % len(colors)])

    img = img.convert("RGBA")
    # Bottom dark rounded bar for kids' subtitles so text is 100% clear and never cut
    overlay = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)
    ov_draw.rounded_rectangle([60, 1360, 1020, 1740], radius=35, fill=(15, 20, 40, 210), outline=(255, 215, 0, 255), width=5)
    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
    except Exception:
        font = ImageFont.load_default()

    wrapped = []
    for line in caption.split("\n"):
        wrapped.extend(textwrap.wrap(line, width=28))

    y = 1440
    for line in wrapped[:4]:
        draw.text((543, y+3), line, font=font, fill=(0, 0, 0, 255), anchor="mm")
        draw.text((540, y), line, font=font, fill=(255, 240, 100, 255), anchor="mm")
        y += 60

    img.convert("RGB").save(out_path, quality=95)

# 3. Expressive Kids Storyteller Voice (Swara Didi Voice - Cheerful & Clear)
async def make_story_voice(text, out_mp3):
    communicate = edge_tts.Communicate(text, voice="hi-IN-SwaraNeural", rate="+4%", pitch="+6Hz")
    await communicate.save(out_mp3)

# 4. YouTube Direct Auto-Upload (No human touch!)
def upload_to_youtube(video_path, title, description):
    client_id = os.getenv("YT_CLIENT_ID")
    client_secret = os.getenv("YT_CLIENT_SECRET")
    refresh_token = os.getenv("YT_REFRESH_TOKEN")

    if not (client_id and client_secret and refresh_token):
        print("⚠️ YouTube Secrets abhi add nahi hain. Video GitHub Artifacts mein save ho gayi hai!")
        return

    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    creds = Credentials(
        None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret
    )
    youtube = build("youtube", "v3", credentials=creds)

    body = {
        "snippet": {
            "title": title[:95],
            "description": description,
            "tags": ["hindikahaniya", "cartoon", "moralstories", "kidsstory", "kahani", "shorts"],
            "categoryId": "24"
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": True
        }
    }
    media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
    req = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    res = req.execute()
    print(f"🎉 AUTO-UPLOADED TO YOUTUBE! Video ID: https://youtu.be/{res['id']}")

async def main():
    os.makedirs("output", exist_ok=True)
    print("🦄 Writing New Kids Hindi Cartoon Story...")
    story = generate_kids_story()
    clips = []

    for i, sc in enumerate(story["scenes"]):
        print(f"🎨 Building Cartoon Scene {i+1}...")
        v_path = f"output/v_{i}.mp3"
        await make_story_voice(sc["tts_hindi"], v_path)
        a_clip = AudioFileClip(v_path)
        dur = a_clip.duration + 0.4

        img_path = f"output/img_{i}.jpg"
        create_cartoon_frame(sc["image_prompt"], sc["caption"], i, img_path)

        clip = (
            ImageClip(img_path)
            .set_duration(dur)
            .resize(lambda t: 1 + 0.02 * t)
            .set_position(("center", "center"))
            .set_audio(a_clip)
        )
        clips.append(clip)

    final_video = concatenate_videoclips(clips, method="compose")

    # Happy Kids Background Music
    try:
        bgm_url = "https://cdn.pixabay.com/download/audio/2022/03/15/audio_c8c8a73467.mp3"
        r = requests.get(bgm_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        with open("output/bgm.mp3", "wb") as f:
            f.write(r.content)
        bgm = AudioFileClip("output/bgm.mp3").fx(afx.audio_loop, duration=final_video.duration).volumex(0.14)
        final_video = final_video.set_audio(CompositeAudioClip([final_video.audio, bgm]))
    except Exception:
        pass

    out_mp4 = "output/kids_cartoon_short.mp4"
    final_video.write_videofile(out_mp4, fps=24, codec="libx264", audio_codec="aac")
    print(f"✅ Cartoon Video Ready: {out_mp4}")
    upload_to_youtube(out_mp4, story["title"], story["description"])

if __name__ == "__main__":
    asyncio.run(main())
