from http import HTTPStatus

import pytest
from django.db.utils import IntegrityError

from http import HTTPStatus


check_name_and_slug_patterns = (
    (
        {
            'name': 'a' * 256 + 'simbols',
            'slug': 'longname'
        },
        ((
            'Проверьте, что при обработке POST-запроса к `{url}` проверяется '
            'длина поля `name`: название произведения не '
            'должно быть длиннее 256 символов.'
        ),)
    ),
    (
        {
            'name': 'longslug',
            'slug': 'l' * 50 + 'simbols'
        },
        ((
            'Проверьте, что при обработке POST-запроса к `{url}` проверяется '
            'длина поля `slug`: его содержимое не должно быть длиннее 50 '
            'символов.'
        ),)
    ),
    (
        {
            'name': 'brokenslug',
            'slug': ':-)'
        },
        ((
            'Проверьте, что при обработке POST-запроса к `{url}` содержание '
            'поля `slug` проверяется на соответствие паттерну, указанному в '
            'спецификации: ^[-a-zA-Z0-9_]+$'
        ),)
    )
)
invalid_data_for_username_and_email_fields = [
    (
        {
            'email': ('a' * 244) + '@yamdb.fake',
            'username': 'valid-username'
        },
        ((
            'Проверьте, что при обработке {request_method}-запроса к `{url}` '
            'проверяется длина поля `email`: его содержимое не должно быть '
            'длиннее 254 символа.'
        ),)
    ),
    (
        {
            'email': 'valid-email@yamdb.fake',
            'username': ('a' * 151)
        },
        ((
            'Проверьте, что при обработке {request_method}-запроса к `{url}` '
            'проверяется длина поля `username`: его содержимое не должно быть '
            'длиннее 150 символов.'
        ),)
    ),
    (
        {
            'email': 'valid-email@yamdb.fake',
            'username': '|-|aTa|_|_|a'
        },
        ((
            'Проверьте, что при обработке {request_method}-запроса к `{url}` '
            'содержание поля `username` проверяется на соответствие '
            'паттерну, указанному в спецификации: ^[\\w.@+-]+\\Z'
        ),)
    )
]
invalid_data_for_user_patch_and_creation = (
    invalid_data_for_username_and_email_fields.copy()
)
invalid_data_for_user_patch_and_creation.extend([
    (
        {
            'email': 'valid-email@yamdb.fake',
            'username': 'validname',
            'first_name': 'toolong' + 'g' * 144
        },
        ((
            'Проверьте, что при обработке POST-запроса к `{url}` '
            'проверяется длина поля `first_name`: его содержимое не должно '
            'быть длиннее 150 символов.'
        ),)
    ),
    (
        {
            'email': 'valid-email@yamdb.fake',
            'username': 'validname',
            'last_name': 'toolong' + 'g' * 144
        },
        ((
            'Проверьте, что при обработке POST-запроса к `{url}` '
            'проверяется длина поля `last_name`: его содержимое не должно '
            'быть длиннее 150 символов.'
        ),)
    )
])


def check_pagination(url, respons_data, expected_count, post_data=None):
    expected_keys = ('count', 'next', 'previous', 'results')
    for key in expected_keys:
        assert key in respons_data, (
            f'Проверьте, что для эндпоинта `{url}` настроена '
            f'пагинация и ответ на GET-запрос содержит ключ {key}.'
        )
    assert respons_data['count'] == expected_count, (
        f'Проверьте, что для эндпоинта `{url}` настроена '
        f'пагинация. Сейчас ключ `count` содержит некорректное значение.'
    )
    assert isinstance(respons_data['results'], list), (
        f'Проверьте, что для эндпоинта `{url}` настроена '
        'пагинация. Значением ключа `results` должен быть список.'
    )
    assert len(respons_data['results']) == expected_count, (
        f'Проверьте, что для эндпоинта `{url}` настроена пагинация. Сейчас '
        'ключ `results` содержит некорректное количество элементов.'
    )
    if post_data:
        assert post_data in respons_data['results'], (
            f'Проверьте, что для эндпоинта `{url}` настроена пагинация. '
            'Значение параметра `results` отсутствует или содержит '
            'некорректную информацию о существующем объекте.'
        )


