from django.contrib import admin
# from django.contrib.contenttypes import generic

# from django.contrib.comments.models import Comment

from contacts.models import (Company, Person, Group,
                             PhoneNumber, EmailAddress,
                             InstantMessenger, WebSite,
                             StreetAddress, SpecialDate,
                             Location)

class EmailAddressInline(admin.TabularInline):
        model = EmailAddress

class PhoneNumberInline(admin.TabularInline):
        model = PhoneNumber

class InstantMessengerInline(admin.TabularInline):
        model = InstantMessenger

class WebSiteInline(admin.TabularInline):
        model = WebSite

class StreetAddressInline(admin.StackedInline):
        model = StreetAddress

class SpecialDateInline(admin.StackedInline):
        model = SpecialDate

# class CommentInline(admin.StackedInline):
#         model = Comment

class CompanyAdmin(admin.ModelAdmin):
        inlines = [
                PhoneNumberInline,
                EmailAddressInline,
                InstantMessengerInline,
                WebSiteInline,
                StreetAddressInline,
                SpecialDateInline
                # CommentInline,
        ]

        list_display = ('name',)
        search_fields = ['^name',]
        prepopulated_fields = {'slug': ('name',)}

class PersonAdmin(admin.ModelAdmin):
        inlines = [
                PhoneNumberInline,
                EmailAddressInline,
                InstantMessengerInline,
                WebSiteInline,
                StreetAddressInline,
                SpecialDateInline
                # CommentInline,
        ]

        list_display_links = ('first_name', 'last_name',)
        list_display = ('first_name', 'last_name', 'company',)
        list_filter = ('company',)
        ordering = ('last_name', 'first_name')
        search_fields = ['^first_name', '^last_name', '^company__name']
        prepopulated_fields = {'slug': ('first_name', 'last_name')}

class GroupAdmin(admin.ModelAdmin):
        list_display_links = ('name',)
        list_display = ('name', 'date_modified')
        ordering = ('-date_modified', 'name',)
        search_fields = ['^name', '^about',]
        prepopulated_fields = {'slug': ('name',)}

class LocationAdmin(admin.ModelAdmin):
        list_display_links = ('name',)
        list_display = ('name', 'date_modified')
        ordering = ('weight', 'name')
        search_fields = ['^name',]
        prepopulated_fields = {'slug': ('name',)}

        fieldsets = (
                (None, {
                        'fields': (('name', 'slug',),)
                }),
                ('Advanced options', {
                        'fields': (('is_phone', 'is_street_address'),)
                })
        )

admin.site.register(Company, CompanyAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Location, LocationAdmin)
