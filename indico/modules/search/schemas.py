# This file is part of Indico.
# Copyright (C) 2002 - 2020 CERN
#
# Indico is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see the
# LICENSE file for more details.

from marshmallow import post_dump

from indico.core.db.sqlalchemy.links import LinkType
from indico.core.marshmallow import mm
from indico.modules.attachments import Attachment
from indico.modules.categories import Category
from indico.modules.events import Event
from indico.modules.events.contributions import Contribution
from indico.modules.events.contributions.models.subcontributions import SubContribution
from indico.modules.events.notes.models.notes import EventNote
from indico.modules.search.base import SearchTarget
from indico.web.flask.util import url_for


class CategorySchema(mm.SQLAlchemyAutoSchema):
    class Meta:
        model = Category
        fields = ('id', 'title', 'url')

    url = mm.Function(lambda c: url_for('categories.display', category_id=c['id']))


class DetailedCategorySchema(mm.SQLAlchemyAutoSchema):
    class Meta:
        fields = ('id', 'title', 'url', 'path')

    path = mm.List(mm.Nested(CategorySchema), attribute='chain')

    @post_dump()
    def update_path(self, c, **kwargs):
        c['path'] = c['path'][:-1]
        return c


class PersonSchema(mm.Schema):
    name = mm.Function(lambda e: e.title and f'{e.title} {e.name}' or e.name)
    affiliation = mm.String()


class LocationSchema(mm.Schema):
    venue_name = mm.String()
    room_name = mm.String()
    address = mm.String()


class EventSchema(mm.SQLAlchemyAutoSchema):
    class Meta:
        model = Event
        fields = ('event_id', 'type', 'type_format', 'title', 'description', 'url', 'keywords', 'location', 'persons',
                  'category_path', 'start_dt', 'end_dt')

    event_id = mm.Int(attribute='id')
    type = mm.Function(lambda a: SearchTarget.event.name)
    type_format = mm.String(attribute='type')
    location = mm.Function(lambda event: LocationSchema().dump(event))
    persons = mm.List(mm.Nested(PersonSchema), attribute='person_links')
    category_path = mm.List(mm.Nested(CategorySchema), attribute='detailed_category_chain')
    note = mm.String()


class AttachmentSchema(mm.SQLAlchemyAutoSchema):
    class Meta:
        model = Attachment
        fields = ('attachment_id', 'type', 'type_format', 'title', 'filename', 'event_id', 'contribution_id',
                  'subcontribution_id', 'user', 'url', 'category_path', 'content', 'modified_dt')

    attachment_id = mm.Int(attribute='id')
    type = mm.Function(lambda a: SearchTarget.attachment.name)
    type_format = mm.String(attribute='type.name')
    filename = mm.String(attribute='file.filename')
    event_id = mm.Int(attribute='folder.event.id')
    contribution_id = mm.Method('_contribution_id')
    subcontribution_id = mm.Method('_subcontribution_id')
    user = mm.Nested(PersonSchema)
    category_path = mm.List(mm.Nested(CategorySchema), attribute='folder.event.detailed_category_chain')
    url = mm.String(attribute='download_url')
    content = mm.String()

    def _contribution_id(self, attachment):
        return attachment.folder.contribution_id if attachment.folder.link_type == LinkType.contribution else None

    def _subcontribution_id(self, attachment):
        return attachment.folder.subcontribution_id \
            if attachment.folder.link_type == LinkType.subcontribution else None


class ContributionSchema(mm.SQLAlchemyAutoSchema):
    class Meta:
        model = Contribution
        fields = ('contribution_id', 'type', 'type_format', 'event_id', 'title', 'description', 'location',
                  'persons', 'url', 'category_path', 'start_dt', 'end_dt')

    contribution_id = mm.Int(attribute='id')
    type = mm.Function(lambda a: SearchTarget.contribution.name)
    type_format = mm.String(attribute='type.name')
    location = mm.Function(lambda contrib: LocationSchema().dump(contrib))
    persons = mm.List(mm.Nested(PersonSchema), attribute='person_links')
    category_path = mm.List(mm.Nested(CategorySchema), attribute='event.detailed_category_chain')
    url = mm.Function(lambda contrib: url_for('contributions.display_contribution', contrib, _external=False))


class SubContributionSchema(mm.SQLAlchemyAutoSchema):
    class Meta:
        model = SubContribution
        fields = ('subcontribution_id', 'type', 'title', 'description', 'event_id', 'contribution_id', 'persons',
                  'location', 'url', 'category_path')

    subcontribution_id = mm.Int(attribute='id')
    type = mm.Function(lambda a: SearchTarget.subcontribution.name)
    event_id = mm.Int(attribute='contribution.event_id')
    persons = mm.List(mm.Nested(PersonSchema), attribute='person_links')
    location = mm.Function(lambda subc: LocationSchema().dump(subc.contribution))
    category_path = mm.List(mm.Nested(CategorySchema), attribute='event.detailed_category_chain')
    url = mm.Function(lambda subc: url_for('contributions.display_subcontribution', subc, _external=False))


class EventNoteSchema(mm.SQLAlchemyAutoSchema):
    class Meta:
        model = EventNote
        fields = ('note_id', 'type', 'content', 'event_id', 'contribution_id', 'subcontribution_id', 'url',
                  'category_path', 'created_dt')

    note_id = mm.Int(attribute='id')
    type = mm.Function(lambda a: SearchTarget.event_note.name)
    content = mm.Str(attribute='html')
    contribution_id = mm.Int(attribute='object.id')
    subcontribution_id = mm.Int()
    category_path = mm.List(mm.Nested(CategorySchema), attribute='event.detailed_category_chain')
    url = mm.Function(lambda note: url_for('event_notes.view', note, _external=False))
    # session_id = mm.Function(lambda note: note.session.id if note.session else None)
    created_dt = mm.DateTime(attribute='current_revision.created_dt', format='%Y-%m-%dT%H:%M')
