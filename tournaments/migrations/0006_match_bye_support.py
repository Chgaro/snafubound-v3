from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tournaments", "0005_alter_match_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="match",
            name="is_bye",
            field=models.BooleanField(default=False, verbose_name="Es bye"),
        ),
        migrations.AlterField(
            model_name="match",
            name="player2_entry",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.CASCADE,
                related_name="matches_as_player2",
                to="tournaments.tournamententry",
                verbose_name="Jugador 2",
            ),
        ),
    ]