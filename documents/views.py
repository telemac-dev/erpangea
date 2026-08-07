from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Document, DocumentRevision, DocumentCategoryChoices, DocumentStatusChoices
from .forms import DocumentForm, DocumentRevisionForm

@login_required
def document_list(request):
    category_filter = request.GET.get('category', '')
    status_filter = request.GET.get('status', '')
    query = request.GET.get('q', '')

    documents = Document.objects.select_related('project', 'uploaded_by', 'approved_by').all()

    if query:
        documents = documents.filter(
            Q(title__icontains=query) |
            Q(revision__icontains=query) |
            Q(project__code__icontains=query) |
            Q(project__name__icontains=query)
        )

    if category_filter:
        documents = documents.filter(category=category_filter)

    if status_filter:
        documents = documents.filter(status=status_filter)

    categories = DocumentCategoryChoices.choices
    statuses = DocumentStatusChoices.choices

    context = {
        'documents': documents,
        'query': query,
        'category_filter': category_filter,
        'status_filter': status_filter,
        'categories': categories,
        'statuses': statuses,
    }
    return render(request, 'documents/document_list.html', context)

@login_required
def document_create(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.uploaded_by = request.user
            doc.save()
            messages.success(request, f'Documento "{doc.title}" ({doc.revision}) cadastrado com sucesso!')
            return redirect('document_detail', pk=doc.pk)
        else:
            messages.error(request, 'Erro ao cadastrar documento.')
    else:
        form = DocumentForm()

    return render(request, 'documents/document_form.html', {'form': form, 'title': 'Novo Documento Técnico'})

@login_required
def document_detail(request, pk):
    document = get_object_or_404(
        Document.objects.select_related('project', 'uploaded_by', 'approved_by')
        .prefetch_related('revisions__uploaded_by'), 
        pk=pk
    )

    revision_form = DocumentRevisionForm()

    if request.method == 'POST':
        revision_form = DocumentRevisionForm(request.POST, request.FILES)
        if revision_form.is_valid():
            rev = revision_form.save(commit=False)
            rev.document = document
            rev.uploaded_by = request.user
            rev.save()

            # Update master document revision code & file to latest
            document.revision = rev.revision_number
            document.file = rev.file
            document.status = DocumentStatusChoices.EM_REVISAO
            document.save()

            messages.success(request, f'Nova revisão {rev.revision_number} adicionada ao documento!')
            return redirect('document_detail', pk=document.pk)
        else:
            messages.error(request, 'Erro ao adicionar nova revisão.')

    context = {
        'document': document,
        'revisions': document.revisions.all(),
        'revision_form': revision_form,
    }
    return render(request, 'documents/document_detail.html', context)

@login_required
def document_edit(request, pk):
    document = get_object_or_404(Document, pk=pk)
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES, instance=document)
        if form.is_valid():
            doc = form.save()
            messages.success(request, f'Documento "{doc.title}" atualizado.')
            return redirect('document_detail', pk=doc.pk)
        else:
            messages.error(request, 'Erro ao atualizar documento.')
    else:
        form = DocumentForm(instance=document)

    return render(request, 'documents/document_form.html', {'form': form, 'document': document, 'title': f'Editar Documento {document.title}'})
