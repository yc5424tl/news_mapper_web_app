from newsapi import NewsApiClient
from .models import Article, Source, NewsQuery
import os
import requests
from datetime import datetime
# import log_controller
import logging

logger = logging.getLogger(__name__)

news_api_key = os.environ.get('NEWS_CLIENT_API_KEY')
api_key = os.environ.get('api_key_news') # TODO
newsapi = NewsApiClient(api_key='daaba2aab3d54874a0a154c18715e82c')


class QueryManager:

    def query_api(self, query_argument, query_type, start_date=None, end_date=None):

        valid_date_range = self.validate_dates(start_date, end_date)

        if not valid_date_range:

            if query_type is 'headlines':
                return self.build_articles_list(newsapi.get_top_headlines(q=query_argument, page_size=100))

            if query_type is 'all':
                endpoint = 'https://newsapi.org/v2/everything?q=' + query_argument + '&apiKey=' + api_key
                article_count_raw = requests.get(endpoint)
                article_count = article_count_raw.json()['totalResults']
                logger.info(article_count)

                if article_count <= 100:  # 100 is max results per page, if the total is higher multiple calls are made to page through all results
                    return self.build_articles_list(requests.get(endpoint).json()['articles'])
                elif article_count > 100:
                    articles = []
                    top_range = (article_count // 100 - 1)
                    if top_range > 98:
                        top_range = 98  # max articles returned per query limited to 10000, paging beyond the top_range will result in an error
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
            new_article_object = self.build_article_object(raw_article_data)
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
    def is_valid_src_or_none(data):
        if data and Source.objects.get(name=data):
            return Source.objects.get(name=data)
        else:
            return None


    def build_article_object(self, raw_article_data):
        title = self.is_str(raw_article_data['title'])
        author = self.is_str(raw_article_data['author'])
        # if raw_article_data['source']['name']
        # source = Source.objects.get(name=raw_article_data['source']['name'])
        
        date_published = raw_article_data['publishedAt']
        description = raw_article_data['description']
        article_url = raw_article_data['url']
        try:
            image_url = raw_article_data['urlToImage']
        except TypeError:
            # log.log_error_message('img_url=None caused TypeError')
            image_url = None
        return Article(title, author, source, date_published, description, article_url, image_url)

    @staticmethod
    def fetch_sources():
        sources_list = []
        sources = newsapi.get_sources()

        try:
            with open('sources.txt', 'a') as text_file:
                text_file.write(str(sources))
        except UnicodeEncodeError:
            logger.exception(UnicodeEncodeError, 'UnicodeDecodeError in QueryManager.build_sources()')
        except AttributeError:
            logger.exception(AttributeError, 'AttributeError in QueryManager.build_sources()')
        except KeyError:
            logger.exception(KeyError, 'KeyError in QueryManager.build_sources()')

        for source in sources['sources']:
            api_id = source['id']
            name = source['name']
            description = source['description']
            url = source['url']
            category = source['category']
            language = source['language']
            country = source['country']
            new_source = Source(api_id, name, description, url, category, language, country)
            sources_list.append(new_source)

        return sources_list


    @staticmethod
    def build_source_object(data):


    @staticmethod
    def validate_dates(start_date, end_date):
        if start_date and end_date:
            pass
        return False

        # todo -- use a datetime object to validate inputs
        # todo -- should be in YYYY-MM-DD format
