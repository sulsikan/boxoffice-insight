from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("regional_boxoffice", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="regionalboxoffice",
            options={
                "verbose_name": "지역별 점유율",
                "verbose_name_plural": "지역별 점유율",
            },
        ),
    ]
