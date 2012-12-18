from django.conf.urls.defaults import *

urlpatterns = patterns('',
                       (r'^$', 'labgeeks_delphi.views.delphi_home'),
                       (r'^create/$', 'labgeeks_delphi.views.create_question'),
                       (r'^(?P<q_id>[\d]+)/$', 'labgeeks_delphi.views.view_question'),
                       (r'^(?P<q_id>[\d]+)/answer/$', 'labgeeks_delphi.views.answer_question'),
                       (r'^(?P<q_id>[\d]+)/select_answer/$', 'labgeeks_delphi.views.select_answer'),
                       )
