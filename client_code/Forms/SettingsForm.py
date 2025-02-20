import anvil.server
from AnvilFusion.components.FormBase import FormBase, POPUP_WIDTH_COL1, POPUP_WIDTH_COL3
from AnvilFusion.components.FormInputs import *
from AnvilFusion.components.SubformGrid import SubformGrid
from ..Forms.ContactForm import ContactForm
from AnvilFusion.tools.utils import AppEnv


FEE_TYPE_RETAINER = ('Flat Fee', 'Hourly', 'Hybrid Flat/Hourly', 'Hybrid Flat/Contingency')
FEE_TYPE_LITIGATION = ('Contingency', 'Hybrid Flat/Contingency', 'Hybrid Hourly/Contingency')


class SettingsForm(FormBase):

    def __init__(self, **kwargs):
        kwargs['model'] = 'Lead'

        # schedule_activity_fields = [
        #     TextInput(name='activity', label='Activity'),
        #     DateTimeInput(name='due_time', label='Due Time'),
        #     TextInput(name='status', label='Status'),
        #     CheckboxInput(name='completed', label='Completed', save=False),
        # ]
        # self.schedule_activity = SubformBase(name='lead_activity', fields=schedule_activity_fields,
        #                                      model='LeadActivity', link_model='Lead', link_field='lead', save=False)
        lead_activities_view = {
            'model': 'SettingsActivity',
            'columns': [
                {'name': 'activity', 'label': 'Task / Activity', 'width': '25%'},
                {'name': 'due_time', 'label': 'Due Time', 'width': '25%'},
                {'name': 'status', 'label': 'Satus', 'width': '15%'},
                {'name': '_spacer', 'label': '', 'width': '40%'},
            ],
        }
        self.lead_activities = SubformGrid(name='lead_activity', label='Tasks and Activities', model='LeadActivity',
                                           link_model='Lead', link_field='lead', 
                                           form_container_id=kwargs.get('target'),
                                           view_config=lead_activities_view,
                                           add_edit_form=SettingsActivityForm,
                                           )
        self.lead_status = TextInput(name='lead_status', label='Lead Status', value="Open")
        self.lead_source = LookupInput(model='LeadSource', name='lead_source', label='Lead Source',
                                       on_change=self.lead_source_referral)
        self.intake_staff = LookupInput(name='intake_staff', label='Intake Staff', model='Staff',
                                        text_field='full_name', select='multi')

        self.referred_by = LookupInput(name='referred_by', label='Referred By', model='Contact', text_field='full_name')
        self.case_contacts = LookupInput(name='contacts', label='Contacts', model='Contact',
                                         text_field='full_name', select='multi')
        self.case_contacts.options = self.referred_by.options

        self.practice_area = LookupInput(model='PracticeArea', name='practice_area', label='Practice Area')
        self.case_number = TextInput(name='case_number', label='Case Number')
        self.case_name = TextInput(name='case_name', label='Case Name')
        self.case_stage = LookupInput(model='CaseStage', name='case_stage', label='Case Stage')
        self.cause_of_action = LookupInput(model='CauseOfAction', name='cause_of_action', label='Cause(s) of Action',
                                           select='multi')
        self.statute_of_limitations = DateInput(name='statute_of_limitations', label='SOL')
        self.auto_generate_case_name = CheckboxInput(label='Auto-Generate Case Name', save=False,
                                                     on_change=self.generate_case_name)
        self.add_statute_of_limitations = CheckboxInput(label='Add Statute of Limitations', save=False,
                                                        on_change=self.add_sol)

        self.incident_date = DateInput(name='incident_date', label='Incident Date')
        self.incident_location = TextInput(name='incident_location', label='Incident Location')
        self.case_description = MultiLineInput(name='case_description', label='Case Description', rows=4)

        self.fee_type = LookupInput(model='FeeType', name='fee_type', label='Fee Type',
                                    on_change=self.fee_type_fields)
        self.retainer = NumberInput(name='retainer', label='Retainer')
        self.pre_litigation_rate = NumberInput(name='pre_litigation_rate', label='Pre Litigation Rate')
        self.litigation_rate = NumberInput(name='litigation_rate', label='Litigation Rate')
        self.trial_included = CheckboxInput(name='trial_included', label='Trial Included')
        self.hours_limited_on_retainer = CheckboxInput(label='Hours Limited on Retainer', save=False,
                                                       on_change=self.limit_retainer)
        self.retainer_hour_limit = NumberInput(name='retainer_hour_limit', label='Retainer Hour Limit')
        self.investigator_included = CheckboxInput(label='Investigator Included', save=False,
                                                   on_change=self.include_investigator)
        self.investigator_budget = NumberInput(name='investigator_budget', label='Investigator Budget')
        self.record_seal_expungement_included = CheckboxInput(name='record_seal_expungement_included',
                                                              label='Record Seal/Expungement Included')


        # subforms = [self.schedule_activity]

        tabs = [
            {'name': 'lead_details', 'label': 'User', 'sections': [
                {'name': 'lead_info', 'label': 'Lead Information', 'rows': [
                    [self.lead_source, self.intake_staff],
                    [self.referred_by, None],
                ]},
                {'name': 'case_contacts', 'label': 'Case Contacts', 'rows': [
                    [self.case_contacts],
                ]},
                {'name': 'case_overview', 'label': 'Case Overview', 'rows': [
                    [self.practice_area, self.auto_generate_case_name],
                    [self.case_number, self.case_name],
                    [self.case_stage, self.add_statute_of_limitations],
                    [self.cause_of_action, self.statute_of_limitations],
                ]},
                {'name': 'case_details', 'label': 'Case Details', 'cols': [
                    [self.incident_date, self.incident_location, self.lead_status],
                    [self.case_description],
                ]},
            ]},
            {'name': 'billing', 'label': 'Security', 'sections': [
                {'name': 'billing_details', 'label': 'Billing Details', 'cols': [
                    [
                        self.fee_type,
                        self.retainer,
                        self.pre_litigation_rate,
                        self.litigation_rate,
                    ],
                    [
                        self.trial_included,
                        self.hours_limited_on_retainer,
                        self.retainer_hour_limit,
                        self.investigator_included,
                        self.investigator_budget,
                        self.record_seal_expungement_included,
                    ],
                ]},
            ]},
            {'name': 'lead_activities', 'label': 'Notification', 'sections': [
                {'name': '_', 'label': '', 'rows': [
                    [self.lead_activities]
                ]},
            ]},
        ]

        super().__init__(tabs=tabs, width=POPUP_WIDTH_COL3, **kwargs)
        self.fullscreen = True
    
    def form_open(self, args):
        super().form_open(args)
        self.lead_status.hide()

    def after_open(self):
        print(f"after_open self.data = {self.data}")
        if not self.data:
            self.case_name.enabled = False
            self.auto_generate_case_name.value = True
            self.lead_status.value = "Open"
            self.statute_of_limitations.hide()
            self.retainer.hide()
            self.retainer_hour_limit.hide()
            self.investigator_budget.hide()
            self.pre_litigation_rate.hide()
            self.litigation_rate.hide()
            self.referred_by.hide()
        else:
            self.generate_case_name(None)
            self.lead_source_referral(None)
            self.add_sol(None)
            self.limit_retainer(None)
            self.include_investigator(None)
            self.fee_type_fields(None)

    # auto_generate_case_name on_change handler
    def generate_case_name(self, args):
        if self.auto_generate_case_name.value is True:
            self.case_name.enabled = False
            self.case_name.value = 'AutoGenerated'
        else:
            self.case_name.enabled = True

    # lead_source on_change handler
    def lead_source_referral(self, args):
        if args['value'] is not None and args['value']['name'] == 'Referral':
            self.referred_by.show()
        else:
            self.referred_by.hide()
            self.referred_by.value = None

    # add_statute_of_limitations on_change handler
    def add_sol(self, args):
        if self.add_statute_of_limitations.value is True:
            self.statute_of_limitations.show()
        else:
            self.statute_of_limitations.hide()
            self.statute_of_limitations.value = None

    # hours_limited_on_retainer on_change handler
    def limit_retainer(self, args):
        if self.hours_limited_on_retainer.value is True:
            self.retainer_hour_limit.show()
        else:
            self.retainer_hour_limit.hide()
            self.retainer_hour_limit.value = None

    # investigator_included on_change handler
    def include_investigator(self, args):
        if self.investigator_included.value is True:
            self.investigator_budget.show()
        else:
            self.investigator_budget.hide()
            self.investigator_budget.value = None

    # fee_type on_change handler
    def fee_type_fields(self, args):
        if self.fee_type.value is None:
            self.retainer.hide()
            self.retainer.value = None
            self.pre_litigation_rate.hide()
            self.pre_litigation_rate.value = None
            self.litigation_rate.hide()
            self.litigation_rate.value = None
        else:
            if self.fee_type.value.name in FEE_TYPE_RETAINER:
                self.retainer.show()
            else:
                self.retainer.hide()
                self.retainer.value = None
            if self.fee_type.value.name in FEE_TYPE_LITIGATION:
                self.pre_litigation_rate.show()
                self.litigation_rate.show()
            else:
                self.pre_litigation_rate.hide()
                self.pre_litigation_rate.value = None
                self.litigation_rate.hide()
                self.litigation_rate.value = None


class SettingsActivityForm(FormBase):

    def __init__(self, **kwargs):
        kwargs['model'] = 'LeadActivity'

        self.activity = TextInput(name='activity', label='Activity')
        self.due_time = DateTimeInput(name='due_time', label='Due Time')
        self.status = TextInput(name='status', label='Status')
        self.completed = CheckboxInput(name='completed', label='Completed', save=False)

        sections = [
            {'name': '_', 'cols': [
                [self.activity, self.due_time, self.status, self.completed],
            ]}
        ]

        super().__init__(sections=sections, width=POPUP_WIDTH_COL1, **kwargs)
