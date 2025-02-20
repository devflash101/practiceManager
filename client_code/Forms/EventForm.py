import anvil.server
from AnvilFusion.components.FormBase import FormBase, POPUP_WIDTH_COL3
from AnvilFusion.components.FormInputs import *
from datetime import datetime, timedelta
from .. import Forms
from ..app.models import Entity

class EventForm(FormBase):

    def __init__(self, **kwargs):

        print('EventForm')
        kwargs['model'] = 'Event'
        self.case = LookupInput(name='case', label='Case', model='Case', text_field='case_name')
        self.no_case = CheckboxInput(name='no_case', label='Event is not linked to a Case',
                                     on_change=self.toggle_case)
        self.activity = LookupInput(model='Activity', name='activity', label='Event Type')
        self.notes = MultiLineInput(name='notes', label='Notes', rows=4)
        self.documents = FileUploadInput(name='documents', label='Documents', save=False)
        self.start_time = DateTimeInput(name='start_time', label='Start Date', on_change=self.update_time, string_format='MMM dd, yyyy hh:mm a')
        self.end_time = DateTimeInput(name='end_time', label='End Date', on_change=self.update_time, string_format='MMM dd, yyyy hh:mm a')
        self.staff = LookupInput(name='staff', label='Staff', model='Staff', text_field='full_name', select='multi')
        self.contact = LookupInput(name='contact', label='Contact', model='Contact', text_field='full_name',
                                   select='multi')
        self.location = LookupInput(name='location', label='Location', model='Entity', text_field='name',
                                    on_change=self.location_change)
        self.department = LookupInput(name='department', label='Department', model='Contact',
                                      text_field=['department', 'courtroom', 'last_name'],
                                      compute_option=self.contact_department, enabled=False)
        self.client_attendance_required = CheckboxInput(name='client_attendance_required',
                                                        label='Client attendance required')
        self.client_update = CheckboxInput(name='client_update', label='Client Update')

        sections = [
            {'name': '_', 'rows': [
                [self.case],
                [self.no_case],
            ]},
            {
                'name': 'case_details',
                'rows': [
                    [self.case],
                    [self.no_case]
                ]
            },
            {
                'name': 'event_details',
                'cols': [
                    [self.activity, self.location, self.department],
                    # [self.case, self.activity, self.location, self.department],
                    [self.documents, self.notes],
                ]
            },
            {
                'name': 'event_schedule',
                'label': 'Schedule',
                'rows': [
                    [self.start_time, self.end_time],
                ]
            },
            {
                'name': 'sharing_and_attendance',
                'label': 'Sharing & Attendance',
                'rows': [
                    [self.staff, self.contact],
                    [None, self.client_attendance_required],
                ]
            }
        ]

        super().__init__(sections=sections, width=POPUP_WIDTH_COL3, **kwargs)

    def toggle_case(self, args):
        if self.no_case.value is True:
            self.case.enabled = False
            self.case.value = None
        else:
            self.case.enabled = True

    def location_change(self, args):
        if self.location.value is not None:
            location_entity = Entity.get(self.location.value['uid'])
            if location_entity['entity_type']['name'] == 'Court':
                self.department.enabled = True
        else:
            self.department.enabled = False
            self.department.value = None

    def contact_department(self, rec):
        if rec['department'] and rec['courtroom'] and rec['last_name']:
            return f"{rec['department']}/{rec['courtroom']} - {rec['last_name']}"
        return None

    def update_time(self, args):
        if not self.start_time.value or not self.end_time.value:
            return
        if args['name'] == 'start_time' and self.start_time.value is not None:
            if (self.end_time.value - self.start_time.value).total_seconds() / 3600 < 1:
                self.end_time.value = self.start_time.value + timedelta(hours=1)
        if args['name'] == 'end_time':
            if self.end_time.value is not None:
                if self.start_time.value is None:
                    self.start_time = self.end_time.value - timedelta(hours=1)
                elif self.end_time.value <= self.start_time.value:
                    self.end_time.value = self.start_time.value + timedelta(hours=1)
