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
from country_classifier import CountryClassifier
from autoassess.visitorlog import log_visitor_ip
from autoassess.local_conf import model_root

GENDER_MODEL_PATH = model_root + 'nameall_models/gender_model/gender'
GENDER_PREDICTOR = None
CHINESE_GENDER_MODEL_PATH = model_root + 'nameall_models/gender_model/gender-zh'
CHINESE_GENDER_PREDICTOR = None
COUNTRY_MODEL_PATH = model_root + 'nameall_models/gender_model/country'
COUNTRY_ID_PATH = model_root + 'nameall_models/gender_model/country-id.txt'
COUNTRY_PREDICTOR = None


def load_gender_predict_model(model_path=GENDER_MODEL_PATH):
    logging.info('Loading model...' + str(model_path))
    gen_class = GenderClassifier()
    gen_class.loadModel(model_path)
    logging.info('Gender loaded.')
    return gen_class


def load_country_predict_model(
        model_path=COUNTRY_MODEL_PATH,
        country_id_file=COUNTRY_ID_PATH):
    logging.info('Loading model...' + str(model_path))
    gen_class = CountryClassifier()
    gen_class.loadModel(model_path, country_id_file)
    logging.info('Country model loaded.')
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

    global GENDER_PREDICTOR, CHINESE_GENDER_PREDICTOR, COUNTRY_PREDICTOR
    if not CHINESE_GENDER_PREDICTOR:
        CHINESE_GENDER_PREDICTOR = load_gender_predict_model(
            CHINESE_GENDER_MODEL_PATH)
    if not GENDER_PREDICTOR:
        GENDER_PREDICTOR = load_gender_predict_model(GENDER_MODEL_PATH)
    if not COUNTRY_PREDICTOR:
        COUNTRY_PREDICTOR = load_country_predict_model()


    target_name = request_data['name']

    if not target_name:
        return JsonResponse({'gender': 'NONAME'})
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
    ### Country Prediction
    country = COUNTRY_PREDICTOR.predict(target_name)
    response_data['country'] = country.capitalize()
    if country == 'china':
        is_chinese = True
    ### Gender Prediction
    if is_chinese:
        is_male = CHINESE_GENDER_PREDICTOR.predict(target_name)
    else:
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