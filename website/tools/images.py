from api import app
from PIL import Image
import shutil
import os


# make a class that handles image information
class ImageHandler:
    def __init__(self, order):
        self.order = order

    # resize image function (already in memory --> don't want to read again)
    # https://stackoverflow.com/questions/65266569/how-can-i-open-an-image-of-filestorage-type-in-pillow
    def resize_and_save_image(self, file):
        img = Image.open(file)

        # resize https://stackoverflow.com/questions/273946/how-do-i-resize-an-image-using-pil-and-maintain-its-aspect-ratio
        # https://stackoverflow.com/questions/6444548/how-do-i-get-the-picture-size-with-pil
        width, height = img.size

        ratio = min(app.config['IMAGES']['MAXWIDTH'] / width,
                    app.config['IMAGES']['MAXHEIGHT'] / height)

        img.resize((int(width * ratio), int(height * ratio)), resample=0)

        # save it
        img.save(file.filename)

    # upload images function
    def upload_images(self, files):
        # only use the correct extensions (relatively cheap operations in string contruction)
        files = [
            file for file in files if f".{file.filename.split('.')[-1]}".lower() in app.config['IMAGES']['EXTENSIONS']]

        # most efficient way of making folders
        try:
            os.mkdir(self.long_directory)
        except FileNotFoundError:
            os.makedirs(self.long_directory)

        # keep a counter
        file_counter = 0
        for file in files:
            # change the image's filename (will include the directory)
            file.filename = f"{self.long_directory}/{file_counter}.{file.filename.split('.')[-1]}"

            # resize and save the image
            self.resize_and_save_image(file)

            # increment the counter
            file_counter += 1

    # make a function that deletes all the images in a directory
    def delete_images(self):
        if os.path.exists(self.long_directory):
            # delete the tree
            shutil.rmtree(self.long_directory)

    # make a function to get the order url
    def get_image_urls(self):
        # return if the directory does not exist
        if not os.path.exists(self.long_directory):
            return []

        urls = [
            {"url": f"/static/uploads/{self.short_directory}/{file}"} for file in os.listdir(self.long_directory)]

        return urls

    @property
    def short_directory(self):
        # make the directory
        return f"{self.order.user_id}/orders/{self.order.id}"

    @property
    def long_directory(self):
        return f"{app.config['UPLOAD_PATH']}/{self.short_directory}"
        return self._foo
