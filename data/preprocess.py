import os
import random
import re

import tqdm
from PIL import Image

ANN_PATH = 'annotations/xmls'
IMG_PATH = 'images'

TRAIN_CAT_PATH = 'train/cat'
TRAIN_DOG_PATH = 'train/dog'

TEST_CAT_PATH = 'test/cat'
TEST_DOG_PATH = 'test/dog'

TRAIN_RATIO = 0.8


def _preprocess_files(files: list[tuple[str, str, str]], target_path: str):
    for _img_file, _img_path, _ann_path in tqdm.tqdm(files):
        _img = Image.open(_img_path)
        with open(_ann_path, 'r') as _f:
            _ann = _f.read()

        x_min = int(re.search(r'<xmin>(\d+)</xmin>', _ann).group(1))
        x_max = int(re.search(r'<xmax>(\d+)</xmax>', _ann).group(1))
        y_min = int(re.search(r'<ymin>(\d+)</ymin>', _ann).group(1))
        y_max = int(re.search(r'<ymax>(\d+)</ymax>', _ann).group(1))
        _img.crop((x_min, y_min, x_max, y_max)).save(os.path.join(target_path, _img_file))


def preprocess():
    os.makedirs(TRAIN_CAT_PATH, exist_ok=True)
    os.makedirs(TRAIN_DOG_PATH, exist_ok=True)

    os.makedirs(TEST_CAT_PATH, exist_ok=True)
    os.makedirs(TEST_DOG_PATH, exist_ok=True)

    _cat_files = []
    _dog_files = []

    for _img_file in os.listdir(IMG_PATH):
        _img_path = os.path.join(IMG_PATH, _img_file)
        _ann_path = os.path.join(ANN_PATH, '.'.join(_img_file.split('.')[:-1]) + '.xml')

        if _img_file.split('.')[-1] in ['jpg', 'jpeg', 'png'] and os.path.isfile(_ann_path):
            if _img_file[0].isupper():
                _cat_files.append((_img_file, _img_path, _ann_path))
            else:
                _dog_files.append((_img_file, _img_path, _ann_path))
        else:
            print('Missing', _ann_path)

    random.shuffle(_cat_files)
    random.shuffle(_dog_files)

    print('Cat', len(_cat_files))
    print('Dog', len(_dog_files))

    _size = int(min(len(_cat_files), len(_dog_files)) * TRAIN_RATIO)

    _preprocess_files(_cat_files[:_size], TRAIN_CAT_PATH)
    _preprocess_files(_cat_files[_size:], TEST_CAT_PATH)
    _preprocess_files(_dog_files[:_size], TRAIN_DOG_PATH)
    _preprocess_files(_dog_files[_size:], TEST_DOG_PATH)


if __name__ == '__main__':
    preprocess()
