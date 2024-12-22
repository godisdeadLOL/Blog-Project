def update_fields(object, object_update):
    for key, value in vars(object_update).items():
        if value:
            setattr(object, key, value)
