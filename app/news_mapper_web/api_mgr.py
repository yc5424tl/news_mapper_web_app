import logging
import os
from datetime import datetime

import requests
from dateutil.parser import parse
# from django.core.exceptions import ValidationError
# from django.core.validators import URLValidator
from newsapi import NewsApiClient

from .models import Article, Source

logger = logging.getLogger(__name__)

news_api_key = os.environ.get('NEWS_CLIENT_API_KEY')
api_key = os.environ.get('api_key_news')  # TODO
newsapi = NewsApiClient(api_key='daaba2aab3d54874a0a154c18715e82c')

# validate_url = URLValidator(verify_exists=True)


class QueryManager:

    def query_api(self, query_argument, query_type, start_date=None, end_date=None):

        valid_date_range = self.validate_date_range(start_date, end_date)

        if not valid_date_range:

            if query_type is 'headlines':
                return self.build_articles_list(newsapi.get_top_headlines(q=query_argument, page_size=100))  # TODO return to page_size=100

            if query_type is 'all':
                endpoint = 'https://newsapi.org/v2/everything?q=' + query_argument + '&apiKey=' + api_key
                article_count_raw = requests.get(endpoint)
                article_count = article_count_raw.json()['totalResults']
                logger.info(article_count)

                if article_count <= 100:  # 100 is max results/page.
                    return self.build_articles_list(requests.get(endpoint).json()['articles'])

                elif article_count > 100:  # Multiple calls used to page through results
                    articles = []
                    # top_range = (article_count // 100 - 1)

                    # if top_range > 98:
                    # top_range = 98  # query max articles=10000, err if page past end
                    top_range = 2

                    for i in range(1, top_range):
                        results_page = requests.get(endpoint + '&page=' + str(i))

                        try:
                            articles += results_page.json()['articles']
                            with open('api_data-' + query_argument + '-' + datetime.now().day) as text_file:
                                text_file.write(str(results_page.json()))
                        except KeyError:
                            logger.exception(KeyError, 'KeyError during writing articles.json to file (QueryManager)')
                        except UnicodeEncodeError:
                            logger.exception(UnicodeEncodeError, 'UnicodeEncodeError during writing articles.json to file (QueryManager)')
                        except AttributeError:
                            logger.exception(AttributeError, 'AttributeException during writing articles.json to file (QueryManager)')

                    return articles

            if valid_date_range and query_type is 'all':
                return self.build_articles_list(newsapi.get_everything(q=query_argument, from_parameter=start_date, to=end_date))

    def build_articles_list(self, api_query):

        articles_list = []

        for i in range(len(api_query['articles'])):
            raw_article_data = api_query['articles'][i]
            new_article_object = self.build_article_object(raw_article_data, api_query)
            articles_list.append(new_article_object)

        logger.info(str(articles_list))
        return articles_list

    @staticmethod
    def is_str(data):
        if data and type(data) is str:
            return data
        else:
            return None

    @staticmethod
    def is_src(data: str):
        if data and Source.objects.get(name=data):
            return Source.objects.get(name=data)
        else:
            return None

    @staticmethod
    def format_date(date_str):
        # from YYYY-MM-DD"T"HH:MM::SS
        try:
            return parse(date_str)  # https://stackoverflow.com/a/29161018
        except ValueError:  # 'String does not contain a date'
            return None

    def is_datetime(self, data: str):
        if data and isinstance(self.format_date(data), datetime):
            return self.format_date(data)
        else:
            return None

    # @staticmethod
    # def is_url(url):
    #     try:
    #         validate_url(url)
    #         return url
    #     except TypeError:
    #         logger.exception(TypeError, 'TypeError in QueryManager.validate_url() - probably caused by url=None')
    #         return None
    #     except ValidationError:
    #         logger.exception(ValidationError, 'ValidationError in QueryManager.validate_url()')
    #         return None

    def build_article_object(self, raw_article_data, query):

        title = self.is_str(raw_article_data['title'])
        author = self.is_str(raw_article_data['author'])
        source = self.is_src(raw_article_data['source']['name'])
        date_published = self.is_datetime(raw_article_data['publishedAt'])
        description = self.is_str(raw_article_data['description'])
        article_url = raw_article_data['url']
        if raw_article_data['urlToImage']:
            image_url = raw_article_data['urlToImage']
        else:
            image_url = None
        # article_url = self.is_url(raw_article_data['url'])
        # image_url = self.is_url(raw_article_data['urlToImage'])

        new_article = Article(
            title=title,
            author=author,
            source=source,
            date_published=date_published,
            description=description,
            article_url=article_url,
            image_url=image_url,
            query=query)

        new_article.save()

        return new_article

    def build_source_object(self, source_data):

        api_id = self.is_str(source_data['id'])
        name = self.is_str(source_data['name'])
        description = self.is_str(source_data['description'])
        url = source_data['url']
        # url = self.is_url(source_data['url'])
        category = self.is_str(source_data['category'])
        language = self.is_str(source_data['language'])
        country = self.is_str(source_data['country'])

        return Source(
            api_id=api_id,
            name=name,
            description=description,
            url=url,
            category=category,
            language=language,
            country=country
        )

    # this should probably go to an AppManager or the like
    @staticmethod
    def write_sources_json_to_file(sources_json):
        try:
            with open('sources.txt', 'a') as text_file:
                text_file.write(str(sources_json))
        except UnicodeEncodeError:
            logger.exception(UnicodeEncodeError, 'UnicodeDecodeError in QueryManager.build_sources()')
        except AttributeError:
            logger.exception(AttributeError, 'AttributeError in QueryManager.build_sources()')
        except KeyError:
            logger.exception(KeyError, 'KeyError in QueryManager.build_sources()')

    def fetch_and_build_sources(self):
        source_list = []
        sources = newsapi.get_sources()['sources']
        for source in sources:
            new_source = self.build_source_object(source)
            new_source.save()
            source_list.append(source)
        return source_list

    @staticmethod
    def validate_date_range(start_date, end_date):
        if start_date and end_date:
            pass
        return False

        # todo -- use a datetime object to validate inputs
        # todo -- should be in YYYY-MM-DD format
