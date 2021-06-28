import boto3
import sys
import re

info = {}


def get_data(image):
    with open(image, 'rb') as file:
        img_test = file.read()
        bytes_test = bytearray(img_test)
    client = boto3.client('textract')
    response = client.analyze_document(Document={'Bytes': bytes_test}, FeatureTypes=['FORMS'])
    return response['Blocks']


def check_lastName(line):
    word = re.search(r"[A-Z]{3,}", line.strip())
    if (word):
        info['lastName'] = word.group()


def check_firstName(line):
    word = re.search(r"[A-Z]{2,}\s[A-Z]{3,}", line.strip())
    if (word):
        info['firstName'] = word.group()
    else:
        word = re.match(r"[A-Z]{3,}", line.strip())
        if(word):
            info['firstName'] = word.group()


def check_CIN_Number(line):
    if ('cin' not in info):
        word = re.search(r"[A-Z]{1,2}\d{4,}", line.strip())
        if (word):
            info['cin'] = word.group()


def check_Birthday(line):
    if ('birthday' not in info):
        word = re.search(r"\d{2}(.)\d{2}(.)\d{4}", line.strip())
        if (word):
            info['birthday'] = word.group()


def check_Nationality(line):
    if ('nationalite' not in info):
        word = re.search(r"Nationalité", line.strip())
        if (word):
            info['nationalite'] = re.search(r"[A-Z]{3,}", line.strip()).group()


def check_justif(line):
    if ('justificatif' not in info):
        word = re.search(r"(CARTE|CART|CAR)", line.strip())
        if (word):
            info['justificatif'] = line.strip()


def look_data(blocks):
    for block in blocks:
        if(block['BlockType'] == 'LINE'):
            # print(block['Text'])
            word = re.search(r"(ROYAUME|ROYAUM|ROYAU|ROYA)|(MAROC|MARO|MAR)|(CARTE|CART|CAR)|(IDENTITE|IDENTIT|IDENTI|IDENT|IDEN|IDE)", block['Text'].strip())
            if(word):
                check_justif(block['Text'])
                continue
            if ('firstName' not in info):
                check_firstName(block['Text'])
                continue
            if ('lastName' not in info):
                check_lastName(block['Text'])
                continue
            check_Birthday(block['Text'])
            check_CIN_Number(block['Text'])
            check_Nationality(block['Text'])


if __name__ == "__main__":
    if(len(sys.argv) > 1):
        data = get_data(sys.argv[1])
        look_data(data)
        if ('nationalite' not in info):
            info['nationalite'] = 'MAROCAINE'
        print(info)
        sys.stdout.flush()
