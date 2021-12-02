import os

import cv2
import numpy
from PIL import Image
from sklearn import svm

S = 256
F = 256
K = 32

_sift = cv2.SIFT_create(F)


def _features_of(image):
    return _sift.detectAndCompute(image, None)


def _load_images(path: str):
    _images = []
    for _root, _, _files in os.walk(path):
        for _file in _files:
            if _file.split('.')[-1] in ['jpeg', 'jpg', 'png']:
                _images.append(numpy.array(Image.open(os.path.join(_root, _file)).convert('L').resize((S, S))))
    return _images


def train(cat_path: str, dog_path: str, cb_update):
    cb_update({
        'fmt': '正在读取图片……'
    })
    _cats = _load_images(cat_path)
    _dogs = _load_images(dog_path)

    _kms_trainer = cv2.BOWKMeansTrainer(K)

    _cat_keys = []
    _dog_keys = []

    cb_update({
        'fmt': '正在计算特征 %p%',
        'max': len(_cats) + len(_dogs)
    })
    for _idx, _img in enumerate(_cats):
        _kp, _ds = _features_of(_img)
        _cat_keys.append(_kp)
        _kms_trainer.add(_ds)
        cb_update({
            'cur': 1 + _idx
        })
    for _idx, _img in enumerate(_dogs):
        _kp, _ds = _features_of(_img)
        _dog_keys.append(_kp)
        _kms_trainer.add(_ds)
        cb_update({
            'cur': 1 + _idx + len(_cats)
        })

    cb_update({
        'fmt': '正在聚类……'
    })
    _kms_extract = cv2.BOWImgDescriptorExtractor(_sift, cv2.FlannBasedMatcher({'algorithm': 1, 'tree': 5}, {}))
    _kms_extract.setVocabulary(_kms_trainer.cluster())

    _train = []
    _label = []

    cb_update({
        'fmt': '正在准备训练数据 %p%',
        'max': len(_cats) + len(_dogs)
    })
    for _idx, _img in enumerate(_cats):
        _train.extend(_kms_extract.compute(_img, _cat_keys[_idx]))
        _label.append(-1)
        cb_update({
            'cur': 1 + _idx
        })
    for _idx, _img in enumerate(_dogs):
        _train.extend(_kms_extract.compute(_img, _dog_keys[_idx]))
        _label.append(+1)
        cb_update({
            'cur': 1 + _idx + len(_cats)
        })

    cb_update({
        'fmt': '正在训练 SVM……'
    })
    _svm_trainer = svm.SVC()
    _svm_trainer.fit(numpy.concatenate(_train).reshape((-1, K)).astype(numpy.float32), numpy.array(_label))

    return _kms_extract.getVocabulary(), _svm_trainer


def predict(model, picture_path: str):
    _voc, _svm = model

    _kms = cv2.BOWImgDescriptorExtractor(_sift, cv2.FlannBasedMatcher({'algorithm': 1, 'tree': 5}, {}))
    _kms.setVocabulary(_voc)

    _original = Image.open(picture_path)
    _rescaled = numpy.array(_original.convert('L').resize((S, S)))

    _features = _features_of(_rescaled)[0]
    _vectored = _kms.compute(_rescaled, _features)

    _featured = Image.fromarray(cv2.drawKeypoints(_rescaled, _features, numpy.array(_original)))

    return _original, _featured, numpy.mean(_svm.predict(_vectored))


def measure(model, cat_path: str, dog_path: str, cb_update):
    _voc, _svm = model

    _kms = cv2.BOWImgDescriptorExtractor(_sift, cv2.FlannBasedMatcher({'algorithm': 1, 'tree': 5}, {}))
    _kms.setVocabulary(_voc)

    cb_update({
        'fmt': '正在读取图片……'
    })
    _cats = _load_images(cat_path)
    _dogs = _load_images(dog_path)

    _cat_correct = 0
    _dog_correct = 0

    cb_update({
        'fmt': '正在评估 %p%',
        'max': len(_cats) + len(_dogs)
    })
    for _idx, _img in enumerate(_cats):
        if _svm.predict(_kms.compute(_img, _features_of(_img)[0])) < 0:
            _cat_correct += 1
        cb_update({
            'cur': 1 + _idx
        })
    for _idx, _img in enumerate(_dogs):
        if _svm.predict(_kms.compute(_img, _features_of(_img)[0])) > 0:
            _dog_correct += 1
        cb_update({
            'cur': 1 + _idx + len(_cats)
        })

    return _cat_correct, len(_cats), _dog_correct, len(_dogs)
