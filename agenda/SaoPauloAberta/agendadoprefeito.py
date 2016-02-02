#coding: utf-8
import re
import time
import datetime
from five import grok
from plone import api

from z3c.form import group, field
from zope import schema
from zope.interface import invariant, Invalid
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.security import checkPermission

from plone.dexterity.content import Container
from plone.directives import dexterity, form
from plone.app.textfield import RichText
from plone.namedfile.field import NamedImage, NamedFile
from plone.namedfile.field import NamedBlobImage, NamedBlobFile
from plone.namedfile.interfaces import IImageScaleTraversable

from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName

from agenda.SaoPauloAberta import MessageFactory as _
from tipo_agendadoprefeito import ITipoAgendaDoPrefeito
from portal.SaoPauloAberta.utils import *

# Interface class; used to define content-type schema.


class IAgendaDoPrefeito(form.Schema, IImageScaleTraversable):
    """
    Container Agenda do Prefeito
    """
    form.model("models/agendadoprefeito.xml")

class AgendaDoPrefeito(Container):
    grok.implements(IAgendaDoPrefeito)

import pdb
import logging

from email.Utils import formatdate

class ElementRetriever(object):
    """ Base class for retrieving spa elements for container"""
    def __init__(self, request = None):        
        request.response.setHeader("Expires",formatdate(time.time() + (60 * 15), usegmt=True))

        self.el_range = 12
        self.el_begin = 0

        self.nonNullNextQuery = False
        self.providesType = ITipoAgendaDoPrefeito.__identifier__
    
        self.queryCache = []
        self.numNonWinner = 0
        self.numWinner = 0

        self.filter = "all"
        self.whom = "all"
        self.action = "all"
        self.view = "list"
        self.week = 0
        if request is not None:
                if "whom" in request.form.keys():
                    self.whom = request.form["whom"]

                if "action" in request.form.keys():
                    self.action = request.form["action"]

                if "view" in request.form.keys():
                    self.view = request.form["view"]
                
                if "week" in request.form.keys():
                    self.week = int(request.form["week"])

                if "filter" in request.form.keys():
                    self.filter = request.form["filter"]

    def update(self):
        if self.action == "submitted" and not checkPermission("cmf.ReviewPortalContent", self.context):
            self.action = "all"

        if self.whom == "mine" and self.action == "submitted":
            self.action = "all"

        self.LoadData()


        date = datetime.datetime.utcnow() + datetime.timedelta(minutes=3)

    def LoadCalendar(self, week=0):
        context = aq_inner(self.context)
        form = context.REQUEST.form
        catalog = getToolByName(context, 'portal_catalog')
        query = catalog({'object_provides':self.providesType,
                           'path':'/'.join(context.getPhysicalPath()),
                           'sort_on':'start',
                           'start': {'query':(self.GetCalStart(week), self.GetCalEnd(week)), 'range':'min:max'}
                         })
                   
        elements = self.FilterElements(query)
        elements = elements[self.el_begin : self.el_begin + self.el_range]
        self.nonNullNextQuery = len(query) >= self.el_begin + self.el_range 

        return elements

    def GetCalendarIndexes(self, elements):
        #Retrieve elements by day
        events_by_date = {}
        for element in elements:
            date = element.start.date().strftime("%Y%m%d") 
            if not date in events_by_date.keys():
                events_by_date[date] = []
            events_by_date[date].append(element)

        #Retrieve elements by time and count max occurences of events in the same hour
        elements_by_time = {}
        for date in events_by_date.keys():
            local_elements_by_time = {}
            for element in events_by_date[date]:
                time = element.start.time().strftime("%H%M%S")
                if not time in local_elements_by_time:
                    local_elements_by_time[time] = 0
                local_elements_by_time[time] += 1
            #Update global events by time
            for time in local_elements_by_time.keys():
                if time not in elements_by_time.keys():
                    elements_by_time[time] = 0
                if local_elements_by_time[time] > elements_by_time[time]:
                    elements_by_time[time] = local_elements_by_time[time]
        
        #Make a list of hours in which there are events
        events_list = []
        for time, number in elements_by_time.items():
            for i in range(number):
                events_list.append(time)
        events_list.sort()
        return events_list

    def GetCalendarEvents(self):
        week = self.week

        week_days = [6, 0, 1, 2, 3, 4, 5]
        elements = self.LoadCalendar(week)
        indexes = self.GetCalendarIndexes(elements)

        remaining_elements = elements
        for atom in indexes:
            atom_events = []
            for week_day in week_days:
                added_element = False
                for event in remaining_elements:
                    if event.start.date().weekday() == week_day:
                        event_time = event.start.time().strftime("%H%M%S")
                        if event_time == atom:
                            atom_events.append(event)
                            remaining_elements.remove(event)
                            added_element = True
                            break
                if not added_element:
                    atom_events.append(None)
            yield atom_events

    def LoadData(self):                
        context = aq_inner(self.context)
        form = context.REQUEST.form
                 
        if "el_range" in form.keys() and "el_begin" in form.keys():
            self.el_range = int(form['el_range'])
            self.el_begin = int(form['el_begin']) + self.el_range
            
        catalog = getToolByName(context, 'portal_catalog')
        query = catalog(object_provides=self.providesType,
                   path='/'.join(context.getPhysicalPath()),
                   sort_on='start'
                   )
                   
        elements = self.FilterElements(query)
        elements = elements[self.el_begin : self.el_begin + self.el_range]
        self.nonNullNextQuery = len(query) >= self.el_begin + self.el_range 

        self.queryCache = elements

    def NonNullNextQuery(self):        
        return self.nonNullNextQuery
        
    def GetQueryString(self):        
        query = "el_begin=" + str(self.el_begin) + "&el_range=" + str(self.el_range) 
        query += "&filter=" + self.filter
        query += "&whom=" + self.whom
        query += "&action=" + self.action
        query += "&view=" + self.view
        query += "&week=" + str(self.week)
        return query 
    
    def Elements(self):
        if len(self.queryCache) <= 0:
            self.LoadData()
        return self.queryCache

    def FilterElements(self, elements):
        uid = api.user.get_current().id
        if self.whom == "mine":
            elements = filter(lambda el: el.getObject().Creator() == uid, elements)
        
        if self.whom == "all" and self.action == "all" or self.action == "submitted":
            elements = filter(lambda el: el.getObject().start >= datetime.datetime.now(), elements)

        toPublish = filter(lambda el: el.review_state=="private" and el.getObject().state=="submit" and el.getObject().start >= datetime.datetime.now(), elements)
 
        self.toPublish = len(toPublish)
        if self.whom == "all" and self.action == "all":
            elements = filter(lambda el: el.review_state=="published", elements)

        winner = filter(lambda el: el.getObject().winner, elements)
        self.numWinner = len(winner)
        nonWinner = filter(lambda el: not el.getObject().winner, elements)
        self.numNonWinner = len(nonWinner)

        #If has no non-winner, only winners are visible
        if self.numNonWinner == 0 and self.numWinner != 0:
            self.action="winner"
        
        if self.action == "submitted":
            elements = toPublish
        elif self.action == "winner":
            elements = winner
        else:
            elements = nonWinner

        if self.filter == "draft":
            elements = filter(lambda el: self.GetObjectState(el)=="save", elements)
        elif self.filter == "submitted":            
            elements = filter(lambda el: self.GetObjectState(el)=="submit", elements)
        elif self.filter == "published":
            elements = filter(lambda el: self.GetObjectState(el)=="published", elements)
        elif self.filter == "expired":
            elements = filter(lambda el: self.GetObjectState(el)=="expired", elements)

        return elements 

    def GetPreFilter(self):
        if "axis" in self.request.form.keys():
           return self.request.form['axis']
        return ""

    def GetObjectState(self, object):
        state = object.review_state
        element = object.getObject()
        status = element.state
        if state == "published" and status =="submit":
            status = state
        
        if element.start < datetime.datetime.now() and\
           not element.winner:
            status = "expired"
        return status

    def TranslateState(self, object):
        state = self.GetObjectState(object)
        stateTable = {
                        "published": "Publicado",
                        "submit" : "Submetido à Análise",
                        "save": "Rascunho",
                        "selected": "Selecionado",
                        "expired": "Expirado"
                    }
        return stateTable[state]

    def IsMine(self, object):
        uid = api.user.get_current().id
        return uid == object.getObject().Creator()

    def CanPublish(self):
       return checkPermission("cmf.ReviewPortalContent", self.context)

    def GetCalStart(self, weekDelta = None):
        if weekDelta is None:
            weekDelta = self.week

        today = datetime.datetime.now() + datetime.timedelta(weeks = weekDelta)
        start = today - datetime.timedelta(days = today.weekday() + 1)
        return start

    def GetCalEnd(self, weekDelta = None):
        if weekDelta is None:
            weekDelta = self.week

        today = datetime.datetime.now() + datetime.timedelta(weeks = weekDelta)
        end = today + datetime.timedelta(days = (5 - today.weekday())) 
        return end

    def ConvertMonthName(self, month):
        return GetMonthName(month)

    def ConvertFullMonthName(self, month):
        return GetFullMonthName(month)

    def GetStartTime(self, element):
        return element.getObject().start.time().strftime("%H:%M")

