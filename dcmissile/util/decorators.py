import logging
log = logging.getLogger(__name__)

from django.shortcuts import render_to_response
from django.template import RequestContext


class do(object):
    def __init__(self, template):
        self.template = template

    def __call__(self, f):
        def decorate(request, *args, **kwargs):
            obj = f(request, *args, **kwargs)
            if type(obj) == type({}):
                if 'template' in obj:
                    self.template = obj['template']

                ctx_response = { }
                return render_to_response(self.template, obj,
                    context_instance=RequestContext(request, ctx_response))
            else:
                log.debug('skipping and returning view response object')
                return obj
        return decorate
