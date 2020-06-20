from django.shortcuts import get_object_or_404, Http404, HttpResponse, render
from django.core.files.temp import NamedTemporaryFile
from django.views import View
from django.core.files import File
from django.conf import settings
from urllib.request import urlopen, urlretrieve
from .models import ImgModel
from .forms import UploadForm
from PIL import Image, UnidentifiedImageError
import uuid
import os


def main_view(request):
    images = ImgModel.objects.all()
    context = {
        'images': images,
    }
    return render(request, 'index.html', context=context)


class UploadImage(View):

    def get(self, request):
        form = UploadForm()
        return render(request, 'upload.html', context={'form': form})

    def post(self, request):
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            path, url = form.cleaned_data["path"], form.cleaned_data["url"]
            if path:
                path.name = uuid.uuid4().hex + '.' + path.name.split('.')[-1]
                new_image = ImgModel(img=path)
                new_image.save()
            elif url:
                try:
                    image_url = urlretrieve(url)
                    im = Image.open(image_url[0])
                    img_temp = NamedTemporaryFile()
                    img_temp.write(urlopen(url).read())
                    img_temp.flush()
                    new_image = ImgModel()
                    new_image.img.save(uuid.uuid4().hex + '.' + im.format.lower(), File(img_temp))
                except UnidentifiedImageError:
                    return render(request, 'upload.html',
                                  context={'form': form, 'error': 'По указанному URL картинка не найдена'})
            result = True
            return render(request, 'upload.html', context={'form': form, 'result': result})
        return render(request, 'upload.html', context={'form': form, 'error': 'Ошибка при заполении формы'})


def image_view(request, img):
    img = get_object_or_404(ImgModel, img=img)
    err_mess = None
    if not img:
        return Http404('Изображение не найдено')
    image = Image.open(f"{settings.MEDIA_ROOT}/{img.img}").convert('RGB')
    current_width, current_height = image.size
    new_width = request.GET.get('width', None)
    new_height = request.GET.get('height', None)
    max_size = request.GET.get('size', None)
    try:
        if not new_width and new_height:
            new_height = abs(int(new_height))
            new_width = int(current_width * new_height / current_height)
        elif not new_height and new_width:
            new_width = abs(int(new_width))
            new_height = int(new_width * current_height / current_width)
        elif new_height and new_width:
            new_width, new_height = abs(int(new_width)), abs(int(new_height))
        else:
            new_height, new_width = current_height, current_width
        if max_size:
            max_size = abs(int(max_size))
    except ValueError:
        err_mess = """Все get-параметры должны являться числами 
            (отрицательные числа автоматически конвертируются в положительные)"""
        return render(request, 'image.html', context={'err_mes': err_mess})
    image = image.resize((new_width, new_height), Image.ANTIALIAS)
    tmpfile = "media/tmp.jpeg"
    image.save(tmpfile, format="jpeg")
    img_bytes = os.path.getsize(tmpfile)
    if max_size:
        if max_size < img_bytes:
            for x in range(91, 0, -5):
                image.save(tmpfile, format="jpeg", optimize=True, quality=x)
                if x == 1 or os.path.getsize(tmpfile) < max_size:
                    break
        if os.path.getsize(tmpfile) > max_size:
            err_mess = f"Не удалось сжать до {max_size}. Результат сжатия - {os.path.getsize(tmpfile)}."
    return render(request, "image.html", context={'err_mes': err_mess, 'show': True})
