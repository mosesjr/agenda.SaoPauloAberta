#coding: utf-8
import re
from five import grok
from datetime import datetime, timedelta
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName

from z3c.form import group, field
from z3c.form.interfaces import IObjectFactory
from zope import schema
from zope.interface import invariant, Invalid, Interface
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.schema.fieldproperty import FieldProperty
from zope.interface import implements
from zope.component import adapts
from zope.security import checkPermission

from Acquisition import aq_parent

from plone import api
from plone.dexterity.content import Item
from plone.directives import dexterity, form
from plone.app.textfield import RichText
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
from plone.namedfile.field import NamedImage, NamedFile
from plone.namedfile.field import NamedBlobImage, NamedBlobFile
from plone.namedfile.interfaces import IImageScaleTraversable
from Products.ATContentTypes.lib.calendarsupport import CalendarSupportMixin
#from zope.schema import Object as DictRow

from agenda.SaoPauloAberta import MessageFactory as _
from portal.SaoPauloAberta.utils import *

class ITipoAgendaDoPrefeito(form.Schema, IImageScaleTraversable):
    """
    AgendaDoPrefeito Type
    """
    start = schema.Datetime(
            title=_(u"field_start"),
        required=True,
        default=datetime.today())
        
    end = schema.Datetime(
        title=_(u"field_end"),
        required=True,
        default=datetime.today())
        
    form.widget(contents = WysiwygFieldWidget)
    contents = schema.Text(
        title=_(u"field_contents"),
        required=False)
  
#location
    place = schema.TextLine(
        title=_(u"field_place"),
        required=False)
    
    address = schema.TextLine(
        title=_(u"field_address"),
        required=False)
        
    city = schema.TextLine(
        title=_(u"field_city"),
        default=_(u"São Paulo"),
        required=False)
    
    state =  schema.Choice(
            title=_(u"field_state"),
            default=UFS[0],
            values=UFS,
            required=False)
    
#organization
    organizer = schema.TextLine(
        title=_(u"field_organizer"),
        required=False)
    
    telephone = schema.TextLine(
        title=_(u"field_telephone"),
        required=False)
        
    link = schema.TextLine(
        title=_(u"field_link"),
        required=False)
        
    media1name = schema.TextLine(
        title=_(u"field_media_name"),
        required=False)
        
    media1URI = schema.TextLine(
        title=_(u"field_media_URI"),
        required=False)

    media2name = schema.TextLine(
        title=_(u"field_media_name"),
        required=False)
        
    media2URI = schema.TextLine(
        title=_(u"field_media_URI"),
        required=False)
	
    media3name = schema.TextLine(
        title=_(u"field_media_name"),
        required=False)
        
    media3URI = schema.TextLine(
        title=_(u"field_media_URI"),
        required=False)

    media4name = schema.TextLine(
        title=_(u"field_media_name"),
        required=False)
        
    media4URI = schema.TextLine(
        title=_(u"field_media_URI"),
        required=False)
	
    media5name = schema.TextLine(
        title=_(u"field_media_name"),
        required=False)
        
    media5URI = schema.TextLine(
        title=_(u"field_media_URI"),
        required=False)

    winner = schema.Bool( 
        title=_(u"field_winner"),
        required=False)

    fullDescription = schema.Text(
        title=_(u"field_full_description"),
        required=False)

    zoomLevel = schema.TextLine(
        title=_(u"field_zoom_level"),
        required=False)

    mapCenter = schema.TextLine(
        title=_(u"field_map_center"),
        required=False)

    frontPage = schema.TextLine(
        title=_(u"field_front_page"),
        required=False)

    state = schema.TextLine(
        title=_(u"field_front_page"),
        required=False)

