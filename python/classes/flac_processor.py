from mutagen.flac import FLAC, Picture
from PIL import Image
from pathlib import Path
import os
import uuid


class FLACImageReprocessor:
    def __init__(self, base_path, file_search_string='*.flac', progressive=False,
                 quality=100, optimize=True, replace_images=True):
        self.base_path = base_path
        self.file_search_string = file_search_string
        self.progressive = progressive
        self.quality = quality
        self.optimize=optimize
        self.failed = []
        self._created_images = []
        self.replace_images = replace_images
        self.file_count = None
        self.file_list = []

    def run(self):
        file_list = self.get_file_list()
        file_count = self.file_count
        print(f"There are {self.file_count} files to process")
        for file_num, flac_file in enumerate(file_list):
            index_ = file_num + 1
            try:
                base_path, image_in = self.generate_names(flac_file)
                image_in_path = f"{base_path}/{image_in}"
                self._created_images.append(image_in_path)
                print(f"({index_} / {file_count} - {round(index_ / file_count * 100, 2)})%) Processing: {flac_file}")
                images = self.extract_images(flac_file, image_in_path, base_path)
                self._created_images += [img['file'] for img in images]
                self._created_images.append(image_in_path)
                self.add_flac_image_set(flac_file, images)
                self.remove_temp_files(self._created_images)
                print('----------------------------------------------------------------------------------------')
            except Exception as ex:
                print(f"Error processing {flac_file}")
                print(ex)
                self.failed.append(flac_file)
                self.remove_temp_files(self._created_images)
            self._created_images = []

    def get_file_list(self):
        self.file_list = list(Path(self.base_path).rglob(self.file_search_string))
        self.file_count = len(self.file_list)
        return self.file_list

    def generate_names(self, file_path):
        file_name = file_path.name
        base_path = str(file_path).replace(file_name, '')
        extension = file_name.split('.')[-1]
        image_name = file_name.replace(f'.{extension}', '')
        image_in = f'{image_name}_in.jpg'
        return base_path, image_in

    def add_flac_image_set(self,filename, images):
        audio = FLAC(filename)
        if self.replace_images:
            audio.clear_pictures()
        for img in images:
            self.add_flac_cover(audio, img['file'], desc=img['desc'], file_type=img['type'])
            print(f'{filename} images updated')
        audio.save()

    def add_flac_cover(self, audio, albumart, desc='Album cover', file_type=3):
        image = Picture()
        image.type = file_type
        image.desc = desc
        with open(albumart, 'rb') as f:
            image.data = f.read()
        audio.add_picture(image)

    def extract_images(self, file_path, image_in, base_path):
        var = FLAC(file_path)
        pics = var.pictures
        images = []
        types_added = []
        for p in pics:
            if p.type not in types_added:
                print("found front cover")
                print(f'image type: {p.type}')
                image = self._extract_image(p, image_in)
                images.append(image)
                types_added.append(p.type)
            else:
                print(f'Type {p.type} found in list. Skipping')
        return images

    def _extract_image(self, p, image_in):
        image_out = f'{self.base_path}/{str(uuid.uuid4())}.jpg'
        with open(image_in, "wb") as f:
            f.write(p.data)
        img = Image.open(image_in)
        img.save(
            image_out, "JPEG",
            quality=self.quality,
            optimize=self.optimize,
            progressive=self.progressive)
        img.close()

        image = {
            "file": image_out,
            "type": p.type,
            "desc": p.desc
        }
        return image

    def remove_temp_files(self, images_to_remove):
        try:
            for img in images_to_remove:
                print(f"To delete: {img}")
                os.remove(img)
        except Exception:
            pass
        print("Temp files erased")