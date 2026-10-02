from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Contact, ContactTag

class SubordinateContactInline(admin.TabularInline):
    model = Contact
    fk_name = 'parent'
    extra = 0
    fields = ('address_type', 'name', 'job_title', 'email', 'phone', 'is_active')
    verbose_name = _("Contato Subordinado / Endereço")
    verbose_name_plural = _("Contatos Subordinados e Endereços")

@admin.register(ContactTag)
class ContactTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color')
    search_fields = ('name',)

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    inlines = (SubordinateContactInline,)
    list_display = (
        'complete_name',
        'contact_type',
        'doc_type',
        'formatted_doc_number',
        'city',
        'state',
        'email',
        'phone',
        'is_active',
        'created_at'
    )
    list_filter = ('contact_type', 'is_active', 'doc_type', 'state', 'tags')
    search_fields = ('name', 'trade_name', 'doc_number', 'email', 'city', 'phone')
    ordering = ('name',)
    actions = ['archive_selected', 'unarchive_selected']

    @admin.action(description=_("Arquivar contatos selecionados"))
    def archive_selected(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f"{count} contatos arquivados com sucesso.")

    @admin.action(description=_("Desarquivar contatos selecionados"))
    def unarchive_selected(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f"{count} contatos desarquivados com sucesso.")
