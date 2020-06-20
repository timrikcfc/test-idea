from django.test import TestCase, Client
from .forms import UploadForm
from .models import ImgModel
from django.core.files.images import ImageFile
import uuid
from PIL import Image


class TestApp(TestCase):
    allow_database_queries = True

    def setUp(self) -> None:
        img_test = ImgModel.objects.create()
        img_test.img = ImageFile(open("resizeimg/tests/test_img.jpg", "rb"))
        img_test.img.name = "test_img.jpeg"
        img_test.save()

    def test_form_url_success(self):
        form = UploadForm(data={
            'url': "https://avatars.mds.yandex.net/get-pdb/27625/4c7ea1aa-4abf-497c-b575-2b09532fe12a/s1200"
        })

        self.assertTrue(form.is_valid())

    def test_form_url_fail(self):
        form = UploadForm(data={
            'url': "random-string"
        })

        self.assertFalse(form.is_valid())

    def test_form_empty(self):
        form = UploadForm(data={})

        self.assertFalse(form.is_valid())

    def test_pages_code_responses(self):
        self.assertEqual(Client().get('').status_code, 200)
        self.assertEqual(Client().get('/upload/').status_code, 200)

    def test_imgs_from_db(self):
        imgs = ImgModel.objects.all()
        for img in imgs:
            self.assertEqual(Client().get(f"/images/{img.img}").status_code, 200)

    def test_img_with_get_params_success(self):
        img = ImgModel.objects.all()[0]
        html = Client().get(f"/images/{img.img}?width=200&height=200").content.decode('utf-8')
        check = "alert alert-danger" in html
        self.assertFalse(check)

    def test_img_with_get_params_fail(self):
        img = ImgModel.objects.all()[0]
        html = Client().get(f"/images/{img.img}?width=not-int&height=not-int").content.decode('utf-8')
        check = "alert alert-danger" in html
        self.assertTrue(check)

    def test_img_with_get_size_fail_1(self):
        img = ImgModel.objects.all()[0]
        html = Client().get(f"/images/{img.img}?size=1").content.decode('utf-8')
        check = "alert alert-danger" in html
        self.assertTrue(check)

    def test_img_with_get_size_fail_2(self):
        img = ImgModel.objects.all()[0]
        html = Client().get(f"/images/{img.img}?size=dsadsa").content.decode('utf-8')
        check = "alert alert-danger" in html
        self.assertTrue(check)

    def test_img_with_get_size_success(self):
        img = ImgModel.objects.all()[0]
        html = Client().get(f"/images/{img.img}?size=99999999999").content.decode('utf-8')
        check = "alert alert-danger" in html
        self.assertFalse(check)