# core/views.py
from django.shortcuts import render
from http import HTTPStatus


def page_not_found(request, exception):
    template_index = 'core/404.html'
    return render(request,
                  template_index,
                  {'path': request.path},
                  status=HTTPStatus.NOT_FOUND,
                  )


def csrf_failure(request, reason=''):
    template_index = 'core/403csrf.html'
    return render(request,
                  template_index,
                  )


def server_error(request):
    template_index = 'core/500.html'
    return render(request,
                  template_index,
                  status=HTTPStatus.INTERNAL_SERVER_ERROR,
                  )


def permission_denied(request, exception):
    template_index = 'core/403.html'
    return render(request,
                  template_index,
                  status=HTTPStatus.FORBIDDEN,
                  )
