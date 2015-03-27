from django.db import models
from django.db.models import permalink
from django.contrib.auth.models import User
# from django.contrib.comments.models import Comment
from contacts.managers import SpecialDateManager, CompanyManager, PersonManager
from lxml import etree
import xml.etree.ElementTree as ET


class Contact(models.Model):
        """ Unique attributes of former Company model."""
        name = models.CharField('name',
                                max_length=200,
                                blank=True, null=True)
        logo = models.ImageField('photo',
                                 upload_to='contacts/contacts/',
                                 blank=True, null=True)

        """ Unique attributes of former Person model."""
        first_name = models.CharField('first name',
                                      max_length=100,
                                      blank=True, null=True)
        last_name = models.CharField('last name',
                                     max_length=200,
                                     blank=True, null=True)
        middle_name = models.CharField('middle name',
                                       max_length=200,
                                       blank=True, null=True)
        suffix = models.CharField('suffix',
                                  max_length=50,
                                  blank=True, null=True)
        title = models.CharField('title',
                                 max_length=200, blank=True)
        company = models.ForeignKey('Contact',
                                    related_name='people',
                                    blank=True,
                                    null=True,
                                    on_delete=models.SET_NULL)
        user = models.OneToOneField(User,
                                    blank=True, null=True,
                                    verbose_name='user')
        photo = models.ImageField('photo',
                                  upload_to='contacts/contacts/',
                                  blank=True, null=True)

        """ Common attributes of former Person and Company models."""
        nickname = models.CharField('nickname',
                                    max_length=50, blank=True, null=True)
        slug = models.SlugField('slug',
                                blank=True, max_length=50)
        about = models.TextField('about',
                                 blank=True)

        date_added = models.DateTimeField('date added',
                                          auto_now_add=True)
        date_modified = models.DateTimeField('date modified',
                                             auto_now=True)

        """ New attributes of combined model. """
        is_company = models.BooleanField('is company',
                                         help_text="Only used for Company",
                                         default=False)
        prefix = models.CharField('prefix',
                                  max_length=50,
                                  blank=True, null=True)

        class Meta:
                db_table = 'contacts_contacts'
                verbose_name = 'contact'
                verbose_name_plural = 'contacts'

        def create_from_xml(self, xml_string):
            contact_element = etree.XML(xml_string)
            child_list = list(contact_element)
            foreign_key_elements = {
                    'PhoneNumber': PhoneNumber,
                    'EmailAddress': EmailAddress,
                    'StreetAddress': StreetAddress,
                    'WebSite': WebSite}
            wait_till_the_end = []

            # parse all the elements except for
            # foreign key objects
            for child in child_list:
                if child.tag in foreign_key_elements:
                        wait_till_the_end.append(
                                (child,
                                 foreign_key_elements[child.tag]))
                else:
                    setattr(self, child.tag, child.text)
            # save
            self.save()
            # parse the FK objects, and pass the constructors
            # for them the contact we just saved.
            for (element, ModelClass) in wait_till_the_end:
                newInstance = ModelClass(xml=etree.tostring(element),
                                         contact=self)
                newInstance.save()
            self.save()
            return self

        def __unicode__(self):
                return self.fullname

        def simplify(self):
            result = {}  # Object()
            result.name = self.name
            result.logo = self.logo
            result.first_name = self.first_name
            result.last_name = self.last_name
            result.middle_name = self.middle_name
            result.suffix = self.suffix
            result.title = self.title
            if self.company:
                result.company = self.company.simplify()
            # No simplify() for user yet
            # result.user = self.user.simplify()
            result.photo = self.photo
            result.nickname = self.nickname
            result.slug = self.slug
            result.about = self.about
            result.date_added = self.date_added
            result.date_modified = self.date_modified
            result.is_company = self.is_company
            result.prefix = self.prefix
            result.phone_number = [child.simplify() for child in
                                   self.phone_number.all()]
            result.street_address = [address.simplify() for address in
                                     self.street_address.all()]
            result.web_site = [site.simplify() for site in self.web_site.all()]
            result.email_address = [email.simplify() for email in
                                    self.email_address.all()]
            # Just like phone_number, for street_address ,
            # email_address, web_site (or website?)
            return result

        @property
        def fullname(self):
                if self.is_company:
                        return u"%s" % self.name
                else:
                        return u"%s %s" % (self.first_name,
                                           self.last_name)

        @permalink
        def get_absolute_url(self):
                return ('contacts_contact_detail', None, {
                        'pk': self.pk})

        @permalink
        def get_update_url(self):
                return ('contacts_contact_update', None, {
                        'pk': self.pk})

        @permalink
        def get_delete_url(self):
                return ('contacts_contact_delete', None, {
                        'pk': self.pk})


