import logging
log = logging.getLogger(__name__)

from django import forms
from django.utils.translation import ugettext_lazy as _


class MissileForm(forms.Form):
    action = forms.ChoiceField(label=_("action"),
                               choices=(
                                    ('left', _('left')),
                                    ('down', _('down')),
                                    ('up', _('up')),
                                    ('right', _('right')),
                                    ('fire', _('fire')),
                                )
        )
    parameter = forms.IntegerField(label=_("parameter"), min_value=0)
