from django import forms


class UploadForm(forms.Form):
    url = forms.URLField(label='Добавить изображение по URL', required=False)
    path = forms.ImageField(label='Добавить изображение с компьютера', required=False)

    def clean(self):
        path = self.cleaned_data.get('path')
        url = self.cleaned_data.get('url')

        if path and url:
            raise forms.ValidationError('Используйте один из двух способов загрузки')

        if not path and not url:
            raise forms.ValidationError('Воспользуйтесь одним из способов загрузки')