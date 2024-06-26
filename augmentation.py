import albumentations as A
import numpy as np

from config import TARGET_SIZE
import cv2


def random_crop(img: np.ndarray, bboxes: list, labels: list) -> tuple[np.ndarray, list]:
    """
    Функция аугментирования данных при помощи вырезания рандомных частей платы.
    Parameters
    ----------
    img: np.ndarray
        Изображение в виде массива
    bboxes: list
        Список с параметрами ограничивающих прямоугольников
    labels:
        Список с номерами идентификаторов класса дефектов

    Returns
    -------
    (np.ndarray, list)
        Кортеж из аугментированных изображения и списка ограничивающих прямоугольников
    """
    transform = A.Compose([A.RandomSizedBBoxSafeCrop(width=TARGET_SIZE, height=TARGET_SIZE, p=1)],
                          bbox_params=A.BboxParams(format='yolo', label_fields=['category_ids']), )
    transformed = transform(image=img, bboxes=bboxes, category_ids=labels)
    transformed_image = transformed['image']
    transformed_bboxes = transformed['bboxes']
    return transformed_image, transformed_bboxes


def vertical_mirroring(img, bboxes, labels):
    """
    Функция аугментирования данных при помощи вертикального отражения платы
    Parameters
    ----------
    img: np.ndarray
        Изображение в виде массива
    bboxes: list
        Список с параметрами ограничивающих прямоугольников
    labels:
        Список с номерами идентификаторов класса дефектов

    Returns
    -------
    (np.ndarray, list)
        Кортеж из аугментированных изображения и списка ограничивающих прямоугольников
    """
    transform = A.Compose([A.Resize(height=TARGET_SIZE, width=TARGET_SIZE, interpolation=cv2.INTER_AREA, p=1),
                           A.VerticalFlip(p=1), ],
                          bbox_params=A.BboxParams(format='yolo', label_fields=['category_ids']), )
    transformed = transform(image=img, bboxes=bboxes, category_ids=labels)
    transformed_image = transformed['image']
    transformed_bboxes = transformed['bboxes']
    return transformed_image, transformed_bboxes


def horizontal_mirroring(img, bboxes, labels):
    """
     Функция аугментирования данных при помощи горизонтального отражения платы
     Parameters
     ----------
     img: np.ndarray
         Изображение в виде массива
     bboxes: list
         Список с параметрами ограничивающих прямоугольников
     labels:
         Список с номерами идентификаторов класса дефектов

     Returns
     -------
     (np.ndarray, list)
         Кортеж из аугментированных изображения и списка ограничивающих прямоугольников
     """
    transform = A.Compose([A.Resize(height=TARGET_SIZE, width=TARGET_SIZE, interpolation=cv2.INTER_AREA, p=1),
                           A.HorizontalFlip(p=1), ],
                          bbox_params=A.BboxParams(format='yolo', label_fields=['category_ids']), )
    transformed = transform(image=img, bboxes=bboxes, category_ids=labels)
    transformed_image = transformed['image']
    transformed_bboxes = transformed['bboxes']
    return transformed_image, transformed_bboxes


def rotate_90(img, bboxes, labels):
    """
     Функция аугментирования данных при помощи наклона платы
     Parameters
     ----------
     img: np.ndarray
         Изображение в виде массива
     bboxes: list
         Список с параметрами ограничивающих прямоугольников
     labels:
         Список с номерами идентификаторов класса дефектов

     Returns
     -------
     (np.ndarray, list)
         Кортеж из аугментированных изображения и списка ограничивающих прямоугольников
     """
    transform = A.Compose([A.Resize(height=TARGET_SIZE, width=TARGET_SIZE, interpolation=cv2.INTER_AREA, p=1),
                           A.SafeRotate(p=1), ],
                          bbox_params=A.BboxParams(format='yolo', label_fields=['category_ids']), )
    transformed = transform(image=img, bboxes=bboxes, category_ids=labels)
    transformed_image = transformed['image']
    transformed_bboxes = transformed['bboxes']
    return transformed_image, transformed_bboxes


def augment_orig_data(img, bboxes, labels) -> tuple[tuple, tuple, tuple]:
    """
     Функция соединяющая и вызывающая все методы аугментации во время препроцессинга

     Parameters
     ----------
     img: np.ndarray
         Изображение в виде массива
     bboxes: list
         Список с параметрами ограничивающих прямоугольников
     labels:
         Список с номерами идентификаторов класса дефектов

     Returns
     -------
     (tuple, tuple, tuple)
         Кортеж из кортежей аугментированных изображения, ограничивающих прямоугольников и названий аугментаций
     """
    aug_names = ('random_crop_aug_', 'vertical_mirror_aug_', 'hoizontal_mirror_aug_', 'rotate_90_aug_')

    random_cropped_img, random_cropped_bboxes = random_crop(img, bboxes, labels)
    vertical_flipped_img, vertical_flipped_bboxes = vertical_mirroring(img, bboxes, labels)
    horizontal_flipped_img, horizontal_flipped_bboxes = horizontal_mirroring(img, bboxes, labels)
    rotated_90_img, rotated_90_bboxes = rotate_90(img, bboxes, labels)

    auged_imgs = (random_cropped_img, vertical_flipped_img, horizontal_flipped_img, rotated_90_img)
    auged_bboxes = (random_cropped_bboxes, vertical_flipped_bboxes, horizontal_flipped_bboxes, rotated_90_bboxes)

    return auged_imgs, auged_bboxes, aug_names
