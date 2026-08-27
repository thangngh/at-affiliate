"""Faceless short-video engine for Accesstrade affiliate campaigns.

Pipeline: campaign -> script -> edge-tts voiceover + subtitles -> PIL slides -> moviepy MP4.
Free, no API key, no filming. Run locally (needs ffmpeg/font/network to Microsoft).
"""
import os
import io
import sys
import glob
import asyncio
import urllib.request
import numpy as np

import edge_tts
from PIL import Image, ImageDraw, ImageFont
from moviepy import ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips

W, H = 1080, 1920
FONT_CANDIDATES = [
    r"C:\Windows\Fonts\arial.ttf",
    r"C:\Windows\Fonts\segoeui.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]


def _font(size):
    for p in FONT_CANDIDATES:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def _wrap(text, font, max_w):
    lines = []
    for para in text.split("\n"):
        words = para.split(" ")
        cur = ""
        for w in words:
            test = (cur + " " + w).strip()
            if font.getlength(test) <= max_w or not cur:
                cur = test
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
    return lines


def _gradient(top, bottom):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        r = int(top[0] + (bottom[0] - top[0]) * y / H)
        g = int(top[1] + (bottom[1] - top[1]) * y / H)
        b = int(top[2] + (bottom[2] - top[2]) * y / H)
        d.line([(0, y), (W, y)], fill=(r, g, b))
    return img


def _draw_scene(title, sub, accent="#FFD54F"):
    img = _gradient((17, 24, 39), (31, 41, 55))
    d = ImageDraw.Draw(img)
    d.rectangle([80, 220, 300, 260], fill=accent)
    f_title = _font(72)
    for i, line in enumerate(_wrap(title, f_title, W - 240)):
        d.text((120, 320 + i * 90), line, font=f_title, fill="#FFFFFF")
    f_sub = _font(44)
    if sub:
        for i, line in enumerate(_wrap(sub, f_sub, W - 240)):
            d.text((120, 1100 + i * 64), line, font=f_sub, fill="#E5E7EB")
    return img


def _logo(path_url):
    try:
        req = urllib.request.Request(path_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            return Image.open(io.BytesIO(r.read())).convert("RGBA").resize((160, 160))
    except Exception:
        return None


def build_script(campaign):
    name = campaign.get("name", "")
    commission = campaign.get("commission") or "hấp dẫn"
    scenes = [
        (f"{name} có thực sự trả hoa hồng cao?", "Cùng mình xem nhé"),
        (f"Mỗi đơn thành công", f"bạn nhận đến {commission} đồng hoa hồng"),
        ("Miễn phí tham gia", "không cần bỏ vốn, link chính chủ"),
        ("Nhấn vào link của mình", "ở dưới để đăng ký ngay nhé"),
    ]
    text = ". ".join(s[0] + (". " + s[1] if s[1] else "") for s in scenes) + "."
    return scenes, text


async def _speak(text, voice, mp3_path):
    word_cues = []
    sent_cues = []
    communicate = edge_tts.Communicate(text, voice)
    with open(mp3_path, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
                start = chunk["offset"] / 10_000_000
                end = (chunk["offset"] + chunk["duration"]) / 10_000_000
                item = (chunk["text"], start, end)
                if chunk["type"] == "WordBoundary":
                    word_cues.append(item)
                else:
                    sent_cues.append(item)
    return word_cues if word_cues else sent_cues


def _subtitle_png(word_cues):
    pngs = []
    cur_words, cur_start, cur_end = [], None, None
    for w, s, e in word_cues:
        cur_words.append(w)
        if cur_start is None:
            cur_start = s
        cur_end = e
        if len(cur_words) >= 6 or w.strip().endswith((".", "!", "?", ",")):
            pngs.append((" ".join(cur_words), cur_start, cur_end))
            cur_words, cur_start, cur_end = [], None, None
    if cur_words:
        pngs.append((" ".join(cur_words), cur_start, cur_end))
    return pngs


def _render_subs(pngs):
    out = []
    f = _font(52)
    for text, start, end in pngs:
        lines = _wrap(text, f, W - 200)
        h = 64 * len(lines) + 30
        bg = Image.new("RGBA", (W, h), (0, 0, 0, 170))
        d = ImageDraw.Draw(bg)
        for i, ln in enumerate(lines):
            d.text((24, 15 + i * 64), ln, font=f, fill="#FFFFFF")
        out.append((bg, start, end))
    return out


def make_video(campaign, out_path, voice="vi-VN-HoaiMyNeural"):
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    mp3 = out_path.rsplit(".", 1)[0] + ".mp3"
    scenes, text = build_script(campaign)
    print("[video] tts start", flush=True)
    cues = None
    for attempt in range(2):
        try:
            cues = asyncio.run(asyncio.wait_for(_speak(text, voice, mp3), timeout=60))
            break
        except Exception as e:
            print("[video] tts attempt %d failed: %s" % (attempt, e), flush=True)
    if cues is None:
        raise RuntimeError("TTS failed after retries")
    print("[video] tts done cues=%d" % len(cues), flush=True)

    scene_imgs = [_draw_scene(t, s) for t, s in scenes]
    logo = _logo(campaign["logo"]) if campaign.get("logo") else None
    if logo:
        for im in scene_imgs:
            im.paste(logo, (W - 220, 80), logo)
    scene_imgs = [np.asarray(im) for im in scene_imgs]

    audio = AudioFileClip(mp3)
    dur = audio.duration
    n = len(scene_imgs)
    scene_dur = dur / n
    clips = [ImageClip(im).with_duration(scene_dur) for im in scene_imgs]
    bg = concatenate_videoclips(clips, method="chain")
    print("[video] bg built dur=%.1f" % dur, flush=True)

    subs = _render_subs(_subtitle_png(cues))
    overlay = []
    for im, s, e in subs:
        overlay.append(ImageClip(np.asarray(im)).with_start(s).with_end(e).with_position(("center", 0.72), relative=True))
    print("[video] subs=%d" % len(overlay), flush=True)

    final = CompositeVideoClip([bg] + overlay, size=(W, H)).with_audio(audio)
    print("[video] writing...", flush=True)
    final.write_videofile(out_path, codec="libx264", audio_codec="aac", fps=30, logger=None)
    final.close()
    audio.close()
    print("[video] written", flush=True)
    return out_path


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    import json
    files = sorted(glob.glob("output/links_all_*.json"))
    items = json.load(open(files[-1], encoding="utf-8")) if files else []
    for it in items[:1]:
        c = {"name": it.get("name"), "commission": "cao", "link": it.get("link"), "logo": None}
        print("making video for", c["name"])
        print(make_video(c, f"videos/{it.get('name', 'video')}.mp4"))
