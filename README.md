EasyAPI
=======

EasyAPi is an add-on to Django Rest Framework that enables quickly add REST API to 
a Django application to use the app's models in from JavaScript (Angular, Backbone etc).

## Usage

TBD


## Features

###Expose model’s method (DONE)

Every Django model has methods that contain business logic. These methods would be obviously uesful to AJAX application,
because they are already tested and implemented. Since an increasingly larger part of any apps is getting implemented in Angular (JS/Dart),
most of the model method should be exposed by default . For that reason, I’d like to implement a decorator that in one line of code
exposes a method of the model.

The API should be able to use methods that returns:

 - Collections or scalar objects
 - QuerySets od models
 - List of models

The decorator should describe the type of the parameters and whether each of them is required.

###Expose model’s properties (DONE)
Create a decorator to automatically add the model’s property to the serialized form of the model.

    class MyModel(models.Model):

        extra_rest_fields = {
            'my_name': Field(),
        }

        @property
        def my_name(self):
            return self.name.title()

###Expose manager method (DONE)

Manager’s methods are used to perform operations on a sets of models. These methods could be also useful by
Angular application.


### Automatically create viewsets for all models in the application (DONE)

I'd like to be able to quickly expose the whole app in one line of code using standard serialization methods.

The following code exposes all models of two Django applications 'projects' and 'orders':

    router = AutoAppRouter('projects', 'orders')


### Automatic filtering for all fields in the model (DONE)

I'd like to support the standard filtering criteria for Django QuerySets. For example, we should be able to get all
companies form Germany with request:

    GET /api/company/?@country__name__icontains=Germany

Note: to discern filter criterias from other query string params they start with @ sign.


###Expose model’s foreign keys as Hypermedia links

By default foreign keys are exposed as ids. This is the best default strategy, however sometimes it’s useful to explore the models in hypermedia style (in Postman for example). The default serializer in EasyAPI should contin “_links” section that exposes the foreign keys similar to:

       "_links": {
            "self": { "href": "/orders" },
            "curies": [{ "name": "ea", "href": "http://example.com/docs/rels/{rel}", "templated": true }],
            "next": { "href": "/orders?page=2" },
            "ea:find": {
                "href": "/orders{?id}",
                "templated": true
            },
            "ea:admin": [{
                "href": "/admins/2",
                "title": "Fred"
            }, {
                "href": "/admins/5",
                "title": "Kate"
            }]
        },

###Embed foreign key objects into the model’s JSON (DONE)

Sometimes we need to get the embedded object inside the model. For example, when we get userprofile we want use as well. There will be a parameter “_embedded” that accepts a list of embedded objects. For example:

Request:

    GET /profiles/1/?_embed=user,address

Result:

    {
        “_embedded” : {
            “user” : {
                ...
            },
            “address” : {
                ...
            }
        }
    }

Stretch goal: embed inside embed.

Request:

    GET /profiles/1/?_embed=company_address

Result:

    {
        “_embedded” : {
            “company” : {
                “id”: 1,
        “_embedded” : {
            “address” : {
                “street”: “1, Elm St.”
                ...
            }
        }
                ...
            },
        }
    }

###Reverse relationships as sub-URL

We should be able to get reverse relation sets as sub-URL. For example is the Company has reverse relation “departments”, we should be able to get a list of departments using:

Request:

    /companies/123/departments

The result should be the same as:

    /departments/?company_id=123