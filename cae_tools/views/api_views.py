"""
Api views for querying data from forms, etc.
"""

# System Imports.
from django.db.models import Q
from django.http import JsonResponse

# User Imports.
from cae_home import models


def get_wmu_user(request):
    """
    Pulls corresponding WmuUser model.
    """
    # Grab value passed into api call.
    identifier = request.GET.get('identifier', None)

    # Initialize to empty return.
    data = {
        'bronco_net': None,
        'winno': None,
        'first_name': None,
        'middle_name': None,
        'last_name': None,
        'user_type': None,
        'is_active': None,
        'official_email': None,
    }

    # Attempt to grab WmuUser with corresponding value.
    # Note we OR, to check BroncoNet/Winno separately.
    # We also use iexact, so that the field can match regardless of passed letter capitalization.
    # Finally, we convert this into a dictionary of only the model fields we care about.
    wmu_user = models.WmuUser.objects.filter(
        Q(bronco_net__iexact=identifier)
        | Q(winno__iexact=identifier)
    ).values(
        'bronco_net',
        'winno',
        'first_name',
        'middle_name',
        'last_name',
        'user_type',
        'is_active',
        'official_email',
    ).first()

    # Check if we actually had a match.
    if wmu_user:
        # Match found. Override values with actual model data.
        data.update(wmu_user)

    # Return as JSON object.
    return JsonResponse(data)


def get_department(request):
    """
    Pulls corresponding Department model.
    """
    # Grab value passed into api call.
    identifier = request.GET.get('identifier', None)

    # Initialize to empty return.
    data = {
        'name': None,
    }

    # Attempt to grab WmuUser with corresponding value.
    # Note we OR, to check name/slug separately.
    # We also use iexact, so that the field can match regardless of passed letter capitalization.
    # Finally, we convert this into a dictionary of only the model fields we care about.
    department = models.Department.objects.filter(
        Q(name__iexact=identifier)
        | Q(slug__iexact=identifier)
    ).values(
        'name',
    ).first()

    # Check if we actually had a match.
    if department:
        # Match found. Override values with actual model data.
        data.update(department)

    # Return as JSON object.
    return JsonResponse(data)


def get_room_type(request):
    """
    Pulls corresponding RoomType model.
    """
    # Grab value passed into api call.
    identifier = request.GET.get('identifier', None)

    # Initialize to empty return.
    data = {
        'name': None,
    }

    # Attempt to grab WmuUser with corresponding value.
    # Note we OR, to check name/slug separately.
    # We also use iexact, so that the field can match regardless of passed letter capitalization.
    # Finally, we convert this into a dictionary of only the model fields we care about.
    room_type = models.RoomType.objects.filter(
        Q(name__iexact=identifier)
        | Q(slug__iexact=identifier)
    ).values(
        'name',
    ).first()

    # Check if we actually had a match.
    if room_type:
        # Match found. Override values with actual model data.
        data.update(room_type)

    # Return as JSON object.
    return JsonResponse(data)


def get_room(request):
    """
    Pulls corresponding Room model.
    """
    # Grab value passed into api call.
    identifier = request.GET.get('identifier', None)

    # Initialize to empty return.
    data = {
        'department': None,
        'room_type': None,
        'name': None,
        'description': None,
        'capacity': None,
    }

    # Attempt to grab WmuUser with corresponding value.
    # Note we OR, to check name/slug separately.
    # We also use iexact, so that the field can match regardless of passed letter capitalization.
    # Finally, we convert this into a dictionary of only the model fields we care about.
    room = models.Room.objects.filter(
        Q(name__iexact=identifier)
        | Q(slug__iexact=identifier)
    ).values(
        'department',
        'room_type',
        'name',
        'description',
        'capacity',
    ).first()

    # Check if we actually had a match.
    if room:
        # Match found. Override values with actual model data.
        data.update(room)

    # Return as JSON object.
    return JsonResponse(data)


def get_major(request):
    """
    Pulls corresponding Major model.
    """
    # Grab value passed into api call.
    identifier = request.GET.get('identifier', None)

    # Initialize to empty return.
    data = {
        'department': None,
        'student_code': None,
        'program_code': None,
        'name': None,
        'degree_level': None,
        'is_active': None,
    }

    # Attempt to grab WmuUser with corresponding value.
    # Note we OR, to check student-code/prog-code/slug separately.
    # We also use iexact, so that the field can match regardless of passed letter capitalization.
    # Finally, we convert this into a dictionary of only the model fields we care about.
    major = models.Major.objects.filter(
        Q(student_code__iexact=identifier)
        | Q(program_code__iexact=identifier)
        | Q(slug__iexact=identifier)
    ).values(
        'department',
        'student_code',
        'program_code',
        'name',
        'degree_level',
        'is_active',
    ).first()

    # Check if we actually had a match.
    if major:
        # Match found. Override values with actual model data.
        data.update(major)

    # Return as JSON object.
    return JsonResponse(data)


def get_class(request):
    """
    Pulls corresponding WmuClass model.
    """
    # Grab value passed into api call.
    identifier = request.GET.get('identifier', None)

    # Initialize to empty return.
    data = {
        'code': None,
        'title': None,
        'description': None,
    }

    # Attempt to grab WmuUser with corresponding value.
    # Note we OR, to check code/title/slug separately.
    # We also use iexact, so that the field can match regardless of passed letter capitalization.
    # Finally, we convert this into a dictionary of only the model fields we care about.
    wmu_class = models.WmuClass.objects.filter(
        Q(code__iexact=identifier)
        | Q(slug__iexact=identifier)
        | Q(title__iexact=identifier)
    ).values(
        'code',
        'title',
        'description',
    ).first()

    # Check if we actually had a match.
    if wmu_class:
        # Match found. Override values with actual model data.
        data.update(wmu_class)

    # Return as JSON object.
    return JsonResponse(data)


def get_semester(request):
    """
    Pulls corresponding Semester model.
    """
    # Grab value passed into api call.
    identifier = request.GET.get('identifier', None)
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)

    # Initialize to empty return.
    data = {
        'name': None,
        'start_date': None,
        'end_date': None,
    }

    # Attempt to grab WmuUser with corresponding value.
    # Note we OR, to check name/(both dates) separately.
    # We also use iexact, so that the field can match regardless of passed letter capitalization.
    # Finally, we convert this into a dictionary of only the model fields we care about.
    semester = models.Semester.objects.filter(
        Q(name__iexact=identifier)
        | Q(
            start_date=start_date,
            end_date=end_date,
        ),
    ).values(
        'name',
        'start_date',
        'end_date',
    ).first()

    # Check if we actually had a match.
    if semester:
        # Match found. Override values with actual model data.
        data.update(semester)

    # Return as JSON object.
    return JsonResponse(data)
