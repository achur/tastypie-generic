tastypie-generic
================

Generic Foreign Keys and other basic tools for Django-Tastypie

---

# Installation

Run `pip install tastypie-generic` and add `tastypie_generic` to your `INSTALLED_APPS`.

# Use

## Generic Foreign Keys

Generic foreign keys can be plugged-in and used much as standard ForeignKeys, with the exception being that the __to__ field takes in a dictionary, mapping models to resources, rather than a resource

__GenericForeignKeyField(to, attribute[, **kwargs]):__

- __to__: a dictionary mapping models to resources (e.g `{ User: UserResource, Event: EventResource }`)
- __attribute__: the name of the foreign key on the model
- __**kwargs__: the standard kwargs from [fields.ForeignKey](http://django-tastypie.readthedocs.org/en/latest/fields.html#toonefield)

## User-Edit Authorization

Often, you want to have a resource that an owner-user can edit, but anyone can view.  That functionality is in `UserAuthorization`

__UserAuthorization(attribute):__

- __attribute__ the attribute of the user who can edit the resource (e.g. `created_by`).

## Example:

Imagine I'm building an app where users can follow people or events.  We keep track of a follow object which has `created_by`: the user following and `content_object`: the object followed.  It also has `notes`, just for fun.  The owner of a Follow (i.e. the User specified by `created_by`) can edit it, and anyone can view any follow.

_models.py:_

    from django.db import models
    from django.contrib.contenttypes.models import ContentType
    from django.contrib.contenttypes import generic
    from django.contrib.auth.models import User

    class Follow(models.Model):
        created_by = models.ForeignKey(User, related_name="follows")
        content_type = models.ForeignKey(ContentType, related_name="follows")
        object_id = models.PositiveIntegerField()
        content_object = generic.GenericForeignKey('content_type', 'object_id')
        notes = models.TextField()

_api/resources.py:_

    from tastypie import fields
    from tastypie.constants import ALL, ALL_WITH_RELATIONS
    from tastypie.resources import Resource, ModelResource
    from ..models import Follow
    from tastypie_generic.authorization import UserAuthorization
    from tastypie_generic.fields import GenericForeignKeyField
    from django.contrib.auth.models import User
    from myapp.models import Event
    from myapp.api.resources import UserResource, EventResource

    class FollowResource(ModelResource):

        created_by = fields.ForeignKey(UserResource, 'created_by')
        content_object = GenericForeignKeyField({
            User: UserResource,
            Event: EventResource,
        }, 'content_object')

        def obj_create(self, bundle, request, **kwargs):
            return super(FollowResource, self).obj_create(bundle, request, created_by=request.user)
        def obj_update(self, bundle, request, **kwargs):
            return super(FollowResource, self).obj_update(bundle, request, created_by=request.user)

        class Meta:
            queryset = Follow.objects.all().select_related()
            allowed_methods = ['get', 'put', 'post', 'delete']
            excludes = ['object_id']
            authorization = UserAuthorization('created_by')