class Company(Contact):
        """Company model."""
        objects = CompanyManager()

        class Meta:
                proxy = True
                ordering = ('name',)
                verbose_name = 'company'
                verbose_name_plural = 'companies'

        def __init__(self, *args, **kwargs):
                # Call Contact's super and set is_company to True
                super(Contact, self).__init__(*args, **kwargs)
                self.is_company = True

        @permalink
        def get_absolute_url(self):
                return ('contacts_company_detail', None, {
                        'pk': self.pk})

        @permalink
        def get_update_url(self):
                return ('contacts_company_update', None, {
                        'pk': self.pk})

        @permalink
        def get_delete_url(self):
                return ('contacts_company_delete', None, {
                        'pk': self.pk})


class Person(Contact):
        """Person model."""
        objects = PersonManager()

        class Meta:
                proxy = True
                ordering = ('last_name', 'first_name')
                verbose_name = 'person'
                verbose_name_plural = 'people'

        def __init__(self, *args, **kwargs):
                # Call Contact's super
                super(Contact, self).__init__(*args, **kwargs)

        @property
        def fullname(self):
                return u"%s %s %s %s" % (self.first_name,
                                         self.middle_name,
                                         self.last_name,
                                         self.suffix)

        @permalink
        def get_absolute_url(self):
                return ('contacts_person_detail', None, {
                        'pk': self.pk})

        @permalink
        def get_update_url(self):
                return ('contacts_person_update', None, {
                        'pk': self.pk})

        @permalink
        def get_delete_url(self):
                return ('contacts_person_delete', None, {
                        'pk': self.pk})


class Group(models.Model):
        """Group model."""
        name = models.CharField('name', max_length=200)
        slug = models.SlugField('slug', blank=True, max_length=50)
        about = models.TextField('about', blank=True)

        people = models.ManyToManyField(Person,
                                        verbose_name='people',
                                        blank=True,
                                        null=True)
        companies = models.ManyToManyField(Company,
                                           verbose_name='companies',
                                           blank=True, null=True)

        date_added = models.DateTimeField('date added', auto_now_add=True)
        date_modified = models.DateTimeField('date modified', auto_now=True)

        class Meta:
                db_table = 'contacts_groups'
                ordering = ('name',)
                verbose_name = 'group'
                verbose_name_plural = 'groups'

        def __unicode__(self):
                return u"%s" % self.name

        @permalink
        def get_absolute_url(self):
                return ('contacts_group_detail', None, {
                        'pk': self.pk})

        @permalink
        def get_update_url(self):
                return ('contacts_group_update', None, {
                        'pk': self.pk})

        @permalink
        def get_delete_url(self):
                return ('contacts_group_delete', None, {
                        'pk': self.pk})


