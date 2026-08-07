from django import forms
from .models import PayableBill, PaymentReceipt

class PayableBillForm(forms.ModelForm):
    class Meta:
        model = PayableBill
        fields = [
            'supplier', 'project', 'bill_number', 'category',
            'issue_date', 'due_date', 'amount', 'amount_paid',
            'status', 'bill_file', 'notes'
        ]
        widgets = {
            'issue_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

class PaymentReceiptForm(forms.ModelForm):
    class Meta:
        model = PaymentReceipt
        fields = ['payment_date', 'amount_paid', 'payment_method', 'receipt_file', 'notes']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
        }
