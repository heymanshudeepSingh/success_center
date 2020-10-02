"""
Misc views for CAE Home app.
"""

# System Imports.
from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse

# User Imports.
from settings import logging as init_logging


# Import logger.
logger = init_logging.get_logger(__name__)



#region Special Views

def handler400(request, exception=None):
    return TemplateResponse(request, 'cae_home/errors/400.html', status=400)


def handler403(request, exception=None):
    return TemplateResponse(request, 'cae_home/errors/403.html', status=403)


def handler404(request, exception=None):
    return TemplateResponse(request, 'cae_home/errors/404.html', status=404)


def handler500(request, exception=None):
    return TemplateResponse(request, 'cae_home/errors/500.html', status=500)

#endregion Special Views


def info_schedules(request):
    """
    Temporary page to publicly display schedules of users.
    """
    return TemplateResponse(request, 'cae_home/info_schedules.html', {})


def info_servers(request):
    """
    Temporary page to publicly display servers maintained by admins.
    """
    return TemplateResponse(request, 'cae_home/info_servers.html', {
        'contact_mandroo': 'Andrew Barnes<br>znd7233@wmich.edu',
        'contact_hussein': 'Hussein Sheakh<br>hbn2774@wmich.edu',
        'contact_kira': 'Kira Hamelink<br>kdr1002@wmich.edu',
        'contact_musaab': 'Musaab Yousif<br>myn8219@wmich.edu',
        'contact_shagun': 'Shagun Choudhary<br>sgk8005@wmich.edu',
        'contact_phillip': 'Phillip Varner<br>pgs8661@wmich.edu',
    })


def info_software(request):
    """
    Temporary page to publicly display software maintained by programmers.
    """
    return TemplateResponse(request, 'cae_home/info_software.html', {
        'contact_brandon': 'Brandon Rodriguez<br>bfp5870@wmich.edu',
        'contact_jesse': 'Jesse Meachum<br>jdc4014@wmich.edu',
        'contact_singh': 'Simar Singh<br>hfv6838@wmich.edu'
    })


@login_required
def helpful_resources(request):
    """
    "Useful links" page for CAE Center employees.
    """
    return TemplateResponse(request, 'cae_home/helpful_resources.html', {})
