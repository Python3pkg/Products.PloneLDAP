from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PloneLDAP.property import LDAPPropertySheet

class UserPropertiesMixin:
    """Implement Products.PluggableAuthService.interfaces.plugins.IPropertiesPlugin
    and Products.PlonePAS.interfaces.plugtins.IMutablePropertiesPlugin
    """
    security = ClassSecurityInfo()

    security.declarePrivate('getPropertiesForUser')
    def getPropertiesForUser(self, user, request=None):
        """ Fullfill PropertiesPlugin requirements """
        return LDAPPropertySheet(self.id, user)


    security.declarePrivate('setPropertiesForUser')
    def setPropertiesForUser(self, user, propertysheet):
        """Set the properties of a user or group based on the contents of a
        property sheet. Needed for IMutablePropertiesPlugin.

       This is probably unused code: PlonePAS uses IMutablePropertySheet
       instead.
        """
        acl = self._getLDAPUserFolder()

        if acl is None:
            return

        unmangled_userid = self._demangle(user.getId())
        if unmangled_userid is None:
            return

        ldap_user = acl.getUserById(unmangled_userid)

        if ldap_user is None:
            return

        schemaproperties = dict([(x['public_name'], x['ldap_name']) \
                for x in acl.getSchemaConfig().values() if x['public_name']])
        multivaluedprops = [x['public_name'] for x in acl.getSchemaConfig().values() \
               if x['multivalued']]

        changes={}
        for (key,value) in propertysheet.propertyItems():
            if key in schemaproperties and key!=acl._rdnattr:
                if key in multivaluedprops:
                    changes[key] = [x.strip() for x in value.split(';')]
                else:
                    changes[key] = [value.strip()]
                    changes[key] = [value.strip()]

        acl._delegate.modify(ldap_user.dn, changes)

    def deleteUser(self, user_id):
        # XXX PlonePAS also specifies a deleteUser method
        raise NotImplemented


InitializeClass(UserPropertiesMixin)
