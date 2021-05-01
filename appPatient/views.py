import requests
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.crypto import get_random_string, hashlib
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers

import json

# Create your views here.
from . import response
from .exceptions import RequestException
from .models import Visit
from .serializers import VisitRequestSerializer, Visit

PANEL_TOKEN = "Y3VzdG9tZXI6Y3VzdG9tZXJAbG9jYWwuY29tOklOVEVSTkFMOjk5OTk5OQ=="


def token_validation(
        token):
    r = requests.post("http://authentication:8000/auth/verify", data={}, headers={"token": token})

    if r.status_code == 200:
        info = r.json()['data']
        return info
    else:
        raise Exception("Token is invalid")


def extract_request_data_post(request):
    try:
        if len(request.POST.keys()) > 0:
            request_data = request.POST
        else:
            request_data = json.load(request)
        return request_data
    except:
        return {}


def extract_request_headers(request):
    return request.headers


def validate_required_body_items(required_fields, request_data):
    errors = []
    for item in required_fields:
        if item not in request_data.keys():
            errors.append(item + " is required!")

    return errors


def validate_required_header_items(required_fields, request_headers):
    errors = []
    for item in required_fields:
        if item not in request_headers.keys():
            errors.append(item + " is required!")

    return errors


@csrf_exempt
def info(request):
    if request.method == "GET":
        # Validate Header
        request_headers = extract_request_headers(request)
        required_headers_fields = ["token"]
        errors = validate_required_header_items(required_headers_fields, request_headers)

        if len(errors) > 0:
            return response.bad_request_response(errors)

        info = token_validation(request_headers["token"])
        del info['id']

        if info['role'] != "PATIENT":
            return response.forbidden_response()

        return response.success_response(info)
    return response.method_not_allowed_response()


def request_visit(doctor_id, patient, datetime):
    r = requests.post("http://docot:8001/doctors/" + doctor_id + "/visit",
                      data={'datetime': datetime, 'patient': patient}, headers={"token": PANEL_TOKEN})
    if r.status_code == 200:
        visit = r.json()['data']
        return visit
    elif r.status_code == 400 or r.status_code == 404:
        raise RequestException(r.status_code, r.json()['error'])
    else:
        raise Exception("Visit Failed!")


def get_visit(doctor_id, visit_id):
    r = requests.get("http://doctor:8001/doctors/" + doctor_id + "/visit/" + str(visit_id),
                     data={}, headers={"token": PANEL_TOKEN})
    if r.status_code == 200:
        visit = r.json()['data']
        return visit
    elif r.status_code == 400 or r.status_code == 404:
        raise RequestException(r.status_code, r.json()['error'])
    else:
        raise Exception("Get Visit Failed!")


@csrf_exempt
def visit_req(request):
    if request.method == 'GET':
        try:
            # Validate Header
            request_headers = extract_request_headers(request)
            required_headers_fields = ["token"]
            errors = validate_required_header_items(required_headers_fields, request_headers)

            if len(errors) > 0:
                return response.bad_request_response(errors)

            info = token_validation(request_headers['token'])

            if info['role'] != "PATIENT":
                return response.forbidden_response()

            visits = Visit.objects.filter(customer=info['username'])
            visits_data = []

            for visit in visits:
                visits_data.append(VisitRequestSerializer(visit).data)

            return response.success_response(visits_data)

        except Exception as e:
            if str(e) == "Token is invalid":
                return response.un_authorized_response()
            elif str(e) == "Visit matching query does not exist.":
                return response.success_response([])
            return response.internal_server_error_response()

    if request.method == 'POST':
        try:
            # Validate Header
            request_headers = extract_request_headers(request)
            required_headers_fields = ["token"]
            errors = validate_required_header_items(required_headers_fields, request_headers)

            if len(errors) > 0:
                return response.bad_request_response(errors)

            # Validate Data
            request_data = extract_request_data_post(request)
            required_data_fields = ["doctor_id", "datetime"]
            errors = validate_required_body_items(required_data_fields, request_data)

            if len(errors) > 0:
                return response.bad_request_response(errors)

            info = token_validation(request_headers['token'])

            if info['role'] != "PATIENT":
                return response.forbidden_response()

            doctor_id = request_data['doctor_id']
            username = info['username']

            visit = Visit(doctor_id=doctor_id, customer=username)

            result = request_visit(visit.restaurant, visit.customer, request_data['datetime'])
            visit.datetime = result["datetime"]
            visit.id = result["id"]
            visit.status = result["status"]
            visit.save()
            return response.success_response(VisitRequestSerializer(visit).data)

        except Exception as e:
            if str(e) == "Token is invalid":
                return response.un_authorized_response()
            elif str(e) == "Visit Failed!":
                return response.internal_server_error_response()
            elif isinstance(e, RequestException):
                if e.status == 404:
                    return response.not_found_response(e.message)
                elif e.status == 400:
                    return response.bad_request_response(e.message)
            else:
                return response.internal_server_error_response()
    return response.internal_server_error_response()


@csrf_exempt
def get_visit_detail(request, visit_id):
    if request.method == 'GET':
        try:
            # Validate Header
            request_headers = extract_request_headers(request)
            required_headers_fields = ["token"]
            errors = validate_required_header_items(required_headers_fields, request_headers)

            if len(errors) > 0:
                return response.bad_request_response(errors)

            info = token_validation(request_headers['token'])

            if info['role'] != "PATIENT":
                return response.forbidden_response()

            visit = Visit.objects.get(id=visit_id)
            visit_info = get_visit(visit.doctor_id, visit.id)
            visit.status = visit_info["status"]
            visit_info["id"] = visit.id
            visit.save()

            return response.success_response(visit_info)

        except Exception as e:
            if str(e) == "Token is invalid":
                return response.un_authorized_response()
            elif str(e) == "Get Visit Failed!":
                return response.internal_server_error_response()
            elif str(e) == "Visit matching query does not exist.":
                return response.not_found_response("Visit Not Found")
            elif isinstance(e, RequestException):
                if e.status == 404:
                    return response.not_found_response(e.message)
                elif e.status == 400:
                    return response.bad_request_response(e.message)
            else:
                return response.internal_server_error_response()


@csrf_exempt
def health(request):
    if request.method == 'GET':
        try:
            return response.success_response("OK")

        except Exception as e:
            return response.internal_server_error_response()
