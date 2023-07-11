from defuction import images_to_video

input_folder = r".\image"
output_video = r".\video.mp4"

images_to_video(input_folder, output_video, duration=3, fps=30)