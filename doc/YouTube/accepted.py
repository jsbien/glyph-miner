import os
import subprocess

frames_dir = 'frames'
accepted_dir = 'accepted-frames'

os.makedirs(accepted_dir, exist_ok=True)

for frame in os.listdir(frames_dir):
    if frame.endswith('.png'):
        path = os.path.join(frames_dir, frame)
        try:
            rating = subprocess.check_output(['getfattr', '--only-values', '-n', 'user.xdg.rating', path], text=True).strip()
            if rating and int(rating) >= 1:
                shutil.copy2(path, accepted_dir)
        except subprocess.CalledProcessError:
            pass  # No rating set
