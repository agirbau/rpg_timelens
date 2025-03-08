"""Class for reading / writing image sequences."""

import os

import numpy as np
from PIL import Image

import cv2
from timelens.common import os_tools
from timelens.common import iterator_modifiers
import tqdm

from concurrent.futures import ThreadPoolExecutor, as_completed


class ImageJITReader(object):
    """Reads Image Just-in-Time"""
    def __init__(self, filenames):
        self.filenames = filenames

    def __len__(self):
        return len(self.filenames)

    def __getitem__(self, index):
        f = self.filenames[index]
        img = Image.open(f).convert("RGB")
        return img



class ImageSequence(object):
    """Class that provides access to image sequences."""

    def __init__(self, images, timestamps):
        self._images = images
        self._timestamps = timestamps
        self._width, self._height = self[0].size

    def __len__(self):
        return len(self._images)

    def skip_and_repeat(self, number_of_skips, number_of_frames_to_insert):
        images = list(iterator_modifiers.make_skip_and_repeat_iterator(
            iter(self._images), number_of_skips, number_of_frames_to_insert))
        timestamps = list(iterator_modifiers.make_skip_and_repeat_iterator(
            iter(self._timestamps), number_of_skips, number_of_frames_to_insert))
        return ImageSequence(images, timestamps)

    def make_frame_iterator(self, number_of_skips):
        return iter(self._images)

    @staticmethod
    def save_image(image, filename):
        """Helper function to save a single image with full permissions."""
        image.save(filename)
        os.chmod(filename, 0o777)  # Set full permissions (chmod 777)

    def to_folder(self, folder, file_template="{:06d}.png", timestamps_file="timestamp.txt", max_workers=8):
        """Save images to image files concurrently with a visible progress bar."""
        folder = os.path.abspath(folder)
        os.makedirs(folder, exist_ok=True)  # Ensure the folder exists
        os.chmod(folder, 0o777)  # Set full permissions for the output folder

        # Use ThreadPoolExecutor for concurrent writing
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self.save_image, image, os.path.join(folder, file_template.format(image_index))): image_index for image_index, image in enumerate(self._images)}

            # Use tqdm inside the main thread
            with tqdm.tqdm(total=len(self._images), desc="Saving Images", unit="img") as pbar:
                for future in as_completed(futures):
                    future.result()  # Ensure any exceptions are raised
                    pbar.update(1)  # Update the progress bar

        # Save timestamps after images are written
        os_tools.list_to_file(
            os.path.join(folder, timestamps_file),
            [str(timestamp) for timestamp in self._timestamps]
        )
        os.chmod(os.path.join(folder, timestamps_file), 0o777)  # Set full permissions for timestamps file

    def to_folder_old(self, folder, file_template="{:06d}.png", timestamps_file="timestamp.txt"):
        """Save images to image files"""
        folder = os.path.abspath(folder)
        for image_index, image in enumerate(self._images):
            #print(image_index)
            filename = os.path.join(folder, "{:06d}.png".format(image_index))
            image.save(filename)
        os_tools.list_to_file(
        os.path.join(folder, "timestamp.txt"), [str(timestamp) for timestamp in self._timestamps])

    def to_video(self, filename):
        """Saves to video."""
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        video = cv2.VideoWriter(filename, fourcc, 30.0, (self._width, self._height))
        for image in self._images:
            video.write(cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR))
        video.release()

    def __getitem__(self, index):
        """Return example by its index."""
        if index >= len(self):
            raise IndexError
        return self._images[index]

    @classmethod
    def from_folder(
        cls, folder, image_file_template="frame_{:010d}.png", timestamps_file="timestamps.txt"
    ):
        filename_iterator = os_tools.make_glob_filename_iterator(
            os.path.join(folder, image_file_template)
        )
        filenames = [f for f in filename_iterator]

        images = ImageJITReader(filenames)
        timestamps = np.loadtxt(os.path.join(folder, timestamps_file)).tolist()

        return cls(images, timestamps)

    @classmethod
    def from_video(cls, filename, fps):
        images = []
        capture = cv2.VideoCapture(filename)
        while capture.isOpened():
            success, frame = capture.read()
            if not success:
                break
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            images.append(Image.fromarray(frame))
        capture.release()
        timestamps = [float(index) / float(fps) for index in range(len(images))]
        return cls(images, timestamps)
