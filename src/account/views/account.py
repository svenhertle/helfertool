from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _

from registration.views.utils import nopermission

from ..forms import CreateUserForm
from ..templatetags.permissions import has_adduser_group

import logging
logger = logging.getLogger("helfertool")


@login_required
def add_user(request):
    # check permission
    if not (request.user.is_superuser or has_adduser_group(request.user)):
        return nopermission(request)

    # form
    form = CreateUserForm(request.POST or None)

    if form.is_valid():
        user = form.save()

        messages.success(request, _("Added user %(username)s" %
                         {'username': user}))

        logger.info("user created", extra={
            'user': request.user,
            'added_user': user.username,
        })

        return redirect('account:add_user')

    context = {'form': form}
    return render(request, 'account/add_user.html', context)


@login_required
def change_user(request):
    if request.user.has_usable_password():
        pw_form = PasswordChangeForm(data=request.POST or None,
                                     user=request.user)

        if pw_form.is_valid():
            pw_form.save()
            update_session_auth_hash(request, pw_form.user)

            logger.info("password changed", extra={
                'user': request.user,
            })

            messages.success(request, _("Changed password successfully"))

            return redirect('account:change_user')
    else:
        # user from LDAP
        pw_form = None

    context = {'pw_form': pw_form}
    return render(request, 'account/change_user.html', context)
