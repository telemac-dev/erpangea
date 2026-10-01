from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import ProjectDocument, DocumentRevision, RevisionStatusEnum
from .forms import DocumentCreateForm, RevisionUploadForm

def document_vault(request):
    documents = ProjectDocument.objects.all().prefetch_related('revisions')
    doc_list = []
    for doc in documents:
        latest_rev = doc.revisions.order_by('-data_upload').first()
        doc_list.append({
            'document': doc,
            'latest_revision': latest_rev
        })
    return render(request, 'edms_docs/vault.html', {'doc_list': doc_list})

def create_document_modal(request):
    if request.method == 'POST':
        form = DocumentCreateForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save()
            # Cria a revisão inicial R00
            DocumentRevision.objects.create(
                documento=doc,
                arquivo=request.FILES['arquivo'],
                enviado_por=request.user,
                status=RevisionStatusEnum.EM_ELABORACAO,
                notas_alteracao=form.cleaned_data.get('notas_alteracao') or "Emissão inicial"
            )
            response = HttpResponse('<div class="alert alert-success m-3">Documento cadastrado com sucesso!</div>')
            response['HX-Refresh'] = 'true'
            return response
    else:
        form = DocumentCreateForm()
    return render(request, 'edms_docs/partials/create_document_modal.html', {'form': form})

def upload_revision_modal(request, pk):
    doc = get_object_or_404(ProjectDocument, pk=pk)
    if request.method == 'POST':
        form = RevisionUploadForm(request.POST, request.FILES)
        if form.is_valid():
            rev = form.save(commit=False)
            rev.documento = doc
            rev.enviado_por = request.user
            rev.save() # O save auto-incrementa a revisão (R01, R02, etc.)
            response = HttpResponse('<div class="alert alert-success m-3">Nova revisão enviada com sucesso!</div>')
            response['HX-Refresh'] = 'true'
            return response
    else:
        form = RevisionUploadForm()
    return render(request, 'edms_docs/partials/upload_revision_modal.html', {'doc': doc, 'form': form})

def revision_history_modal(request, pk):
    doc = get_object_or_404(ProjectDocument, pk=pk)
    revisions = doc.revisions.all().order_by('-data_upload')
    return render(request, 'edms_docs/partials/revision_history_modal.html', {
        'doc': doc,
        'revisions': revisions
    })

def approve_revision(request, pk):
    rev = get_object_or_404(DocumentRevision, pk=pk)
    if request.method == 'POST':
        rev.status = RevisionStatusEnum.APROVADO_CLIENTE
        rev.save()
        response = HttpResponse('<div class="alert alert-success m-3">Revisão aprovada!</div>')
        response['HX-Refresh'] = 'true'
        return response
    return HttpResponse(status=405)