class Location(models.Model):
        """Location model."""
        WEIGHT_CHOICES = [(i, i) for i in range(11)]

        name = models.CharField('name', max_length=200)
        slug = models.SlugField('slug', blank=True, max_length=50)

        is_phone = models.BooleanField('is phone',
                                       help_text="Only used for Phone",
                                       default=False)
        is_street_address = models.BooleanField(
                'is street address',
                help_text="Only used for Street Address",
                default=False)

        weight = models.IntegerField(max_length=2,
                                     choices=WEIGHT_CHOICES, default=0)

        date_added = models.DateTimeField('date added', auto_now_add=True)
        date_modified = models.DateTimeField('date modified', auto_now=True)

        def create_from_xml(self, xml_element):
                child_list = list(xml_element)
                for child in child_list:
                        setattr(self, child.tag, child.text)
                return self

        def create_xml_version(self):
                location = ET.Element("location")
                elements_dict = {
                        'name': 'str',
                        'slug': 'str',
                        'is_phone': 'bool',
                        'is_street_address': 'bool',
                        'date_added': 'date',
                        'date_modified': 'date'}
                for elementName, elementType in elements_dict.iteritems():
                        newElement = ET.SubElement(location, elementName)
                        if elementType == 'str':
                                newElement.text = getattr(self, elementName)
                        elif elementType == 'bool':
                                bool_var = getattr(self, elementName)
                                newElement.text = str(bool_var)
                        elif elementType == 'date':
                                # do something else
                                date = getattr(self, elementName)
                                date_as_string = date.strftime('%Y-%m-%d')
                                newElement.text = date_as_string
                        else:
                                print "Don't know what to do here."
                                print "unknown element type."
                                print 5/0
                ET.dump(location)
                return(ET)
                # tree = ET.ElementTree("location")

        def __unicode__(self):
                return u"%s" % (self.name)

        class Meta:
                db_table = 'contacts_locations'
                ordering = ('weight',)
                verbose_name = 'location'
                verbose_name_plural = 'locations'

        def simplify(self):
                result = {}
                result.name = self.name
                result.slug = self.slug
                result.is_phone = self.is_phone
                result.is_street_address = self.is_street_address
                result.weight = self.weight
                result.date_added = self.date_added
                result.date_modified = self.date_modified
                return result


class PhoneNumber(models.Model):
        """Phone Number model."""
        contact = models.ForeignKey(Contact, related_name='phone_number')

        phone_number = models.CharField('number',
                                        max_length=50)
        location = models.ForeignKey(
                Location,
                limit_choices_to={'is_street_address': False})

        date_added = models.DateTimeField('date added',
                                          auto_now_add=True)
        date_modified = models.DateTimeField('date modified',
                                             auto_now=True)

        def simplify(self):
                result = {}
                result.phone_number = self.phone_number
                result.location = self.location.simplify()
                result.date_added = self.date_added
                result.date_modified = self.date_modified
                return result

        def __init__(self, *args, **kwargs):
                if 'content_object' in kwargs:
                        content_object_value = kwargs['content_object']
                        del kwargs['content_object']
                elif 'xml' in kwargs:
                        xml_phone_number_element = etree.fromstring(
                                kwargs['xml'])
                        child_list = list(xml_phone_number_element)
                        for child in child_list:
                                if child.tag == "Location":
                                        location_object = Location()
                                        new_location = location_object.create_from_xml(child) # noqa
                                        new_location.save()
                                        kwargs['location'] = new_location
                                else:
                                        kwargs[child.tag] = child.text
                        del kwargs['xml']
                # Then run the normal init
                super(PhoneNumber, self).__init__(*args, **kwargs)
                if 'content_object_value' in locals():
                        self.contact = content_object_value

        def __unicode__(self):
                return u"%s (%s)" % (self.phone_number, self.location)

        class Meta:
                db_table = 'contacts_phone_numbers'
                verbose_name = 'phone number'
                verbose_name_plural = 'phone numbers'