def check_permissions(client, url, data, user_role, objects,
                      expected_status):
    sufix = 'slug' if 'slug' in objects[0] else 'id'

    response = client.post(url, data=data)
    assert response.status_code == expected_status, (
        f'Проверьте, что POST-запрос {user_role} к `{url}` возвращает ответ '
        f'со статусом {expected_status}.'
    )
    response = client.patch(f'{url}{objects[0][sufix]}/', data=data)
    assert response.status_code == expected_status, (
        f'Проверьте, что PATCH-запрос {user_role} к `{url}<{sufix}>/` '
        f'возвращает ответ со статусом {expected_status}.'
    )
    response = client.delete(f'{url}{objects[0][sufix]}/')
    assert response.status_code == expected_status, (
        f'Проверьте, что DELETE-запрос {user_role} к `{url}<{sufix}>/` '
        f'возвращает ответ со статусом {expected_status}'
    )


def create_single_review(client, title_id, text, score):
    data = {'text': text, 'score': score}
    response = client.post(
        f'/api/v1/titles/{title_id}/reviews/', data=data
    )
    assert response.status_code == HTTPStatus.CREATED, (
        'Если POST-запрос авторизованного пользователя к '
        '`/api/v1/titles/{title_id}/reviews/` содержит корректные данные - '
        'должен вернуться ответ со статусом 201.'
    )
    return response


def create_single_comment(client, title_id, review_id, text):
    data = {'text': text}
    response = client.post(
        f'/api/v1/titles/{title_id}/reviews/{review_id}/comments/',
        data=data
    )
    assert response.status_code == HTTPStatus.CREATED, (
        'Если POST-запрос авторизованного пользователя к '
        '`/api/v1/titles/{title_id}/reviews/{review_id}/comments/` содержит '
        'корректные данные - должен вернуться ответ со статусом 201.'
    )
    return response


def create_categories(admin_client):
    data1 = {
        'name': 'Фильм',
        'slug': 'films'
    }
    response = admin_client.post('/api/v1/categories/', data=data1)
    assert response.status_code == HTTPStatus.CREATED, (
        'Если POST-запрос администратора к `/api/v1/categories/` '
        'содержит корректные данные - должен вернуться ответ со статусом 201.'
    )
    data2 = {
        'name': 'Книги',
        'slug': 'books'
    }
    admin_client.post('/api/v1/categories/', data=data2)
    return [data1, data2]


def create_genre(admin_client):
    result = []
    data = {'name': 'Ужасы', 'slug': 'horror'}
    result.append(data)
    response = admin_client.post('/api/v1/genres/', data=data)
    assert response.status_code == HTTPStatus.CREATED, (
        'Если POST-запрос администратора к `/api/v1/genres/` содержит '
        'корректные данные - должен вернуться ответ со статусом 201.'
    )
    data = {'name': 'Комедия', 'slug': 'comedy'}
    result.append(data)
    admin_client.post('/api/v1/genres/', data=data)
    data = {'name': 'Драма', 'slug': 'drama'}
    result.append(data)
    admin_client.post('/api/v1/genres/', data=data)
    return result


def create_titles(admin_client):
    genres = create_genre(admin_client)
    categories = create_categories(admin_client)
    result = []
    data = {
        'name': 'Терминатор',
        'year': 1984,
        'genre': [genres[0]['slug'], genres[1]['slug']],
        'category': categories[0]['slug'],
        'description': 'I`ll be back'
    }
    response = admin_client.post('/api/v1/titles/', data=data)
    assert response.status_code == HTTPStatus.CREATED, (
        'Если POST-запрос администратора к `/api/v1/titles/` содержит '
        'корректные данные - должен вернуться ответ со статусом 201.'
    )
    data['id'] = response.json()['id']
    result.append(data)
    data = {
        'name': 'Крепкий орешек',
        'year': 1988,
        'genre': [genres[2]['slug']],
        'category': categories[1]['slug'],
        'description': 'Yippie ki yay...'
    }
    response = admin_client.post('/api/v1/titles/', data=data)
    data['id'] = response.json()['id']
    result.append(data)
    return result, categories, genres


