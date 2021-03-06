from __future__ import absolute_import
from __future__ import unicode_literals
import json
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from ...models import ProtectedCapability

__author__ = "Alan Viars"


fhir_prefix = "/protected/bluebutton/fhir/v1/"

supported_resources = [
    'Condition',
    'AllergyIntolerance',
    'Medication',
    'Observation',
    'FamilyMemberHistory',
    'Device',
    'Procedure',
    'Immunizations',
    'CarePlan',
    'DocumentReference',
]


def create_group(name="BlueButton"):

    g, created = Group.objects.get_or_create(name=name)
    if created:
        print("%s group created" % (name))
    else:
        print("%s group pre-existing. Create skipped." % (name))
    return g


def create_fhir_readonly_capability(group,
                                    fhir_resource_type,
                                    fhir_prefix=fhir_prefix,
                                    title="",
                                    description=""):
    c = None
    if not title:
        title = "My %s records." % (fhir_resource_type)

    smart_scope_string = "patient/%.read" % (fhir_resource_type)
    pr = []
    pr.append(["GET", "%s%s/" % (fhir_prefix, fhir_resource_type)])
    pr.append(["GET", "%s%s/[id]" % (fhir_prefix, fhir_resource_type)])
    pr.append(["GET", "%s%s/[id]/_history" %
               (fhir_prefix, fhir_resource_type)])
    pr.append(["GET", "%s%s/[id]/_history/[vid]" %
               (fhir_prefix, fhir_resource_type)])

    if not ProtectedCapability.objects.filter(slug=smart_scope_string).exists():
        c = ProtectedCapability.objects.create(group=group,
                                               title=title,
                                               description=description,
                                               slug=smart_scope_string,
                                               protected_resources=json.dumps(pr, indent=4))
        print("%s - %s created." % (c.slug, c.title))
    else:
        print("%s - %s skipped because it already existed." %
              (smart_scope_string, title))
    return c


class Command(BaseCommand):
    help = 'Create A started set of FHIR Protected Capapabvilities with  ReadOnly permissions.'

    def handle(self, *args, **options):
        g = create_group()
        for r in supported_resources:
            create_fhir_readonly_capability(g, r)

        print("Done. Stay classy, San Diego.")