class TipoAgendaDoPrefeito(Item):
    grok.implements(ITipoAgendaDoPrefeito)
    
    start = FieldProperty(ITipoAgendaDoPrefeito['start'])
    end = FieldProperty(ITipoAgendaDoPrefeito['end'])
    contents = FieldProperty(ITipoAgendaDoPrefeito['contents'])
    place = FieldProperty(ITipoAgendaDoPrefeito['place'])
    address = FieldProperty(ITipoAgendaDoPrefeito['address'])
    organizer = FieldProperty(ITipoAgendaDoPrefeito['organizer'])
    telephone = FieldProperty(ITipoAgendaDoPrefeito['telephone'])

    fullDescription = FieldProperty(ITipoAgendaDoPrefeito['fullDescription'])
    zoomLevel = FieldProperty(ITipoAgendaDoPrefeito['zoomLevel'])
    mapCenter = FieldProperty(ITipoAgendaDoPrefeito['mapCenter'])
    frontPage = FieldProperty(ITipoAgendaDoPrefeito['frontPage'])
    state = FieldProperty(ITipoAgendaDoPrefeito['state'])
   
    media1name = FieldProperty(ITipoAgendaDoPrefeito['media1name'])
    media1URI = FieldProperty(ITipoAgendaDoPrefeito['media1URI'])
    media2name = FieldProperty(ITipoAgendaDoPrefeito['media2name'])
    media2URI = FieldProperty(ITipoAgendaDoPrefeito['media2URI'])
    media3name = FieldProperty(ITipoAgendaDoPrefeito['media3name'])
    media3URI = FieldProperty(ITipoAgendaDoPrefeito['media3URI'])
    media4name = FieldProperty(ITipoAgendaDoPrefeito['media4name'])
    media4URI = FieldProperty(ITipoAgendaDoPrefeito['media4URI'])
    media5name = FieldProperty(ITipoAgendaDoPrefeito['media5name'])
    media5URI = FieldProperty(ITipoAgendaDoPrefeito['media5URI'])
    
    winner = FieldProperty(ITipoAgendaDoPrefeito['winner'])
   
    def __init__(self, *args, **kw):
        super(TipoAgendaDoPrefeito, self).__init__(*args, **kw)
        self.likes = []
        self.dislikes = []

    def HasLikeVotes(self):
        uid = api.user.get_current().id
        if uid in self.likes:
            return True
        return False

    def HasDislikeVotes(self):
        uid = api.user.get_current().id
        if uid in self.dislikes:
            return True
        return False

    def GetFrontPage(self, preview = True):
        element = None
        frontPage = int(self.frontPage);
        if frontPage >= 0:
            if preview:
                element = MediaElement(self.__getattribute__("media" + str(frontPage + 1) + "name"),
                                   self.__getattribute__("media" + str(frontPage + 1) + "URI")).preview()
            if not preview:
                element = MediaElement(self.__getattribute__("media" + str(frontPage + 1) + "name"),
                                   self.__getattribute__("media" + str(frontPage + 1) + "URI")).preview()
            
        return element
    
class MediaElement(object):
    def __init__(self, name = None, address = None):
	self.name = name
	self.address = address
	
    def preview(self):
	previewPrefix = "http://img.youtube.com/vi/"
	previewSuffix = "/0.jpg"
	videoId = re.search("watch\?v=(\w+)", self.address, re.I)
	if videoId is not None:
	    videoIdStr = videoId.group(1)
	    return previewPrefix + videoIdStr + previewSuffix
	return self.address

    def embeded(self):
        embeded = None
        embedPrefix = "https://www.youtube.com/embed/"
        if self.address is not None:
            videoId = re.search("watch\?v=([^/]*)", self.address, re.I)
            if videoId is not None:
                embeded = embedPrefix + videoId.group(1)
                return embeded
        return self.address

def IsReadyToPublish(context):
    ready = False
    workflow = getToolByName(context,'portal_workflow')
    status = workflow.getInfoFor(context,'review_state')
    if status == "private" and context.state == "submit" and\
       checkPermission("cmf.ReviewPortalContent", context):
        ready = True 
    return ready

def IsReadyToWin(context):
    ready = False
    workflow = getToolByName(context,'portal_workflow')
    status = workflow.getInfoFor(context,'review_state')
    if context.winner == False and status == "published" and\
       checkPermission("cmf.ReviewPortalContent", context):
        ready = True 
    return ready

def IsPublished(context):
    published = False
    workflow = getToolByName(context,'portal_workflow')
    status = workflow.getInfoFor(context,'review_state')
    if status == "published" and context.state == "submit" and\
        context.start > datetime.now():
        published = True
    return published 

class View(grok.View):
    grok.context(ITipoAgendaDoPrefeito)
    grok.require('zope2.View')
    grok.name('view')
    
    def __init__(self, context, request):
        super(View, self).__init__(context, request)
        self.context = aq_inner(context)
        self.request = request

    def update(self):
        data = self.request.form
        
        if self.IsPublished():
            self.context.allow_discussion = True
        else:
            self.context.allow_discussion = False

        self.request["disable_border"] = 1
        if self.AuthenticatedUser() and "vote" in data.keys() and\
            self.IsPublished() and\
            self.context.winner == False:
            user = api.user.get_current()
            if data["vote"] == "like":
                if user.id not in self.context.dislikes:
                        if user.id not in self.context.likes:
                            self.context.likes.append(user.id)
                        else:
                            self.context.likes.remove(user.id)
                        self.context.likes = list(set(self.context.likes))
                 
            elif data["vote"] == "dislike":
                if user.id not in self.context.likes:
                        if user.id not in self.context.dislikes:
                            self.context.dislikes.append(user.id)
                        else:
                            self.context.dislikes.remove(user.id)
                        self.context.dislikes = list(set(self.context.dislikes))
    
    def AuthenticatedUser(self):
        context = aq_inner(self.context)
        mbs = getToolByName(context, "portal_membership")
        return not mbs.isAnonymousUser()

    def GetLikes(self):
	return len(self.context.likes)
	
    def GetDislikes(self):
	return len(self.context.dislikes)
	
    def GetDate(self, context, element = None):	
        if context == 'start':
            dateContext = self.context.start
        else:
            dateContext = self.context.end        
        return dateContext
        
    def GetFormatedTime(self, context):
        if context == 'start':
            dateContext = self.context.start
        else:
            dateContext = self.context.end
        
        formatedDate = "%d:%02d" % (dateContext.hour, dateContext.minute)
        return formatedDate
        
    def ConvertMonthName(self, month):
        return GetMonthName(month)

    def GetFullDate(self, context):
        if context == 'start':
            dateContext = self.context.start
        else:
            dateContext = self.context.end
        fullDate = "%02d de %s de %d" % (dateContext.day, self.context.translate(self.ConvertFullMonthName(dateContext.month)), dateContext.year)
        return fullDate        
	
    def GetGmailEvent(self):
	return GCalEventGenerator(self.context.title, self.context.description, self.context.start, self.context.end, self.context.place)

    def ConvertFullMonthName(self, month):
        return GetFullMonthName(month)
	
    def GetMedia(self):
        media = []
        frontPage = int(self.context.frontPage);
        for i in range(5):
            if i != frontPage:
                elementUri = self.context.__getattribute__("media" + str(i+1) + "URI")
                elementName = self.context.__getattribute__("media" + str(i+1) + "name")
                if elementUri:
                    mediaEl = MediaElement(elementName, elementUri)
                    media.append(mediaEl)
        return media

    def IsReadyToPublish(self):
        return IsReadyToPublish(self.context)

    def IsReadyToWin(self):
        return IsReadyToWin(self.context)

    def IsPublished(self):
        return IsPublished(self.context)

    def IsAuthor(self):
        uid = api.user.get_current().id
        return uid == self.context.Creator()

