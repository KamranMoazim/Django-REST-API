from django.core.exceptions import ValidationError


def validate_file_size(file):
    max_size_kb = 500
    # print(file.size)
    if file.size > max_size_kb*1024:
        raise ValidationError(f"Image Size cannot be bigger than {max_size_kb}-KB!")