def create_reviews(admin_client, authors_map):
    titles, _, _ = create_titles(admin_client)
    result = []
    text = 'review number {}'
    for idx, (user, user_client) in enumerate(authors_map.items(), 1):
        response = create_single_review(
            user_client, titles[0]['id'], text.format(idx), 5
        )
        result.append(
            {
                'id': response.json()['id'],
                'author': user.username,
                'text': text.format(idx),
                'score': 5
            }
        )
    return result, titles


def create_comments(admin_client, authors_map):
    reviews, titles = create_reviews(admin_client, authors_map)
    text = 'comment number {}'
    result = []
    for idx, (user, user_client) in enumerate(authors_map.items(), 1):
        response = create_single_comment(
            user_client, titles[0]['id'], reviews[0]['id'], text.format(idx)
        )
        result.append(
            {
                'id': response.json()['id'],
                'author': user.username,
                'text': text.format(idx),
            }
        )
    return result, reviews, titles


def check_fields(obj_type, url_pattern, obj, expected_data, detail=False):
    obj_types = {
        'comment': 'комментария(ев) к отзыву',
        'review': 'отзыва(ов)'
    }
    results_in_msg = ' в ключе `results`'
    if detail:
        results_in_msg = ''
    for field in expected_data:
        assert obj.get(field) == expected_data[field], (
            f'Проверьте, что ответ на GET-запрос к `{url_pattern}` содержит '
            f'данные {obj_types[obj_type]}{results_in_msg}. Поле '
            f'`{field}` не найдено или содержит некорректные данные.'
        )
    assert obj.get('pub_date'), (
        f'Проверьте, что ответ на GET-запрос к `{url_pattern}` содержит '
        f'данные {obj_types[obj_type]}{results_in_msg}. Поле `pub_date` не '
        'найдено.'
    )
    assert isinstance(obj.get('id'), int), (
        f'Проверьте, что ответ на GET-запрос к `{url_pattern}` содержит '
        f'данные {obj_types[obj_type]}{results_in_msg}. Поле `id` не '
        'найдено или не является целым числом.'
    )



