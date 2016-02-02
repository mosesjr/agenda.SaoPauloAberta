from five import grok
from zope.interface import Interface
from zope.viewlet.interfaces import IViewletManager

from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName

grok.templatedir("viewlets")

class INavBar(IViewletManager):
    pass

class NavBar(grok.Viewlet):
    grok.viewletmanager(INavBar)
    grok.context(Interface)
    grok.template('NavBar')
    grok.order(0)
