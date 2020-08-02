from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView, LoginView
from django.http import HttpResponseRedirect
# from django.http.response import HttpResponseRedirect
from django.urls import path
from django.views.generic.edit import FormMixin


from otree.extensions import get_extensions_modules, get_extensions_data_export_views
from otree import common, views

import inspect
import vanilla
from importlib import import_module

from django.conf import urls
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic.base import RedirectView
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import admin
from django.conf.urls.static import static

from otree.views.room import CreateRoom, DeleteRoom, UpdateRoom

ALWAYS_UNRESTRICTED = {
    'AssignVisitorToRoom',
    'InitializeParticipant',
    'MTurkLandingPage',
    'MTurkStart',
    'JoinSessionAnonymously',
    'OutOfRangeNotification',
    'ParticipantRoomHeartbeat',
    'ParticipantHeartbeatGBAT',
}

UNRESTRICTED_IN_DEMO_MODE = ALWAYS_UNRESTRICTED.union(
    {
        'AdminReport',
        'AdvanceSession',
        'CreateDemoSession',
        'DemoIndex',
        'SessionSplitScreen',
        'SessionDescription',
        'SessionMonitor',
        'SessionPayments',
        'SessionData',
        'SessionStartLinks',
    }
)


def view_classes_from_module(module_name):
    views_module = import_module(module_name)

    # what about custom views?
    return [
        ViewCls
        for _, ViewCls in inspect.getmembers(views_module)
        if hasattr(ViewCls, 'url_pattern')
           and inspect.getmodule(ViewCls) == views_module
    ]


def url_patterns_from_app_pages(module_name, name_in_url):
    views_module = import_module(module_name)

    view_urls = []
    for ViewCls in views_module.page_sequence:
        url_pattern = ViewCls.url_pattern(name_in_url)
        url_name = ViewCls.url_name()
        view_urls.append(urls.url(url_pattern, ViewCls.as_view(), name=url_name))

    return view_urls


def url_patterns_from_builtin_module(module_name: str):
    all_views = view_classes_from_module(module_name)

    view_urls = []
    for ViewCls in all_views:
        # automatically assign URL name for reverse(), it defaults to the
        # class's name
        url_name = getattr(ViewCls, 'url_name', ViewCls.__name__)

        if settings.AUTH_LEVEL == 'STUDY':
            unrestricted = url_name in ALWAYS_UNRESTRICTED
        elif settings.AUTH_LEVEL == 'DEMO':
            unrestricted = url_name in UNRESTRICTED_IN_DEMO_MODE
        else:
            unrestricted = True

        if unrestricted:
            as_view = ViewCls.as_view()
        else:
            as_view = login_required(ViewCls.as_view())
            # i want to use
            # staff_member_required decorator
            # but then .test_auth_level fails on client.get():
            # NoReverseMatch: 'admin' is not a registered namespace
        #

        url_pattern = ViewCls.url_pattern
        if callable(url_pattern):
            url_pattern = url_pattern()

        view_urls.append(urls.url(url_pattern, as_view, name=url_name))

    return view_urls


def extensions_urlpatterns():
    urlpatterns = []

    for url_module in get_extensions_modules('urls'):
        urlpatterns += getattr(url_module, 'urlpatterns', [])

    return urlpatterns


def extensions_export_urlpatterns():
    view_classes = get_extensions_data_export_views()
    view_urls = []

    for ViewCls in view_classes:
        if settings.AUTH_LEVEL in {'DEMO', 'STUDY'}:
            as_view = login_required(ViewCls.as_view())
        else:
            as_view = ViewCls.as_view()
        view_urls.append(urls.url(ViewCls.url_pattern, as_view, name=ViewCls.url_name))

    return view_urls


class GamesView(vanilla.TemplateView):
    template_name = 'otree/games.html'

class DaytraderIntroView(vanilla.TemplateView):
    template_name = 'otree/daytrader-introduction.html'


class DaytraderIntroView(vanilla.TemplateView):
    template_name = 'otree/introduction/daytrader-introduction.html'


class DaytraderIntro1View(vanilla.TemplateView):
    template_name = 'otree/introduction/daytrader-introduction1.html'


