#!/usr/bin/env python3

import sys
import os
import numpy as np
import logging
import argparse
import json, re
from tqdm import tqdm

from common import read_imgfile, plot_humans
from estimator2 import TfPoseEstimator as TfPoseEstimator2

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

logger = logging.getLogger('TfPoseEstimator-Video')
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

eval_size = 100


def round_int(val):
    return int(round(val))


def model_wh(resolution_str):
    width, height = map(int, resolution_str.split('x'))
    if width % 16 != 0 or height % 16 != 0:
        raise Exception('Width and height should be multiples of 16. w=%d, h=%d' % (width, height))
    return int(width), int(height)


def write_coco_json(human, image_w, image_h):
    keypoints = []
    coco_ids = [0, 15, 14, 17, 16, 5, 2, 6, 3, 7, 4, 11, 8, 12, 9, 13, 10]
    for coco_id in coco_ids:
        if coco_id not in human.body_parts.keys():
            keypoints.extend([0, 0, 0])
            continue
        body_part = human.body_parts[coco_id]
        keypoints.extend([round_int(body_part.x * image_w), round_int(body_part.y * image_h), 2])
    return keypoints


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Tensorflow Openpose Inference')
    parser.add_argument(
        '--resize',
        type=str,
        default='432x368',
        help=
        'if provided, resize images before they are processed. default=0x0, Recommends : 432x368 or 656x368 or 1312x736 '
    )
    parser.add_argument(
        '--resize-out-ratio',
        type=float,
        default=8.0,
        help='if provided, resize heatmaps before they are post-processed. default=8.0')
    parser.add_argument('--model', type=str, default='cmu', help='cmu / mobilenet_thin')
    parser.add_argument('--cocoyear', type=str, default='2017')
    parser.add_argument('--coco-dir', type=str, default='/Users/Joel/Desktop/coco2/')
    parser.add_argument('--data-idx', type=int, default=-5)
    parser.add_argument('--multi-scale', type=bool, default=True)
    parser.add_argument('--net_type', type=str, default='full_normal')
    args = parser.parse_args()

    w, h = model_wh(args.resize)

    result = []
    #path to npz model
    desktop = os.path.join(os.getenv('HOME'), 'Desktop')
    path_to_npz = os.path.join(desktop, 'Log_2108/inf_model255000.npz')
    #path to your image folder
    # base_dir = '/Users/Joel/Desktop/test/'
    base_dir = './data/media/'

    if args.net_type == 'full_normal':
        e = TfPoseEstimator2(path_to_npz, target_size=(w, h))
    imglist = os.listdir(base_dir)

    for idx, image_name in enumerate(imglist):
        img_name = os.path.join(base_dir, image_name)
        image = read_imgfile(img_name, None, None)

        # inference the image with the specified network
        humans = e.inference(image, resize_to_default=(w > 0 and h > 0), resize_out_ratio=args.resize_out_ratio)
        plot_humans(e, image, humans, '%02d' % (idx + 1))