class EmailAddress(models.Model):
        contact = models.ForeignKey(Contact, related_name='email_address')
        email_address = models.EmailField('email address')
        location = models.ForeignKey(
                Location,
                limit_choices_to={'is_street_address': False,
                                  'is_phone': False})

        date_added = models.DateTimeField('date added',
                                          auto_now_add=True)
        date_modified = models.DateTimeField('date modified',
                                             auto_now=True)

        def simplify(self):
                result = {}
                result.email_address = self.email_address
                result.date_added = self.date_added
                result.date_modified = self.date_modified
                return result

        def __init__(self, *args, **kwargs):
                # If there is a content_object in the kwarguments,
                # peel it off into
                # a variable named content_object_value
                if 'content_object' in kwargs:
                        content_object_value = kwargs['content_object']
                        del kwargs['content_object']
                elif 'xml' in kwargs:
                        xml_email_address_element = etree.fromstring(
                                kwargs['xml'])
                        child_list = list(xml_email_address_element)
                        for child in child_list:
                                if child.tag == "Location":
                                        location_object = Location()
                                        new_location = location_object.create_from_xml(child) # noqa
                                        new_location.save()
                                        kwargs['location'] = new_location
                                else:
                                        kwargs[child.tag] = child.text
                        del kwargs['xml']

                # Then run the normal init
                super(EmailAddress, self).__init__(*args, **kwargs)
                if 'content_object_value' in locals():
                        self.contact = content_object_value

        def __unicode__(self):
                return u"%s (%s)" % (self.email_address, self.location)

        class Meta:
                db_table = 'contacts_email_addresses'
                verbose_name = 'email address'
                verbose_name_plural = 'email addresses'


class InstantMessenger(models.Model):
        OTHER = 'other'
        IM_SERVICE_CHOICES = (
                ('aim', 'AIM'),
                ('msn', 'MSN'),
                ('icq', 'ICQ'),
                ('jabber', 'Jabber'),
                ('yahoo', 'Yahoo'),
                ('skype', 'Skype'),
                ('qq', 'QQ'),
                ('sametime', 'Sametime'),
                ('gadu-gadu', 'Gadu-Gadu'),
                ('google-talk', 'Google Talk'),
                (OTHER, 'Other')
        )

        contact = models.ForeignKey(Contact, related_name='instant_messenger')

        im_account = models.CharField('im account',
                                      max_length=100)
        location = models.ForeignKey(
                Location,
                limit_choices_to={
                        'is_street_address': False, 'is_phone': False})
        service = models.CharField('service',
                                   max_length=11,
                                   choices=IM_SERVICE_CHOICES,
                                   default=OTHER)

        date_added = models.DateTimeField('date added',
                                          auto_now_add=True)
        date_modified = models.DateTimeField('date modified',
                                             auto_now=True)

        def __init__(self, *args, **kwargs):
                # If there is a content_object in the kwarguments,
                # peel it off into a variable named content_object_value
                if 'content_object' in kwargs:
                        content_object_value = kwargs['content_object']
                        del kwargs['content_object']

                # Then run the normal init
                super(InstantMessenger, self).__init__(*args, **kwargs)
                if 'content_object_value' in locals():
                        self.contact = content_object_value

        def __unicode__(self):
                return u"%s (%s)" % (self.im_account, self.location)

        class Meta:
                db_table = 'contacts_instant_messengers'
                verbose_name = 'instant messenger'
                verbose_name_plural = 'instant messengers'


class WebSite(models.Model):
        contact = models.ForeignKey(Contact, related_name='web_site')

        url = models.URLField('URL')
        location = models.ForeignKey(
                Location,
                limit_choices_to={
                        'is_street_address': False, 'is_phone': False})

        date_added = models.DateTimeField('date added', auto_now_add=True)
        date_modified = models.DateTimeField('date modified', auto_now=True)

        def __init__(self, *args, **kwargs):
                # If there is a content_object in the kwarguments,
                # peel it off into a variable named content_object_value
                if 'content_object' in kwargs:
                        content_object_value = kwargs['content_object']
                        del kwargs['content_object']
                elif 'xml' in kwargs:
                        xml_website_element = etree.fromstring(kwargs['xml'])
                        child_list = list(xml_website_element)
                        for child in child_list:
                                if child.tag == "Location":
                                        location_object = Location()
                                        kwargs['location'] = location_object.create_from_xml(child)  # noqa
                                else:
                                        kwargs[child.tag] = child.text
                        del kwargs['xml']

                # Then run the normal init
                super(WebSite, self).__init__(*args, **kwargs)
                if 'content_object_value' in locals():
                        self.contact = content_object_value

        def __unicode__(self):
                return u"%s (%s)" % (self.url, self.location)

        def simplify(self):
                result = {}
                # result.contact = self.contact.simplify()
                result.url = self.url
                result.location = self.location.simplify()
                result.date_added = self.date_added
                result.date_modified = self.date_modified
                return result

        class Meta:
                db_table = 'contacts_web_sites'
                verbose_name = 'web site'
                verbose_name_plural = 'web sites'

        def get_absolute_url(self):
                return u"%s?web_site=%s" % (
                        self.content_object.get_absolute_url(), self.pk)


