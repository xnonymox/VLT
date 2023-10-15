# app.py
import os
import subprocess
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Handle form submission
        video = request.files["video"]
        destination_language = request.form.get("destination_language")

        if video and destination_language:
            # Save the uploaded video
            video_path = "static/input_video.mp4"
            video.save(video_path)

            # Video processing
            video_processing_command = f"spleeter separate -o . -c mp3 {video_path}"
            subprocess.call(video_processing_command, shell=True)

            # Language processing
            language = destination_language
            language_command = f"whisper_timestamped --task translate 'vocals.mp3' -o './' --model medium --language {language}"
            subprocess.call(language_command, shell=True)

            # Audio processing
            from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip

            # Load the video and audio files
            video = VideoFileClip(video_path)
            audio = AudioFileClip("vocals.mp3")

            # Combine the existing audio of the video with the new audio
            video = video.set_audio(CompositeAudioClip([video.audio, audio]))

            # Write the final video with the combined audio
            video.write_videofile("static/output_video.mp4")

            # Close the audio and video objects
            audio.close()
            video.close()

            # Delete temporary files
            files_to_delete = [video_path, "vocals.mp3"]
            for file in files_to_delete:
                try:
                    os.remove(file)
                except OSError as e:
                    print(f"Error deleting {file}: {e}")

            return redirect(url_for("index"))

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
