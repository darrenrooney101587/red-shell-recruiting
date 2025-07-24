from django import forms


class RequestAccessForm(forms.Form):
    """Form for requesting site access."""

    first_name = forms.CharField(max_length=100, label="First Name")
    last_name = forms.CharField(max_length=100, label="Last Name")
    email = forms.EmailField(label="Email")
    reason = forms.CharField(widget=forms.Textarea, label="Reason for Access")
    manager = forms.CharField(max_length=100, label="Manager")
