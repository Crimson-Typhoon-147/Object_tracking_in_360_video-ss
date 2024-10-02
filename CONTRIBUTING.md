First of all, thank you for your interest in contributing! We're excited to have you help improve this project. 

Below are some guidelines to follow when contributing.
GUIDELINES:- 

1. **Creativity Allowed**: Feel free to submit pull requests that break the rules—we might just merge them anyway!

2. **No Build Steps**: Avoid adding build steps like `npm install` to maintain simplicity as a static site.

3. **Preserve Existing Content**: Do not remove existing content. Instead, focus on adding new content or improving what's already there.

4. **Code Style**: Your code can be neat, messy, simple, or complex. As long as it works, it's welcome!

5. **Add Your Name**: Remember to add your name to the `contributorsList` file when submitting your pull request.

6. **Keep it Small**: Aim for small pull requests to minimize merge conflicts and streamline the review process.


GETTING STARTED

This repository contains a Python script for real-time object tracking using YOLOv8 and OpenCV. It allows you to select an object in a video frame, track it, and display its coordinates in real-time.

Requirements
numpy==1.24.3
opencv_python==4.8.1.78
ultralytics
Installation
Clone this repository to your local machine:

STEPS TO FOLLOW:-

git clone https://github.com/MAVERICK-VF142/Object_tracking_in_360_video.git
Install the required dependencies:

pip install -r requirements.txt
Download the YOLOv9 model weights (yolov9e.pt) and place them in the root directory of this repository.

Usage
Run the script object_tracking.py:

python object_tracking.py
Select an object in the video frame by clicking on it. The script will track the selected object and display its coordinates in real-time.

Press 'q' to quit the application.

Contributing
Contributions are welcome! Here's how you can contribute:

Fork the repository to your GitHub account.

Clone the forked repository to your local machine:

git clone https://github.com/your-username/Object_tracking_in_360_video.git
Create a new branch for your feature or bug fix:

git checkout -b feature-name
Replace feature-name with a descriptive name for your feature or bug fix.

Make your changes and commit them:

git add .
git commit -m "Description of your changes"
Push your changes to your forked repository:

git push origin feature-name
Create a pull request from your forked repository to the main repository's master branch.

Note: Please ensure your pull request adheres to the repository's contribution guidelines.

Thank you for contributing to this project!

License
This project is licensed under the MIT License - see the LICENSE file for details.
