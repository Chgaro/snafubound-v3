from django import forms


class TournamentImportForm(forms.Form):
    file = forms.FileField(
        label="Archivo Excel (.xlsx)",
        help_text="Sube un archivo .xlsx generado con la plantilla oficial de Snafubound.",
    )

    def clean_file(self):
        uploaded_file = self.cleaned_data["file"]
        filename = (uploaded_file.name or "").lower()

        if not filename.endswith(".xlsx"):
            raise forms.ValidationError("Solo se permiten archivos .xlsx.")

        return uploaded_file