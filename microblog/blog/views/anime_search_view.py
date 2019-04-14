from django.shortcuts import render
from blog.forms import SearchForm
from blog.views import blog_option_view
import requests


# アニメ検索機能（関数ビューの知見）
def api_call(request):
    endpoint = 'http://api.moemoe.tokyo/anime/v1/master'

    # リクエストがpostであることをチェック
    if request.method == 'POST':
        # フォームデータを取得
        form = SearchForm(request.POST)
        # フォームのデータが安全かチェック
        if form.is_valid():

            # データを受け取る
            year = form.cleaned_data['year']
            cours = form.cleaned_data['cours']

            if year:
                query = str(year)
                url = endpoint + "/" + query

            else:
                form = SearchForm()
                messages = ["放送年を選択してください"]
                context = {'messages': messages, 'form': form}

                return render(request, 'blog/anime_search.html', context)

            if cours:
                query = str(cours)
                url = url + "/" + query

            response = requests.get(url)
            anime_list = response.json()

            form = SearchForm()

            page_obj = blog_option_view.paginate_queryset(request, anime_list, 10)
            context = {
                'anime_list': page_obj.object_list,
                'form': form,
                'year': year,
                'cours': cours,
                'page_obj': page_obj,
            }

            return render(request, 'blog/anime_search.html', context)

        else:
            form = SearchForm()
            messages = ["放送年を選択してください"]

            context = {'messages': messages, 'form': form}

            return render(request, 'blog/anime_search.html', context)
    else:

        # 最初にブラウザから呼び出されるときに使用するフォームクラスを指定
        form = SearchForm()

        # ページネーションバーからGETで遷移したときの処理
        # ページネーションしてきたときはクエリにyear,coursがあるのでそれを判定して分岐に入る
        if 'year' in request.GET:
            year = request.GET.get('year')
            url = endpoint + "/" + year

            cours = request.GET.get('cours')

            if cours:
                cours = request.GET.get('cours')
                url = url + "/" + cours

            response = requests.get(url)
            anime_list = response.json()
            page_obj = blog_option_view.paginate_queryset(request, anime_list, 10)

            context = {
                'anime_list': page_obj.object_list,
                'form': form,
                'year': year,
                'cours': cours,
                'page_obj': page_obj,
            }

            return render(request, 'blog/anime_search.html', context)

    # 作成されたフォームオブジェクトをコンテキストへ格納
    context = {'form': form}
    # 最初にブラウザから呼び出されたときに指定テンプレートとコンテキストで描画する
    return render(request, 'blog/anime_search.html', context)