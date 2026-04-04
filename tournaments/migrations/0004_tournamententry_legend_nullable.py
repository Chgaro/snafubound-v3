from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0002_set"),
        ("tournaments", "0003_alter_tournament_set"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tournamententry",
            name="legend",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="tournament_entries",
                to="catalog.legend",
                verbose_name="Leyenda",
            ),
        ),
    ]