class View(grok.View, ElementRetriever):
    grok.context(IAgendaDoPrefeito)
    grok.require('zope2.View')  
    grok.name('view') 
    
    def __init__(self, context, request):
        super(View, self).__init__(context, request)
        ElementRetriever.__init__(self, request)

    def update(self, *args):
        super(View, self).update(*args)
        ElementRetriever.update(self)

    def AuthenticatedUser(self):
        context = aq_inner(self.context)
        mbs = getToolByName(context, "portal_membership")
        return not mbs.isAnonymousUser()

class Elements(grok.View, ElementRetriever):    
    grok.context(IAgendaDoPrefeito)
    grok.require('zope2.View')  
    grok.name('elements')    
 
    def __init__(self, context, request):
        super(Elements, self).__init__(context, request)
        ElementRetriever.__init__(self, request)

    def update(self, *args):
        super(Elements, self).update(*args)
        ElementRetriever.update(self)

    def AuthenticatedUser(self):
        context = aq_inner(self.context)
        mbs = getToolByName(context, "portal_membership")
        return not mbs.isAnonymousUser()

class AddElement(grok.View, ElementRetriever):
    grok.context(IAgendaDoPrefeito)
    grok.require('zope2.View')  
    grok.name('addElement')    
        
    def __init__(self, context, request):
        super(AddElement, self).__init__(context, request)
        ElementRetriever.__init__(self, request) 
        self.context = context
        self.request = request
        self.whom = "add"
        if "evt" in self.request.form.keys():
            self.baseObject = self.context[self.request.form["evt"]]
            if self.baseObject.state != "save":
                self.baseObject = None
        else:
            self.baseObject = None

    def update(self):
        if not self.AuthenticatedUser():
            self.request.response.redirect("/")
    
    def AuthenticatedUser(self):
        context = aq_inner(self.context)
        mbs = getToolByName(context, "portal_membership")
        return not mbs.isAnonymousUser()

    def FormatDate(self, object):
        return str(object.day) + "/" + str(object.month) + "/" + str(object.year)

    def FormatTime(self, object):
        return str(object.hour) + ":" + str(object.minute)

    def GetMedia(self):
        media = []
        if self.baseObject:
            frontPage = int(self.baseObject.frontPage);
            for i in range(5):
                elementUri = self.baseObject.__getattribute__("media" + str(i+1) + "URI") or ''
                elementName = self.baseObject.__getattribute__("media" + str(i+1) + "name") or ''
                media.append(MediaElement(elementName, elementUri, frontPage == i))
        return media

