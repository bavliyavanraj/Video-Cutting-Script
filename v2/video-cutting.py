import os
import numpy as np
from moviepy.editor import VideoFileClip, CompositeVideoClip, ColorClip, ImageClip
from PIL import Image, ImageDraw, ImageFont

# ================= PIL FIX =================
if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.Resampling.LANCZOS
# ==========================================

# ================= STATIC CONFIG =================

INPUT_VIDEO = "anime.mp4"
OUTPUT_FOLDER = "parts"

PART_SECONDS = 10        # seconds

TOP_TEXT = "A Wild Last Boss Appeared Part" # video top text.
BOTTOM_TEXT = "Don’t miss the full video! Check it out in my Highlights." # video bottom text.

START_NUMBER = 1 # Dynamic numbers will be added at the end of the text that appears above the video.

FINAL_W, FINAL_H = 1080, 1920
TEXT_VIDEO_GAP = 10

FONT_PATH = "C:/Windows/Fonts/arial.ttf"
FONT_SIZE_TOP = 64
FONT_SIZE_BOTTOM = 58

# ================= TEXT UTILS =================

def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines = []
    line = ""
    for w in words:
        test = line + w + " "
        if draw.textbbox((0, 0), test, font=font)[2] <= max_width:
            line = test
        else:
            lines.append(line)
            line = w + " "
    lines.append(line)
    return lines

def calc_text_height(draw, lines, font, spacing):
    height = 0
    for l in lines:
        bbox = draw.textbbox((0, 0), l, font=font)
        height += (bbox[3] - bbox[1]) + spacing
    return height

def draw_text(draw, lines, font, width, padding, spacing):
    y = padding
    for l in lines:
        bbox = draw.textbbox((0, 0), l, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        draw.text(((width - w) // 2, y), l, font=font, fill="white")
        y += h + spacing

# ================= MAIN LOGIC =================

def process_video():
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    clip = VideoFileClip(INPUT_VIDEO)  # 🔹 FULL VIDEO ONLY

    font_top = ImageFont.truetype(FONT_PATH, FONT_SIZE_TOP)
    font_bottom = ImageFont.truetype(FONT_PATH, FONT_SIZE_BOTTOM)

    t = 0
    index = START_NUMBER

    while t < clip.duration:
        end_t = min(t + PART_SECONDS, clip.duration)
        part = clip.subclip(t, end_t)

        video = part.resize(width=FINAL_W)
        bg = ColorClip((FINAL_W, FINAL_H), (0, 0, 0), duration=part.duration)
        video = video.set_position("center")

        video_top = (FINAL_H - video.h) // 2
        video_bottom = video_top + video.h

        dummy = Image.new("RGBA", (FINAL_W, 10))
        draw_dummy = ImageDraw.Draw(dummy)

        # ---------- TOP TEXT ----------
        top_lines = wrap_text(
            draw_dummy,
            f"{TOP_TEXT} {index}",
            font_top,
            FINAL_W - 40
        )
        top_h = calc_text_height(draw_dummy, top_lines, font_top, 8) + 20
        img_top = Image.new("RGBA", (FINAL_W, top_h), (0, 0, 0, 0))
        draw_top = ImageDraw.Draw(img_top)
        draw_text(draw_top, top_lines, font_top, FINAL_W, 10, 8)

        top_clip = ImageClip(np.array(img_top)) \
            .set_duration(part.duration) \
            .set_position(("center", video_top - top_h - TEXT_VIDEO_GAP))

        # ---------- BOTTOM TEXT ----------
        bot_lines = wrap_text(
            draw_dummy,
            BOTTOM_TEXT,
            font_bottom,
            FINAL_W - 40
        )
        bot_h = calc_text_height(draw_dummy, bot_lines, font_bottom, 10) + 20
        img_bot = Image.new("RGBA", (FINAL_W, bot_h), (0, 0, 0, 0))
        draw_bot = ImageDraw.Draw(img_bot)
        draw_text(draw_bot, bot_lines, font_bottom, FINAL_W, 10, 10)

        bot_clip = ImageClip(np.array(img_bot)) \
            .set_duration(part.duration) \
            .set_position(("center", video_bottom + TEXT_VIDEO_GAP))

        final = CompositeVideoClip([bg, video, top_clip, bot_clip])

        output_path = os.path.join(OUTPUT_FOLDER, f"{index}.mp4")
        final.write_videofile(
            output_path,
            fps=30,
            codec="libx264",
            audio_codec="aac"
        )

        index += 1
        t += PART_SECONDS

    print("✅ VERSION-2 DONE (FULL VIDEO → MULTIPLE REELS)")

# ================= RUN =================
if __name__ == "__main__":
    process_video()
