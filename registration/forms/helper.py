from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from ..models import Helper, Shift, Job


class HelperForm(forms.ModelForm):
    class Meta:
        model = Helper
        exclude = ['event', 'shifts', 'privacy_statement', ]

    def __init__(self, *args, **kwargs):
        self.related_event = kwargs.pop('event')
        self.new_coordinator = kwargs.pop('new_coordinator', False)
        self.job = kwargs.pop('job', None)

        super(HelperForm, self).__init__(*args, **kwargs)

        # remove field for shirt?
        if not self.related_event.ask_shirt:
            self.fields.pop('shirt')

        # remove field for vegetarian food?
        if not self.related_event.ask_vegetarian:
            self.fields.pop('vegetarian')

        # remove field for instruction for food handling
        if not self.instance.needs_infection_instruction:
            self.fields.pop('infection_instruction')

    def save(self, commit=True):
        instance = super(HelperForm, self).save(False)

        instance.event = self.related_event

        if self.new_coordinator and self.related_event.mail_validation:
            instance.validated = False

        if commit:
            instance.save()

        if self.job:
            self.job.coordinators.add(self.instance)

        return instance


class HelperAddShiftForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.helper = kwargs.pop('helper')
        self.user = kwargs.pop('user')

        super(HelperAddShiftForm, self).__init__(*args, **kwargs)

        event = self.helper.event

        # field that contains all shifts if
        #  - user is admin for shift/job
        #  - helper is not already in this shift

        # all administered shifts
        administered_jobs = [job for job in event.job_set.all()
                             if job.is_admin(self.user)]
        shifts = Shift.objects.filter(job__event=event,
                                      job__in=administered_jobs)

        # exclude already taken shifts
        shifts = shifts.exclude(id__in=self.helper.shifts.all())

        # add field
        self.fields['shifts'] = forms.ModelMultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            queryset=shifts, required=True)

    def clean(self):
        super(HelperAddShiftForm, self).clean()

        for shift in self.cleaned_data['shifts']:
            if shift.is_full():
                raise ValidationError(_("This shift if already full: "
                                        "%(shift)s") % {'shift': str(shift)})

    def save(self):
        for shift in self.cleaned_data['shifts']:
            self.helper.shifts.add(shift)
        self.helper.save()


class HelperAddCoordinatorForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.helper = kwargs.pop('helper')
        self.user = kwargs.pop('user')

        super(HelperAddCoordinatorForm, self).__init__(*args, **kwargs)

        event = self.helper.event

        # field that contains all jobs if
        #  - user is admin for job
        #  - helper is not already coordinator for this job

        # all administered jobs
        coordinated_jobs = self.helper.coordinated_jobs
        jobs = [job.pk for job in event.job_set.all()
                if job.is_admin(self.user) and job not in coordinated_jobs]

        # we need a queryset
        jobs = Job.objects.filter(pk__in=jobs)

        # add field
        self.fields['jobs'] = forms.ModelMultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            queryset=jobs, required=True)

    def save(self, commit=True):
        for job in self.cleaned_data['jobs']:
            job.coordinators.add(self.helper)
            job.save()


class HelperDeleteForm(forms.ModelForm):
    class Meta:
        model = Helper
        fields = ['firstname', 'surname', 'email', 'shifts', ]
        widgets = {
            'shifts': forms.CheckboxSelectMultiple
        }

    def __init__(self, *args, **kwargs):
        self.shift = kwargs.pop('shift')
        self.user = kwargs.pop('user')
        self.show_all_shifts = kwargs.pop('show_all_shifts')

        super(HelperDeleteForm, self).__init__(*args, **kwargs)

        # show only the one specified shift ot shifts, where the helper is
        # registered
        if self.show_all_shifts:
            self.fields['shifts'].queryset = self.instance.shifts
        else:
            self.fields['shifts'].queryset = Shift.objects.filter(
                pk=self.shift.pk)  # we need a queryset, not a Shift object

        # make firstname, surname and email readonly
        for name in ('firstname', 'surname', 'email'):
            self.fields[name].widget.attrs['readonly'] = True

    def clean(self):
        super(HelperDeleteForm, self).clean()

        # check if user is admin for all shifts that will be deleted
        for shift in self.get_deleted_shifts():
            if not shift.job.is_admin(self.user):
                raise ValidationError(_("You are not allowed to delete a "
                                        "helper from the job \"%(jobname)s\"")
                                      % {'jobname': shift.job.name})

    def get_deleted_shifts(self):
        return self.cleaned_data['shifts']

    def delete(self):
        # delete all selected shifts
        for shift in self.cleaned_data['shifts']:
            self.instance.shifts.remove(shift)


class HelperDeleteCoordinatorForm(forms.ModelForm):
    class Meta:
        model = Helper
        fields = ['firstname', 'surname', 'email', ]

    def __init__(self, *args, **kwargs):
        self.job = kwargs.pop('job')

        super(HelperDeleteCoordinatorForm, self).__init__(*args, **kwargs)

        # make firstname, surname and email readonly
        for name in ('firstname', 'surname', 'email'):
            self.fields[name].widget.attrs['readonly'] = True

    def delete(self):
        self.job.coordinators.remove(self.instance)


class HelperSearchForm(forms.Form):
    pattern = forms.CharField(
        min_length=2,
        max_length=100,
        label=_("Search term"),
    )

    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event')
        self.user = kwargs.pop('user')

        super(HelperSearchForm, self).__init__(*args, **kwargs)

    def get(self):
        p = self.cleaned_data['pattern']

        data = self.event.helper_set.filter(Q(firstname__icontains=p) |
                                            Q(surname__icontains=p) |
                                            Q(email__icontains=p) |
                                            Q(phone__icontains=p))
        data = filter(lambda h: h.can_edit(self.user), data)

        return data