class Publish(grok.View):
    grok.context(ITipoAgendaDoPrefeito)
    grok.require('cmf.ReviewPortalContent')
    grok.name('publish')

    def __init__(self, context, request):
        self.context = context
        self.request = request    

    def update(self):
        try: 
            if IsReadyToPublish(self.context):
                workflowTool = getToolByName(self.context, "portal_workflow")
                workflowTool.doActionFor(self.context, "publish")
            else:
                self.request.response.redirect("/")
        except:
            pass 
        self.request.response.redirect("@@view")
        
    def render(self):
        pass

class Win(grok.View):
    grok.context(ITipoAgendaDoPrefeito)
    grok.require("cmf.ReviewPortalContent")
    grok.name("win")

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def update(self):
        try:
            if IsReadyToWin(self.context): 
                self.context.winner = True
                self.context.state = u"selected"
            else:
                self.request.response.redirect("/")
        except:
            pass
        self.request.response.redirect("@@view")

    def render(self):
        pass

class VcsView(grok.View):
    grok.context(ITipoAgendaDoPrefeito)
    grok.require('zope2.View')


from DateTime import DateTime
class AgendaDoPrefeitoCalAdapter(CalendarSupportMixin):
    def __init__(self, agendaDoPrefeito):
	ap = agendaDoPrefeito	
	self.props = {}
	self.props['getId'] = ap.id
	self.props['CreationDate'] = DateTime(ap.CreationDate())
	self.props['ModificationDate'] = DateTime(ap.ModificationDate())
	self.props['UID'] = ap.UID()
	self.props['Title'] = ap.Title()
	self.props['start'] = DateTime(ap.start)
	self.props['end'] = DateTime(ap.end)
	self.props['Description'] = ap.Description()	
	if ap.place:
	    self.props['getLocation'] = ap.place.encode("utf-8")	
	if ap.organizer:
	    self.props['contact_name'] = ap.organizer.encode("utf-8")
	if ap.telephone:
	    self.props['contact_phone'] = ap.telephone.encode("utf-8")	
	self.props['event_url'] = ap.link

    
    def __getattr__(self, key):
	def myfunc():
	    value = None
	    if key in self.props:
		value = self.props[key]		
	    return value
	return myfunc

#Event View Classes
class IcsView(grok.View):
    grok.context(ITipoAgendaDoPrefeito)
    grok.require('zope2.View')
    grok.name('ics_view')

    def __init__(self, context, request):
        super(IcsView, self).__init__(context, request)
        self.context = aq_inner(context)
        self.request = request    

    def render(self):	        
        gcal = AgendaDoPrefeitoCalAdapter(self.context)
        return gcal.ics_view(self.request, self.request.response);

class VcsView(grok.View):
    grok.context(ITipoAgendaDoPrefeito)
    grok.require('zope2.View')
    grok.name('vcs_view')

    def __init__(self, context, request):
        super(VcsView, self).__init__(context, request)
        self.context = aq_inner(context)
        self.request = request    

    def render(self):
        gcal = AgendaDoPrefeitoCalAdapter(self.context)
        return gcal.vcs_view(self.request, self.request.response);

class Edit(grok.View):
    grok.context(ITipoAgendaDoPrefeito)
    grok.require('zope2.View')
    grok.name('edit')

    def __init__(self, context, request):
        self.context = aq_inner(context)
        self.request = request    

    def render(self):
            self.request.response.redirect("/")

class Sharing(grok.View):
    grok.context(ITipoAgendaDoPrefeito)
    grok.require('zope2.View')
    grok.name('sharing')

    def __init__(self, context, request):
        self.context = aq_inner(context)
        self.request = request    

    def render(self):
            self.request.response.redirect("/")