class MediaElement(object):
    def __init__(self, name, url, isFront):
        self.name = name
        self.url = url
        self.isFront = isFront

def SaveData(context, request, new_content_item):
    form = request.form
    title = form["title"]
    if len(title) > 128:
        title = title[:128]

    summary = form["summary"]
    if len(summary) > 256:
        summary = summary[:256]

    description = form["description"]
    if len(description) > 1024:
         description = description[:1024]

    startDate = form["start-date"]
    startTime = form["start-time"]
    endDate = form["end-date"]
    endTime= form["end-time"]
    location = form["location"]
    mapCenter = form["map-center"]
    zoomLevel = form["zoom-level"]
    frontPage = form["front-page"]
    action = form["action"]
        
    media = {}
    for key, value in form.items():
        mediaKey = re.search("media(\d+)(url|title)", key, re.I)
        if mediaKey is not None:
            mediaId = int(mediaKey.group(1))
            if mediaId not in media.keys():
                media[mediaId] = PageMedia()
            if "url" == mediaKey.group(2):
                media[mediaId].url = value;
            elif "title" == mediaKey.group(2):
                media[mediaId].title = value

    new_content_item.title = title.decode("utf-8")
    new_content_item.description = summary.decode("utf-8")
    new_content_item.fullDescription = description.decode("utf-8")
    new_content_item.location = location.decode("utf-8")
    new_content_item.mapCenter = mapCenter.decode("utf-8")
    new_content_item.zoomLevel = zoomLevel.decode("utf-8")
    new_content_item.frontPage = frontPage.decode("utf-8")
    new_content_item.winner = False
    new_content_item.start = GetDateTime(startDate, startTime)
    new_content_item.end = GetDateTime(endDate, endTime)
    new_content_item.state = action.decode("utf-8")
    for key, value in media.items():
        new_content_item.__setattr__("media" + str(key + 1) + "name",value.title.decode("utf-8"))
        new_content_item.__setattr__("media" + str(key + 1) + "URI",value.url.decode("utf-8"))

    catalog = getToolByName(context, "portal_catalog") 
    err = catalog.refreshCatalog(clear=True)