class StreetAddress(models.Model):
        contact = models.ForeignKey(Contact, related_name='street_address')
        street = models.TextField('street', blank=True)
        street2 = models.TextField('street2', blank=True)
        city = models.CharField('city', max_length=200, blank=True)
        province = models.CharField('province',
                                    max_length=200,
                                    blank=True)
        postal_code = models.CharField('postal code',
                                       max_length=10,
                                       blank=True)
        country = models.CharField('country',
                                   max_length=100)
        location = models.ForeignKey(Location,
                                     limit_choices_to={'is_phone': False})

        date_added = models.DateTimeField('date added',
                                          auto_now_add=True)
        date_modified = models.DateTimeField('date modified',
                                             auto_now=True)

        def __init__(self, *args, **kwargs):
                # If there is a content_object in the kwarguments,
                # peel it off into a variable named content_object_value
                if 'content_object' in kwargs:
                        content_object_value = kwargs['content_object']
                        del kwargs['content_object']
                elif 'xml' in kwargs:
                        xml_street_address_element = etree.fromstring(
                                kwargs['xml'])
                        child_list = list(xml_street_address_element)
                        for child in child_list:
                                if child.tag == "Location":
                                        location_object = Location()
                                        new_location = location_object.create_from_xml(child)  # noqa
                                        new_location.save()
                                        kwargs['location'] = new_location
                                else:
                                        kwargs[child.tag] = child.text
                        del kwargs['xml']

                # Then run the normal init
                super(StreetAddress, self).__init__(*args, **kwargs)
                if 'content_object_value' in locals():
                        self.contact = content_object_value

        def __unicode__(self):
                return u"%s (%s)" % (self.city, self.location)

        def simplify(self):
                result = {}
                result.street = self.street
                result.street2 = self.street2
                result.city = self.city
                result.province = self.province
                result.postal_code = self.postal_code
                result.country = self.country
                result.location = self.location.simplify()
                result.date_added = self.date_added
                result.date_modified = self.date_modified
                return result

        class Meta:
                db_table = 'contacts_street_addresses'
                verbose_name = 'street address'
                verbose_name_plural = 'street addresses'


class SpecialDate(models.Model):
        contact = models.ForeignKey(Contact,
                                    related_name="special_date")
        # object_id = models.IntegerField(db_index=True)
        # content_object = generic.GenericForeignKey()

        occasion = models.TextField('occasion',
                                    max_length=200)
        date = models.DateField('date')
        every_year = models.BooleanField('every year',
                                         default=True)

        date_added = models.DateTimeField('date added',
                                          auto_now_add=True)
        date_modified = models.DateTimeField('date modified',
                                             auto_now=True)

        objects = SpecialDateManager()

        def __init__(self, *args, **kwargs):
                # If there is a content_object in the kwarguments,
                # peel it off into a variable named content_object_value
                if 'content_object' in kwargs:
                        content_object_value = kwargs['content_object']
                        del kwargs['content_object']

                # Then run the normal init
                super(SpecialDate, self).__init__(*args, **kwargs)
                if 'content_object_value' in locals():
                        self.contact = content_object_value

        def __unicode__(self):
                return u"%s: %s" % (self.occasion, self.date)

        class Meta:
                db_table = 'contacts_special_dates'
                verbose_name = 'special date'
                verbose_name_plural = 'special dates'
