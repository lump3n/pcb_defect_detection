import xml.etree.ElementTree as ET
from os import listdir
import random

import torch
from torch.utils.data import Dataset
from PIL import Image
import numpy as np
import cv2


class RCnnDataset(Dataset):
    def __init__(self,  image_paths, anno_paths):
        self.image_paths = image_paths
        self.anno_paths = anno_paths

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, index):
        image_path = self.image_paths[index]
        anno_path = self.anno_paths[index]

        image = self._load_image(image_path)
        image = torch.tensor(image)/255

        bndboxs, labels = take_anno_params(anno_path)
        labels = torch.tensor(labels)

        bndboxs = torch.tensor(bndboxs,  dtype=torch.float32)
        areas = torch.tensor([(bndbox[3] - bndbox[1]) * (bndbox[2] - bndbox[0]) for bndbox in bndboxs],  dtype=torch.float32)

        target = {'boxes': bndboxs,
                  'labels': labels,
                  'image_id': torch.tensor([index]),
                  'areas': areas,
                  'iscrowd': torch.zeros(6, dtype=torch.int64)}
        return image, target

    def _load_image(self, img_path: int):
        image = cv2.imread(img_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return image


def divide_train_val(img_dir: str, anno_dir: str, subdirs: list, train_size: float = 0.8) -> tuple:
    """
    Функция разделения на тренировочную и валидационную выборки для изображений и анотаций
    Parameters
    ----------
    img_dir:
        Путь до папки с оригинальными изображениями
    anno_dir:
        Путь до папки с оригинальными аннотациями
    subdirs:
        Имена подпапок, соответствуют классам изображений
    train_size:
        Относительный размер тренировочной выборки, например 0.8 означает,
        что тренировочная выборка будет составлять 80% данных от оригинальной

    Returns
    -------
    tuple
        Возвращает кортеж списков, которые содержат пути до оригинальных изображений и аннотаций, разделенные на tarin/val
    """
    img_train_paths, img_val_paths, = [], []
    anno_train_paths, anno_val_paths, = [], []
    img_test_paths, anno_test_paths = [], []
    for subdir in subdirs:
        img_dir_path = img_dir + subdir
        anno_dir_path = anno_dir + subdir

        img_paths = [img_dir_path + f for f in listdir(img_dir_path)]
        anno_paths = [anno_dir_path + f for f in listdir(anno_dir_path)]

        number_of_train = int(len(img_paths) * train_size)
        for _ in range(number_of_train):
            random_idx = random.randint(0, len(img_paths) - 1)

            img_train_path = img_paths.pop(random_idx)
            anno_train_path = anno_paths.pop(random_idx)

            img_train_paths.append(img_train_path)
            anno_train_paths.append(anno_train_path)

        img_val_paths.extend(img_paths)
        anno_val_paths.extend(anno_paths)

        img_test_paths.extend(img_val_paths[:5])
        anno_test_paths.extend(anno_val_paths[:5])

    return img_train_paths, img_val_paths, img_test_paths, anno_train_paths, anno_val_paths, anno_test_paths


def take_anno_params(xml_path: str) -> tuple:
    """
    Функция для парсинга ключевых параметров аннотиции:
    лэйбла изображения, координат окружающего треугольника и размера изображения
    Parameters
    ----------
    xml_path:
        Путь до аннотации
    Returns
    -------
    tuple
        Кортеж содержащий лэйбл изображения, кортеж координат окружающего треугольника и  кортеж размеров изображения
    """
    lbls = {'spurious_copper': 0,
            'mouse_bite': 1,
            'open_circuit': 2,
            'missing_hole': 3,
            'spur': 4,
            'short': 5}

    tree = ET.parse(xml_path)
    root = tree.getroot()

    labels = []
    bndboxs = []
    for obj in root.iter('object'):
        label = lbls[obj.find('name').text]
        labels.append(label)
        for box in obj.iter('bndbox'):
            xmin = int(box.find('xmin').text)
            ymin = int(box.find('ymin').text)
            xmax = int(box.find('xmax').text)
            ymax = int(box.find('ymax').text)
            bndboxs.append((xmin, ymin, xmax, ymax))
    return bndboxs, labels