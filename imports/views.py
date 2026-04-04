from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

from .forms import TournamentImportForm
from .services import (
    TournamentImportError,
    TournamentWorkbookImporter,
    TournamentWorkbookValidator,
)


@staff_member_required
def tournament_import_view(request):
    form = TournamentImportForm()
    success_message = None
    validation_result = None
    import_result = None
    import_error = None

    if request.method == "POST":
        form = TournamentImportForm(request.POST, request.FILES)

        if form.is_valid():
            uploaded_file = form.cleaned_data["file"]

            try:
                validation_result = TournamentWorkbookValidator(uploaded_file).run()
                import_result = TournamentWorkbookImporter(validation_result).run()
                success_message = (
                    f"Importación completada correctamente: {uploaded_file.name}."
                )
                form = TournamentImportForm()
            except TournamentImportError as exc:
                import_error = str(exc)

    context = {
        "form": form,
        "success_message": success_message,
        "validation_result": validation_result,
        "import_result": import_result,
        "import_error": import_error,
    }
    return render(request, "imports/tournament_import.html", context)