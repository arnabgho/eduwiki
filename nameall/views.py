from django.shortcuts import render, redirect, Http404
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import string
import random
import os
import datetime
from xpinyin import Pinyin
import logging

from models import *
from gender_classifier import GenderClassifier
from autoassess.visitorlog import log_visitor_ip
from autoassess.local_conf import model_root

GENDER_MODEL_PATH = model_root + '/nameall_models/gender_model/gender'
GENDER_PREDICTOR = None


def load_gender_predict_model(model_path=GENDER_MODEL_PATH):
    logging.info('Loading gender model...')
    gen_class = GenderClassifier()
    gen_class.loadModel(model_path)
    logging.info('Gender model loaded.')
    return gen_class


def name_home(request):
    request_data = {}
    if request.method == 'GET':
        request_data = request.GET
    elif request.method == 'POST':
        request_data = request.POST
    response_data = {}

    return render(request, 'nameall/nameall.html', response_data)


def name_submit(request):
    ip = log_visitor_ip(request)
    request_data = {}
    if request.method == 'GET':
        request_data = request.GET
    elif request.method == 'POST':
        request_data = request.POST
    response_data = {}

    global GENDER_PREDICTOR
    if not GENDER_PREDICTOR:
        GENDER_PREDICTOR = load_gender_predict_model(GENDER_MODEL_PATH)

    target_name = request_data['name']
    try:
        name_info = NameInfo(
            name=request_data['name'],
            gender=request_data.get('gender', None),
            country=request_data.get('country', None),
            time=datetime.datetime.now(),
            ip=ip
        )
        name_info.save()
    except:
        pass

    is_chinese = any(u'\u4e00' <= c <= u'\u9fff' for c in target_name)
    if is_chinese:
        py = Pinyin()
        target_name = ' '.join(
            [string.capitalize(py.get_pinyin(target_name[1:], '')),
             string.capitalize(py.get_pinyin(target_name[0], ''))]
        )

    if type(target_name) is unicode:
        target_name = target_name.encode('utf-8')

    if 'diyi' in target_name.lower() and 'yang' in target_name.lower():
        response_data['gender'] = 'SPECIAL'
        response_data['redirect_url'] = '/nameall/ydy'
        return JsonResponse(response_data)

    if ('lidan' in target_name.lower() or 'coco' in target_name.lower()) \
            and ('mu' in target_name.lower() or 'mou' in target_name.lower()):
        response_data['gender'] = 'LOVELY'

        return JsonResponse(response_data)
    is_male = GENDER_PREDICTOR.predict(target_name)
    if is_male:
        response_data['gender'] = 'MALE'
    else:
        response_data['gender'] = 'FEMALE'

    return JsonResponse(response_data)


@csrf_exempt
def name_report(request):
    ip = log_visitor_ip(request)
    request_data = {}
    if request.method == 'GET':
        request_data = request.GET
    elif request.method == 'POST':
        request_data = request.POST
    response_data = {}

    try:
        name_info = NameInfo(
            name=request_data['name'],
            gender=request_data.get('gender', None),
            country=request_data.get('country', None),
            time=datetime.datetime.now(),
            ip=ip
        )
        name_info.save()
    except:
        pass

    return JsonResponse(response_data)


def ydy(request):
    ip = log_visitor_ip(request)
    request_data = {}
    if request.method == 'GET':
        request_data = request.GET
    elif request.method == 'POST':
        request_data = request.POST
    response_data = {}

    return render(request, 'nameall/ydydyt.html', request)