@pytest.mark.django_db(transaction=True)
class Test05ReviewAPI:

    TITLE_DETAIL_URL_TEMPLATE = '/api/v1/titles/{title_id}/'
    REVIEWS_URL_TEMPLATE = '/api/v1/titles/{title_id}/reviews/'
    REVIEW_DETAIL_URL_TEMPLATE = (
        '/api/v1/titles/{title_id}/reviews/{review_id}/'
    )

    def test_01_review_not_auth(self, client, admin_client, admin, user_client,
                                user, moderator_client, moderator):
        author_map = {
            admin: admin_client,
            user: user_client,
            moderator: moderator_client
        }
        reviews, titles = create_reviews(admin_client, author_map)
        new_data = {'text': 'new_text', 'score': 7}

        response = client.get(
            self.REVIEWS_URL_TEMPLATE.format(title_id=titles[0]['id'])
        )
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт `{self.REVIEWS_URL_TEMPLATE}` не найден, проверьте '
            'настройки в *urls.py*.'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что GET-запрос неавторизованного пользователя к '
            f'`{self.REVIEWS_URL_TEMPLATE}` возвращает ответ со статусом 200.'
        )

        response = client.post(
            self.REVIEWS_URL_TEMPLATE.format(title_id=titles[0]['id']),
            data=new_data
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Проверьте, что POST-запрос неавторизованного пользователя к '
            f'`{self.REVIEWS_URL_TEMPLATE}` возвращает ответ со статусом 401.'
        )

        response = client.patch(
            self.REVIEW_DETAIL_URL_TEMPLATE.format(
                title_id=titles[0]['id'], review_id=reviews[1]['id']
            ),
            data=new_data
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Проверьте, что PATCH-запрос неавторизованного пользователя к '
            f'`{self.REVIEW_DETAIL_URL_TEMPLATE}` возвращает ответ со '
            'статусом 401.'
        )

        response = client.delete(
            self.REVIEW_DETAIL_URL_TEMPLATE.format(
                title_id=titles[0]['id'], review_id=reviews[1]['id']
            )
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Проверьте, что DELETE-запрос неавторизованного пользователя к '
            f'`{self.REVIEW_DETAIL_URL_TEMPLATE}` возвращает ответ со '
            'статусом 401.'
        )

    def test_02_review_post(self, admin_client, user_client,
                            moderator_client, admin):
        titles, _, _ = create_titles(admin_client)
        title_0_reviews_count = 0
        first_title_reviews_url = self.REVIEWS_URL_TEMPLATE.format(
            title_id=titles[0]['id']
        )
        second_title_reviews_url = self.REVIEWS_URL_TEMPLATE.format(
            title_id=titles[1]['id']
        )

        data = {}
        response = user_client.post(first_title_reviews_url, data=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Если POST-запрос авторизованного пользователя к '
            f'`{self.REVIEWS_URL_TEMPLATE}` содержит некорректные данные - '
            'должен вернуться ответ со статусом 400.'
        )

        post_data = {
            'text': 'Неочень',
            'score': 5
        }
        create_single_review(
            admin_client,
            titles[0]['id'],
            post_data['text'],
            post_data['score']
        )
        title_0_reviews_count += 1

        data = {
            'text': 'Шляпа',
            'score': 1
        }
        response = admin_client.post(first_title_reviews_url, data=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Проверьте, что при попытке пользователя создать второй отзыв на '
            'одно и то же произведение POST-запрос к '
            f'`{self.REVIEWS_URL_TEMPLATE}` вернёт ответ со статусом 400.'
        )

        try:
            from reviews.models import Review, Title
        except Exception as e:
            assert False, (
                'Не удалось импортировать модели из приложения reviews. '
                f'Ошибка: {e}'
            )
        title = Title.objects.get(pk=titles[0]['id'])
        review = None
        try:
            review = Review.objects.create(
                text='Текст второго отзыва',
                score='5',
                author=admin,
                title=title
            )
        except IntegrityError:
            pass

        assert review is None, (
            'Проверьте, что на уровне модели запрещено повторное '
            'создание отзыва на произведение от имени пользователя, отзыв '
            'которого уже существует.'
        )

        response = admin_client.put(first_title_reviews_url, data=data)
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED, (
            'Проверьте, что PUT-запрос авторизованного пользователя к '
            f'`{self.REVIEWS_URL_TEMPLATE}` возвращает ответ со статусом 405.'
        )

        create_single_review(user_client, titles[0]['id'], 'Ну такое', 3)
        title_0_reviews_count += 1
        response = create_single_review(
            moderator_client, titles[0]['id'], 'Ниже среднего', 4
        )
        title_0_reviews_count += 1

        assert type(response.json().get('id')) == int, (
            'Проверьте, что POST-запрос авторизованного пользователя к '
            f'`{self.REVIEWS_URL_TEMPLATE}` возвращает данные созданного '
            'объекта. Сейчас поля `id` нет в ответе или его значение не '
            'является целым числом.'
        )

        data = {'text': 'На один раз', 'score': 4}
        response = user_client.post(
            self.REVIEWS_URL_TEMPLATE.format(title_id='999'), data=data
        )
        assert response.status_code == HTTPStatus.NOT_FOUND, (
            'Проверьте, что POST-запрос авторизованного пользователя к '
            f'`{self.REVIEWS_URL_TEMPLATE}` для несуществующего произведения '
            'возвращает ответ со статусом 404.'
        )

        data = {'text': 'Супер!', 'score': 11}
        response = user_client.post(second_title_reviews_url, data=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Если в POST-запросе авторизованного пользователя к '
            f'`{self.REVIEWS_URL_TEMPLATE}` передана оценка выше 10 баллов - '
            'должен вернуться ответ со статусом 400.'
        )

        data = {'text': 'Ужас!', 'score': 0}
        response = user_client.post(first_title_reviews_url, data=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Если в POST-запросе авторизованного пользователя к '
            f'`{self.REVIEWS_URL_TEMPLATE}` передана оценка ниже 1 балла - '
            'должен вернуться ответ со статусом 400.'
        )

        response = user_client.get(first_title_reviews_url)
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что GET-запрос авторизованного пользователя к '
            f'`{self.REVIEWS_URL_TEMPLATE}` возвращает ответ со статусом 200.'
        )
        data = response.json()
        check_pagination(first_title_reviews_url, data, title_0_reviews_count)

        expected_data = {
            'text': post_data['text'],
            'score': post_data['score'],
            'author': admin.username
        }
        review = None
        for value in data['results']:
            if value.get('text') == post_data['text']:
                review = value
        assert review, (
            'Проверьте, что при GET-запросе к '
            f'`{self.REVIEWS_URL_TEMPLATE}` возвращается вся информация '
            'об отзывах. В ответе на запрос не обнаружен текст отзыва.'
        )
        check_fields(
            'review', self.REVIEWS_URL_TEMPLATE, review, expected_data
        )

        response = admin_client.get(
            self.TITLE_DETAIL_URL_TEMPLATE.format(title_id=titles[0]['id'])
        )
        data = response.json()
        assert data.get('rating') == 4, (
            'Проверьте, что произведениям присваивается рейтинг, '
            'равный средной оценке оставленных отзывов. '
            'Поле `rating` не найдено в ответе на GET-запрос к '
            f'`{self.TITLE_DETAIL_URL_TEMPLATE}` или содержит некорректное '
            'значение.'
        )

    def test_03_review_detail_get(self, client, admin_client, admin, user,
                                  user_client, moderator, moderator_client):
        author_map = {
            admin: admin_client,
            user: user_client,
            moderator: moderator_client
        }
        reviews, titles = create_reviews(admin_client, author_map)

        response = client.get(
            self.REVIEW_DETAIL_URL_TEMPLATE.format(
                title_id=titles[0]['id'], review_id=reviews[0]['id']
            )
        )
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт `{self.REVIEW_DETAIL_URL_TEMPLATE}` не найден. '
            'Проверьте настройки в *urls.py*.'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что GET-запрос неавторизованного пользователя к '
            f'`{self.REVIEW_DETAIL_URL_TEMPLATE}` возвращает ответ со '
            'статусом 200.'
        )
        review = response.json()

        expected_data = {
            key: value for key, value in reviews[0].items() if key != 'id'
        }
        check_fields(
            'review', self.REVIEW_DETAIL_URL_TEMPLATE, review, expected_data,
            detail=True
        )

    def test_04_review_detail_user(self, admin_client, admin, user,
                                   user_client, moderator, moderator_client):
        author_map = {
            admin: admin_client,
            user: user_client,
            moderator: moderator_client
        }
        reviews, titles = create_reviews(admin_client, author_map)
        new_data = {
            'text': 'Top score',
            'score': 10
        }
        user_review_url = self.REVIEW_DETAIL_URL_TEMPLATE.format(
            title_id=titles[0]['id'], review_id=reviews[1]['id']
        )

        response = user_client.patch(user_review_url, data=new_data)
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что PATCH-запрос пользователя с ролью `user` к его '
            f'собственному отзыву через `{self.REVIEW_DETAIL_URL_TEMPLATE}` '
            'возвращает ответ со статусом 200.'
        )
        data = response.json()
        assert data.get('text') == new_data['text'], (
            'Проверьте, что ответ на успешный PATCH-запрос к '
            f'`{self.REVIEW_DETAIL_URL_TEMPLATE}` содержит обновлённые данные '
            'отзыва. Сейчас поле `text` не найдено или содержит некорректные '
            'данные.'
        )

        response = user_client.get(user_review_url)
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что GET-запрос авторизованного пользователя к '
            f'{self.REVIEW_DETAIL_URL_TEMPLATE} возвращает ответ со статусом '
            '200.'
        )
        data = response.json()
        assert_msg_template = (
            'Проверьте, что если в PATCH-запросе авторизованного пользователя '
            'к его собственному отзыву через `{url_template}` содержится поле '
            '`{field}` - то это поле отзыва будет изменено.'
        )
        assert data.get('text') == new_data['text'], (
            assert_msg_template.format(
                url_template=self.REVIEW_DETAIL_URL_TEMPLATE, field='text'
            )
        )
        assert data.get('score') == new_data['score'], (
            assert_msg_template.format(
                url_template=self.REVIEW_DETAIL_URL_TEMPLATE, field='score'
            )
        )

        moderator_review_url = self.REVIEW_DETAIL_URL_TEMPLATE.format(
            title_id=titles[0]['id'], review_id=reviews[2]['id']
        )
        response = user_client.patch(moderator_review_url, data=new_data)
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Проверьте, что PATCH-запрос пользователя с ролью `user` к '
            f'чужому отзыву через `{self.REVIEW_DETAIL_URL_TEMPLATE}` '
            'возвращает ответ со статусом 403.'
        )

        response = user_client.delete(user_review_url)
        assert response.status_code == HTTPStatus.NO_CONTENT, (
            'Проверьте, что DELETE-запрос пользователя с ролью `user` к его '
            f'собственному отзыву через `{self.REVIEW_DETAIL_URL_TEMPLATE}` '
            'возвращает ответ со статусом 204.'
        )
        response = user_client.get(
            self.REVIEWS_URL_TEMPLATE.format(title_id=titles[0]['id'])
        )
        test_data = response.json()['results']
        assert len(test_data) == len(reviews) - 1, (
            'Проверьте, что DELETE-запрос пользователя с ролью `user` к его '
            f'собственному отзыву через `{self.REVIEW_DETAIL_URL_TEMPLATE}` '
            'удаляет отзыв.'
        )

        response = user_client.delete(moderator_review_url)
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Проверьте, что DELETE-запрос пользователя с ролью `user` к '
            f'чужому отзыву через `{self.REVIEW_DETAIL_URL_TEMPLATE}` '
            'возвращает ответ со статусом 403.'
        )

    def test_05_reviews_detail_moderator_and_admin(self, admin_client, admin,
                                                   user_client, user,
                                                   moderator_client,
                                                   moderator):
        author_map = {
            admin: admin_client,
            user: user_client,
            moderator: moderator_client
        }
        reviews, titles = create_reviews(admin_client, author_map)
        new_data = {
            'text': 'Top score',
            'score': 10
        }

        for idx, (client, role) in enumerate((
                (moderator_client, 'модератора'),
                (admin_client, 'администратора')
        ), 1):
            response = client.patch(
                self.REVIEW_DETAIL_URL_TEMPLATE.format(
                    title_id=titles[0]['id'], review_id=reviews[idx]['id']
                ),
                data=new_data
            )
            assert response.status_code == HTTPStatus.OK, (
                f'Проверьте, что PATCH-запросе {role} к  чужому отзыву через '
                f'`{self.REVIEW_DETAIL_URL_TEMPLATE}` возвращает ответ со '
                'статусом 200.'
            )

            response = client.delete(
                self.REVIEW_DETAIL_URL_TEMPLATE.format(
                    title_id=titles[0]['id'], review_id=reviews[idx]['id']
                )
            )
            assert response.status_code == HTTPStatus.NO_CONTENT, (
                f'Проверьте, что DELETE-запрос {role} к чужому отзыву через '
                f'`{self.REVIEW_DETAIL_URL_TEMPLATE}` возвращает ответ со '
                'статусом 204.'
            )
            response = client.get(
                self.REVIEWS_URL_TEMPLATE.format(title_id=titles[0]['id'])
            )
            test_data = response.json()['results']
            assert len(test_data) == len(reviews) - idx, (
                f'Проверьте, что DELETE-запрос {role} к чужому отзыву через '
                f'`{self.REVIEW_DETAIL_URL_TEMPLATE}` удаляет отзыв.'
            )

    def test_06_reviews_detail_put_not_allowed(
            self, admin_client, admin, user_client, user, moderator_client,
            moderator):
        author_map = {
            admin: admin_client,
            user: user_client,
            moderator: moderator_client
        }
        reviews, titles = create_reviews(admin_client, author_map)
        review = reviews[0]
        review['text'] = 'Новвый текст отзыва.'
        response = admin_client.put(
            self.REVIEW_DETAIL_URL_TEMPLATE.format(
                title_id=titles[0]['id'], review_id=reviews[0]['id']
            ),
            data=review
        )
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED, (
            f'Проверьте, что PUT-запрос к `{self.REVIEW_DETAIL_URL_TEMPLATE} '
            'не предусмотрен и возвращает статус 405.'
        )
