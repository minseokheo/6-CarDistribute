import os

# Create 'video' directory
os.makedirs('video', exist_ok=True)

# Create subdirectories inside 'video'
subdirectories = ['crop_video', 'crop_video2', 'new_label', 'trackingvideo']
for subdirectory in subdirectories:
    os.makedirs(os.path.join('video', subdirectory), exist_ok=True)

print("Directories created successfully.")