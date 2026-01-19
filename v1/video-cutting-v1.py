import os
from moviepy.video.io.VideoFileClip import VideoFileClip

# =========================
# SETTINGS
# =========================
input_video = "anime.mp4"   # path of video
part_duration = 20         # seconds
output_folder = "video_parts"
# =========================

os.makedirs(output_folder, exist_ok=True)

video = VideoFileClip(input_video)
video_duration = int(video.duration)

part_number = 1

for start in range(0, video_duration, part_duration):
    end = min(start + part_duration, video_duration)

    part = video.subclipped(start, end)

    output_path = os.path.join(output_folder, f"{part_number}.mp4")

    part.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac"
    )

    print(f"✅ Part {part_number} created")
    part_number += 1

video.close()
print("🎉 All video parts successfully created!")