def GetDateTime(dateStr, timeStr):
    reDate = re.search("(\d+)/(\d+)/(\d+)", dateStr)
    reTime = re.search("(\d+):(\d+)", timeStr)

    if reDate is not None:
        year = int(reDate.group(3))
        month = int(reDate.group(2))
        day = int(reDate.group(1))
    
    if reTime is not None:
        hour = int(reTime.group(1))
        minute = int(reTime.group(2))

    if reTime is None or reDate is None:
        return datetime.datetime.now()

    return datetime.datetime(year, month, day, hour, minute)

class CommitElement(grok.View):
    grok.context(IAgendaDoPrefeito)
    grok.require('zope2.View')
    grok.name('commitElement')

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def update(self):
        if not self.AuthenticatedUser():
            self.request.response.redirect("/")

        portal_types = getToolByName(self.context, "portal_types")
        type_info = portal_types.getTypeInfo("agenda.SaoPauloAberta.tipoagendadoprefeito")
        new_content_item = type_info._constructInstance(self.context, time.time())
        
        SaveData(self.context, self.request, new_content_item)
        self.request.response.redirect("@@view")

    def render(self):
        pass

    def AuthenticatedUser(self):
        context = aq_inner(self.context)
        mbs = getToolByName(context, "portal_membership")
        return not mbs.isAnonymousUser()

class UpdatetElement(grok.View):
    grok.context(IAgendaDoPrefeito)
    grok.require('zope2.View')
    grok.name('updateElement')

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def update(self):
        if not self.AuthenticatedUser():
            self.request.response.redirect("/")

        if 'id' in self.request.form.keys():
            id= self.request.form['id']        
            element = self.context[id]
        
            SaveData(self.context, self.request, element)
            self.request.response.redirect("@@view")
        else:
            self.request.response.redirect("/")

    def render(self):
        pass

    def AuthenticatedUser(self):
        context = aq_inner(self.context)
        mbs = getToolByName(context, "portal_membership")
        return not mbs.isAnonymousUser()

class RemoveElement(grok.View):
    grok.context(IAgendaDoPrefeito)
    grok.require('zope2.View')
    grok.name('removeElement')

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def update(self):
        if not self.AuthenticatedUser():
            self.request.response.redirect("/")

        if 'id' in self.request.form.keys():
            id= self.request.form['id']        
            element = self.context[id]
            if not element.winner:
                uid = api.user.get_current().id
                if (uid == element.Creator()):
                    self.context.manage_delObjects([id]) 
                    catalog = getToolByName(self.context, "portal_catalog") 
                    err = catalog.refreshCatalog(clear=True)
                
        self.request.response.redirect("@@view")
        
    def render(self):
        pass 

    def AuthenticatedUser(self):
        context = aq_inner(self.context)
        mbs = getToolByName(context, "portal_membership")
        return not mbs.isAnonymousUser()

class PageMedia(object):
    def __init__(self, url = None, title = None):
        self.url = url
        self.title = title
