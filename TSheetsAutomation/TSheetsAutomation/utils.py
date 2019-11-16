import logging

from django.db.models.fields.related import ForeignKey
from Timesheets.models import TSheetsUser, JobCode
from jobdiva.models import Job, Company, Candidate


def create_model_from_dict(model, fields, id="id"):
    app = model._meta.app_label
    if app == "Timesheets":
        id_postfix = "_id"
    elif app == "jobdiva":
        id_postfix = "ID"

    def filter_unused_fields(model, fields):
        captured_fields = []
        for field in model._meta.get_fields():
            if type(field) == ForeignKey:
                captured_fields.append(field.name + id_postfix)
            else:
                captured_fields.append(field.name)
        for discard in [field for field in fields if field not in captured_fields]:
            fields.pop(discard)
        return fields

    def map_ids_to_models(model, fields, id):
        id_field_to_model = {
            "jobcode_id": JobCode,
            "user_id": TSheetsUser,
            "created_by_user_id": TSheetsUser,
            "JOBID": Job,
            "CANDIDATEID": Candidate,
            "COMPANYID": Company,
        }
        foreign_fields = dict(
            filter(
                lambda elem: elem[0] not in (id_postfix, id) and elem[0].endswith(id_postfix),
                fields.items(),
            )
        )
        for foreign_key_field, foreign_key_id in foreign_fields.items():
            fields.pop(foreign_key_field)
            if foreign_key_id:
                foreign_model = id_field_to_model[foreign_key_field]
                fields[
                    f"{id_postfix}".join(foreign_key_field.split(id_postfix)[:-1])
                ] = foreign_model.objects.get(pk=foreign_key_id)
        return fields

    fields = filter_unused_fields(model, fields)
    fields = map_ids_to_models(model, fields, id)
    _id = fields.pop(id)

    logging.getLogger("model_creator").info(
        f"Creating a {model._meta.object_name} model with fields: {fields}"
    )
    obj, _ = model.objects.update_or_create(defaults=fields, **{id: _id})
    return obj
