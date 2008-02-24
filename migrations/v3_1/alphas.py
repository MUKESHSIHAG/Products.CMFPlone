from zope.component import getUtilitiesFor
from zope.interface import Interface

from plone.portlets.interfaces import IPortletType

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.migrations.migration_util import loadMigrationProfile
from Products.GenericSetup.browser.manage import ImportStepsView
from Products.GenericSetup.browser.manage import ExportStepsView

def three0_alpha1(portal):
    """3.0.6 -> 3.1alpha1
    """
    out = []

    loadMigrationProfile(portal, 'profile-Products.CMFPlone.migrations:3.0.6-3.1alpha1')

    addBrowserLayer(portal, out)
    migratePortletTypeRegistrations(portal, out)
    removeDoubleGenericSetupSteps(portal, out)

    return out


def addBrowserLayer(portal, out):
    qi=getToolByName(portal, "portal_quickinstaller")
    if not qi.isProductInstalled("plone.browserlayer"):
        qi.installProduct("plone.browserlayer", locked=True)
        out.append("Installed plone.browserlayer")


def migratePortletTypeRegistrations(portal, out):
    for name, portletType in getUtilitiesFor(IPortletType):
        if portletType.for_ is None:
            portletType.for_ = [Interface]
        elif type(portletType.for_) is not list:
            portletType.for_ = [portletType.for_]
    
    out.append("Migrated portlet types to support multiple " + \
      "portlet manager interfaces.")


def removeDoubleGenericSetupSteps(portal, out):
    """Remove all GenericSetup steps that are registered both using
    zcml and in the persistent registry from the persistent registry.
    """
    st=getToolByName(portal, "portal_setup")
    view=ImportStepsView(st, None)
    steps=[step["id"] for step in view.doubleSteps()]
    if steps:
        for step in steps:
            st._import_registry.unregisterStep(step)
        st._p_changed=True
        out.append("Removed doubly registered GenericSetup import steps: %s" %
                " ".join(steps))

    view=ExportStepsView(st, None)
    steps=[step["id"] for step in view.doubleSteps()]
    if steps:
        for step in steps:
            st._export_registry.unregisterStep(step)
        out.append("Removed doubly registered GenericSetup export steps: %s" %
                " ".join(steps))

