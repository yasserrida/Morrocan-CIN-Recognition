from scipy.ndimage import interpolation as inter
import cv2
import pytesseract
import re
import sys
import numpy as np

info = {}


def find_score(arr, angle):
    data = inter.rotate(arr, angle, reshape=False, order=0)
    hist = np.sum(data, axis=1)
    score = np.sum((hist[1:] - hist[:-1]) ** 2)
    return hist, score


def fix_skew(image):
    angles = np.arange(-5, 6, 1)
    scores = []
    for angle in angles:
        hist, score = find_score(image, angle)
        scores.append(score)
    best_score = max(scores)
    best_angle = angles[scores.index(best_score)]
    image = inter.rotate(image, best_angle, reshape=False, order=0)
    return image


def preprocessing(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    kernel = np.ones((1, 1), np.uint8)
    image = cv2.dilate(image, kernel, iterations=1)
    image = cv2.erode(image, kernel, iterations=1)
    image = cv2.GaussianBlur(image, (5, 5), 0)
    image = cv2.medianBlur(image, 5)
    image = cv2.adaptiveThreshold(image.astype(
        np.uint8), 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
    image = fix_skew(image)
    return image


def get_data(image):
    return pytesseract.image_to_string(image, lang='eng', config=r'--oem 3 --psm 6')


def recognition(lines):
    for i in range(2, len(lines)):
        word = re.search(
            r"(D')|(CARTE|CART|CAR)|(IDENTITE|IDENTIT|IDENTI|IDENT|IDEN|IDE)|(NATIONAL|NATIONA|NATION|NATIO|NATI|NAT)", lines[i].strip())
        if(word):
            continue
        if('firstName' not in info):
            word = re.search(r"[A-Z]{3,}", lines[i].strip())
            if word:
                info['firstName'] = word.group()
                continue
        else:
            if('lastName' not in info):
                word = re.search(r"[A-Z]{3,}", lines[i].strip())
                if word == None:
                    word = re.match(
                        r"[A-Z]{2,}\s[A-Z]{3,}", lines[i].strip())
                    if word:
                        info['lastName'] = word.group()
                        continue
                else:
                    info['lastName'] = word.group()
                    continue
        if('birthday' not in info):
            word = re.search(r"\d{2}(.)\d{2}(.)\d{4}", lines[i].strip())
            if word:
                info['birthday'] = word.group()
                continue
        if('cin' not in info):
            word = re.search(r"[A-Z]{1,2}\d{4,}", lines[i].strip())
            if word:
                info["cin"] = word.group()
                continue


def recognition_cin_birthday(lines):
    for i in range(len(lines)):
        if('birthday' not in info):
            word = re.search(r"\d{2}(.)\d{2}(.)\d{4}", lines[i].strip())
            if word:
                info['birthday'] = word.group()
                continue
        if('cin' not in info):
            word = re.search(r"[a-zA-Z]{1,2}\d{4,}", lines[i].strip())
            if word:
                info['cin'] = word.group()
                continue


def recognition_last_first_name(lines):
    for i in range(2, len(lines)):
        word = re.search(
            r"(D')|(CARTE|CART|CAR)|(IDENTITE|IDENTIT|IDENTI|IDENT|IDEN|IDE)|(NATIONAL|NATIONA|NATION|NATIO|NATI|NAT)", lines[i].strip())
        if word:
            continue
        if('firstName' not in info):
            word = re.search(r"[A-Za-z]{3,}", lines[i].strip())
            if word:
                info['firstName'] = word.group()
                continue
        else:
            if('lastName' not in info):
                word = re.search(r"[A-Za-z]{3,}", lines[i].strip())
                if word == None:
                    word = re.match(
                        r"[A-Za-z]{2,}\s[A-Za-z]{3,}", lines[i].strip())
                    if word:
                        info['lastName'] = word.group()
                        continue
                else:
                    info['lastName'] = word.group()
                    continue


if __name__ == '__main__':
    if(len(sys.argv) > 1):
        path = sys.argv[1]
        input = cv2.imread(path)
        
        # ------------------ first recognition
        data = get_data(image=cv2.cvtColor(input, cv2.COLOR_BGR2GRAY))
        recognition(lines=data.split('\n'))
        # print(data)
        
        # ------------------ if not cin || birthday
        if('cin' not in info or 'birthday' not in info):
            data = get_data(image=preprocessing(input))
            recognition_cin_birthday(lines=data.split('\n'))
            # print(data)
            
        # ------------------ if not firstName || lastName
        if('firstName' not in info or 'lastName' not in info):
            data = get_data(image=preprocessing(input))
            recognition(lines=data.split('\n'))
        if('firstName' not in info or 'lastName' not in info):
            data = get_data(image=preprocessing(input))
            recognition_last_first_name()(lines=data.split('\n'))
        print(info)
        sys.stdout.flush()
