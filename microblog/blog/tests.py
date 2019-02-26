from django.test import TestCase, Client


# Create your tests here.

# index のアクセス可否テスト
class BlogTestCase(TestCase):

    # 下準備
    def setUp(self):
        self.c = Client()

    def test_index_access(self):

        # cに入っているレスポンスの内容をresponseに入れる
        response = self.c.get('/')

        # assertEqualメソッドは引数1と２を比較する
        # statu_code == 200 -> OK
        # statu_code == 302 -> Redirect
        # statu_code == 404 -> Not Found
        # statu_code == 500 -> Server Error
        self.assertEqual(response.status_code, 200)


# api動作確認
# class ApiTestClass(TestCase):
#
#     def setUp(self):
#         self.c = Client()
#
#     def test_api_access(self):

