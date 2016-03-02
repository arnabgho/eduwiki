from django.shortcuts import render, redirect, Http404
from models import *
import string
import random
# Create your views here.
import os
import datetime
from django.http.response import JsonResponse
import ast


def label_guess(request):
    request_data = {}
    if request.method == 'GET':
        request_data = request.GET
    elif request.method == 'POST':
        request_data = request.POST
    response_data = {}

    if 'img' not in request_data or not request_data['img']:
        image_name = random_image_name(binary=True)
    else:
        image_name = request_data['img']
    response_data['image_name'] = image_name

    # hack for mnist images
    response_data['true_label'] = image_name[-5]

    if 'assignmentId' not in request_data:
        # user visiting mode not from mturk
        response_data['hitId'] = None

        response_data['assignmentId'] = "LABEL_GUESS_" + id_generator()
        response_data['workerId'] = "LABEL_GUESS_" + id_generator()
        response_data['turkSubmitTo'] = '/'
    else:
        assignmentId = request_data['assignmentId'].strip(" ")
        hitId = request_data['hitId']

        if "ASSIGNMENT_ID_NOT_AVAILABLE" == assignmentId:
            # preview mode
            response_data['assignmentId'] = assignmentId
            response_data['hitId'] = hitId
        else:
            # question form mode
            workerId = request_data['workerId']
            turkSubmitTo = request_data['turkSubmitTo']

            response_data['assignmentId'] = assignmentId
            response_data['hitId'] = hitId
            response_data['workerId'] = workerId
            response_data['turkSubmitTo'] = turkSubmitTo

    return render(request, 'exlabel/explore_label.html', response_data)


def label_submit(request):
    request_data = {}
    if request.method == 'GET':
        request_data = request.GET
    elif request.method == 'POST':
        request_data = request.POST
    response_data = {}

    trajectory = ExploreTrajectory(
        image_name=request_data['image_name'],
        # image_label=request_data['image_label'],
        worker_label=request_data['worker_label'],
        trajectory=request_data['trajectory'],
        actions=request_data['actions'],

        time=datetime.datetime.now(),
        workerId=request_data['workerId'],
        assignmentId=request_data['assignmentId'],
        hitId=request_data['hitId'],
        turkSubmitTo=request_data['turkSubmitTo'],
    )

    trajectory.save()

    # TODO::check if the label is correct
    response_data['correct'] = True
    return JsonResponse(response_data)


def id_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def random_image_name(binary=True):
    path = os.path.dirname(os.path.abspath(__file__))
    img_folder = os.path.join(path, 'static/mnist_images/')
    img_names = os.listdir(img_folder)
    if binary:
        img_names = [i for i in img_names if '-0.png' in i or '-1.png' in i]
    rnd_idx = random.randrange(len(img_names))
    img_name = img_names[rnd_idx]
    return img_name