class DaytraderIntro2View(vanilla.TemplateView):
    template_name = 'otree/introduction/daytrader-introduction2.html'


class DaytraderIntro3View(vanilla.TemplateView):
    template_name = 'otree/introduction/daytrader-introduction3.html'


class DaytraderIntro4View(vanilla.TemplateView):
    template_name = 'otree/introduction/daytrader-introduction4.html'


class DaytraderIntro5View(vanilla.TemplateView):
    template_name = 'otree/introduction/daytrader-introduction5.html'


class DaytraderIntro6View(vanilla.TemplateView):
    template_name = 'otree/introduction/daytrader-introduction6.html'


class BadInfluenceIntroView(vanilla.TemplateView):
    template_name = 'otree/introduction/bad-influence-introduction.html'


class BadInfluenceIntro1View(vanilla.TemplateView):
    template_name = 'otree/introduction/bad-influence-introduction1.html'



def get_urlpatterns():
    urlpatterns = [
            urls.url(r'^admin/', admin.site.urls),
            urls.url(r'^accounts/', urls.include('otree.accounts.urls')),
            urls.url(r'^$', RedirectView.as_view(url='spil/', permanent=True)),
            urls.url(r'^spil/', GamesView.as_view(), name='games'),
            urls.url(r'^accounts/login/$', LoginView.as_view(), name='login'),
            urls.url(r'^accounts/logout/$', LogoutView.as_view(), name='logout'),
            urls.url(r'^delete/(?P<pk>\d+)/$', DeleteRoom.as_view(), name="delete_view_with_pk"),
            urls.url(r'^edit/(?P<pk>\d+)/$', UpdateRoom.as_view(), name="update_view_with_pk"),

            path('create_room/', CreateRoom.as_view(), name='create_room'),

            # Daytrader rules intro pages
            urls.url(r'^daytrader-introduction/$', DaytraderIntroView.as_view(), name="daytrader-intro"),
            urls.url(r'^daytrader-introduction/1/$', DaytraderIntro1View.as_view(), name="daytrader-intro1"),
            urls.url(r'^daytrader-introduction/2/$', DaytraderIntro2View.as_view(), name="daytrader-intro2"),
            urls.url(r'^daytrader-introduction/3/$', DaytraderIntro3View.as_view(), name="daytrader-intro3"),
            urls.url(r'^daytrader-introduction/4/$', DaytraderIntro4View.as_view(), name="daytrader-intro4"),
            urls.url(r'^daytrader-introduction/5/$', DaytraderIntro5View.as_view(), name="daytrader-intro5"),
            urls.url(r'^daytrader-introduction/6/$', DaytraderIntro6View.as_view(), name="daytrader-intro6"),

            # Bad influence rules intro pages
            urls.url(r'^bad-influence-introduction/$', BadInfluenceIntroView.as_view(), name="bad-influence-intro"),
            urls.url(r'^bad-influence-introduction/1/$', BadInfluenceIntro1View.as_view(), name="bad-influence-intro1"),

    ]

    urlpatterns += staticfiles_urlpatterns()

    used_names_in_url = set()
    for app_name in settings.INSTALLED_OTREE_APPS:
        models_module = common.get_models_module(app_name)
        name_in_url = models_module.Constants.name_in_url
        if name_in_url in used_names_in_url:
            msg = (
                "App {} has Constants.name_in_url='{}', "
                "which is already used by another app"
            ).format(app_name, name_in_url)
            raise ValueError(msg)

        used_names_in_url.add(name_in_url)

        views_module = common.get_pages_module(app_name)
        urlpatterns += url_patterns_from_app_pages(views_module.__name__, name_in_url)

    urlpatterns += url_patterns_from_builtin_module('otree.views.participant')
    urlpatterns += url_patterns_from_builtin_module('otree.views.demo')
    urlpatterns += url_patterns_from_builtin_module('otree.views.admin')
    urlpatterns += url_patterns_from_builtin_module('otree.views.room')
    urlpatterns += url_patterns_from_builtin_module('otree.views.mturk')
    urlpatterns += url_patterns_from_builtin_module('otree.views.export')

    urlpatterns += extensions_urlpatterns()
    urlpatterns += extensions_export_urlpatterns()

    return urlpatterns


urlpatterns = get_urlpatterns() + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
