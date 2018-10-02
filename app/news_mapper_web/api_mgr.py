
import logging
import os
import requests

from datetime import datetime
from dateutil.parser import parse
from newsapi import NewsApiClient
from .models import Article, Source

logger = logging.getLogger(__name__)

news_api_key = os.environ.get('NEWS_CLIENT_API_KEY')
api_key = os.environ.get('api_key_news')  # TODO
newsapi = NewsApiClient(api_key=news_api_key)


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
                    # top_range = ((article_count // 100) - 1)

                    # if top_range > 100:
                    #     top_range = 100  #  query max articles=10000, err if page past end

                    top_range = 10 # for development, uncomment above for production -- allow users to choose from a range? aka sliding-scale

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
        if source_name:
            try:
                source = Source.objects.get(_name=source_name)
                return source
            except (AttributeError, Source.DoesNotExist):
                return False


    @staticmethod
    def format_date(date_str): # from YYYY-MM-DD"T"HH:MM::SS
        try:
            return parse(date_str)  # https://stackoverflow.com/a/29161018
        except ValueError:  # 'String does not contain a date'
            return None


    def is_datetime(self, data: str):
        if data and isinstance(self.format_date(data), datetime):
            return self.format_date(data)
        else:
            return None


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

        if source is not False:
            new_article = Article(
                _article_url=article_url,
                _author=author,
                _date_published=date_published,
                _description=description,
                _image_url=image_url,
                _query=query,
                _source=source,
                _title=title)

            new_article.save()
            return new_article

        else:
            return False


    def build_source_object(self, source_data):
        url = source_data['url']
        country  = self.is_str(source_data['country'])
        api_id   = self.is_str(source_data['id'])
        category = self.is_str(source_data['category'])
        language = self.is_str(source_data['language'])

        if country == 'zh':     # China is categorized differently between PyCountry and News_API, this bridges the two
            country = 'cn'

        try:
            name = self.is_str(source_data['name'])
        except UnicodeDecodeError:
            name = self.is_str(source_data['id'])

        try:
            description = self.is_str(source_data['description'])
        except UnicodeDecodeError:
            description = 'Unavailable'

        if name:
            return Source(
                _api_id=api_id,
                _category=category,
                _country=country,
                _description=description,
                _language=language,
                _name=name,
                _url=url)

        else:
            return False


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

        for source in sources:
            new_source = self.build_source_object(source)
            if new_source:
                new_source.save()
                source_list.append(new_source)

        return source_list

    @staticmethod
    def validate_date_range(_start_date, _end_date):

        return False

        # todo -- use a datetime object to validate inputs
        # todo -- should be in YYYY-MM-DD format
