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
newsapi = NewsApiClient(api_key=news_api_key)

# validate_url = URLValidator(verify_exists=True)


class QueryManager:

    def query_api(self, query_argument, query_type, start_date=None, end_date=None):

        valid_date_range = self.validate_date_range(start_date, end_date)

        if valid_date_range is False:
            if query_type == 'headlines':
                return self.build_articles_list(newsapi.get_top_headlines(q=query_argument, page_size=100))  # TODO return to page_size=100

            if query_type == 'all':

                endpoint = 'https://newsapi.org/v2/everything?q=' + query_argument + '&apiKey=' + 'daaba2aab3d54874a0a154c18715e82c'
                article_count_raw = requests.get(endpoint)
                article_count = article_count_raw.json()['totalResults']
                logger.info(article_count)

                if article_count <= 100:  # 100 is max results/page.
                    return self.build_articles_list(requests.get(endpoint).json()['articles'])

                elif article_count > 100:  # Multiple calls used to page through results
                    articles = []
                    # top_range = (article_count // 100 - 1)
                    #
                    # if top_range > 98:
                    #     top_range = 98  #  query max articles=10000, err if page past end
                    top_range = 2

                    for i in range(1, top_range):
                        results_page = requests.get(endpoint + '&page=' + str(i))

                        try:
                            articles += results_page.json()['articles']
                            file_name = 'api_data-' + query_argument + '_' + query_type + '-' + datetime.now().strftime('%Y%m%d-%H%M%S') + '.json'
                            with open(file_name, 'w+') as text_file:
                                text_file.write(str(results_page.json()))
                        except KeyError:
                            logger.exception(KeyError, 'KeyError during writing articles.json to file (QueryManager)')
                        except UnicodeEncodeError:
                            logger.exception(UnicodeEncodeError, 'UnicodeEncodeError during writing articles.json to file (QueryManager)')
                        except AttributeError:
                            logger.exception(AttributeError, 'AttributeException during writing articles.json to file (QueryManager)')
                        except TypeError:
                            logger.exception(TypeError, 'TypeError while ')

                    return articles

            if valid_date_range and query_type is 'all':
                return self.build_articles_list(newsapi.get_everything(q=query_argument, from_parameter=start_date, to=end_date))

    def build_articles_list(self, api_query):

        articles_list = []

        for i in range(len(api_query['articles'])):
            raw_article_data = api_query['articles'][i]
            try:
                new_article_object = self.build_article_object(raw_article_data, api_query)
                if new_article_object:
                    articles_list.append(new_article_object)
            except Source.DoesNotExist:
                logger.exception(Source.DoesNotExist, 'api_mgr.build_articles_list')
        logger.info(str(articles_list))
        return articles_list

    @staticmethod
    def is_str(data):
        if data and isinstance(data, str):
            return data
        else:
            return None

    @staticmethod
    def is_src(source_name):
        # print('is_src(data), data = ' + source_name)
        # if data and (Source.objects.get(name=data)):
        #     return Source.objects.get(name=data)
        # else:
        #     return None

        if source_name:
            try:
                source = Source.objects.get(_name=source_name)
                # print('is_src: ' + str(source.name))
                return source
            except (AttributeError, Source.DoesNotExist):
                return False

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
        source = self.is_src(raw_article_data['source']['name'])
        date_published = self.is_datetime(raw_article_data['publishedAt'])
        article_url = raw_article_data['url']


        if raw_article_data['urlToImage'] is not None:
            image_url = raw_article_data['urlToImage']
        else:
            image_url = None

        try:
            description = self.is_str(raw_article_data['description'])
        except UnicodeDecodeError:
            description = 'Unavailable'

        try:
            title = self.is_str(raw_article_data['title'])
        except UnicodeDecodeError:
            title = 'Unavailable'

        try:
            author = self.is_str(raw_article_data['author'])
            if author is None:
                author = 'Unknown'
        except UnicodeDecodeError:
            author = 'Unavailable'

            print(str(source))
            print(str(date_published))
            print(str(description))
            print(str(title))
            print(str(author))
            print(str(article_url))

        if source is not False:
            new_article = Article(
                _title=title,
                _author=author,
                _source=source,
                _date_published=date_published,
                _description=description,
                _article_url=article_url,
                _image_url=image_url,
                _query=query)
            new_article.save()
            return new_article

        else:
            return False

    def build_source_object(self, source_data):

        print('source data = ' + str(source_data))

        url = source_data['url']
        print('url = ' + str(url))
        country  = self.is_str(source_data['country'])
        print('country = ' + str(country))
        api_id   = self.is_str(source_data['id'])
        category = self.is_str(source_data['category'])
        language = self.is_str(source_data['language'])

        try:
            name = self.is_str(source_data['name'])
        except UnicodeDecodeError:
            name = self.is_str(source_data['id'])

        try:
            description = self.is_str(source_data['description'])
        except UnicodeDecodeError:
            description = 'Unavailable'

        if name:
            print(name)

            return Source(
                _api_id=api_id,
                _name=name,
                _description=description,
                _url=url,
                _category=category,
                _language=language,
                _country=country
            )

        else:
            print('NO NAME')
            return False

    # this should probably go to an AppManager or the like
    @staticmethod
    def write_sources_json_to_file(sources_json):
        try:
            with open('sources.json', 'a') as json_file:
                json_file.write(str(sources_json))
        except UnicodeEncodeError:
            logger.exception(UnicodeEncodeError, 'UnicodeDecodeError in QueryManager.build_sources()')
        except AttributeError:
            logger.exception(AttributeError, 'AttributeError in QueryManager.build_sources()')
        except KeyError:
            logger.exception(KeyError, 'KeyError in QueryManager.build_sources()')

    def fetch_and_build_sources(self):
        source_list = []
        sources = newsapi.get_sources()['sources']
        source_count = 0
        for source in sources:
            source_count += 1
            print('source count: ' + str(source_count))
            new_source = self.build_source_object(source)
            if new_source:
                new_source.save()
                print('new_source: ' + str(new_source.name))
                source_list.append(new_source)
        return source_list

    @staticmethod
    def validate_date_range(_start_date, _end_date):
        # if start_date and end_date:
        #     pass
        return False

        # todo -- use a datetime object to validate inputs
        # todo -- should be in YYYY-MM-DD format
