import logging

import os

from IPython.core.display import display, HTML, display_html
from ipywidgets import HTML

from .models import Article, Source, NewsQuery

import folium
import geopandas as gpd
import numpy as np
import pandas as pd
import pycountry

import jupyter

import os



from .metadata_mgr import MetadataManager
from datetime import datetime

# meta_data_mgr = MetadataManager('./static/txt/geo_data_for_news_choropleth.txt')
settings_dir = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.dirname(settings_dir))
CHORO_MAP_ROOT = os.path.join(PROJECT_ROOT, 'news_mapper_web/media/news_mapper_web/html/')


class GeoMapManager:

    @staticmethod
    def get_country_alpha_3_code(source_country):

        # source = Source.objects.get(name=source_name)
        # alpha_2_code = source.country
        country = pycountry.countries.get(alpha_2=str(source_country).upper())
        print('country: ')
        print(str(country))

        return country.alpha_3

    def map_source(self, source_name):

        if type(source_name) is None:
            # TODO log
            return None
        else:
            country_alpha3 = self.get_country_alpha_3_code(source_name)
            return country_alpha3

    @staticmethod
    def build_choropleth(argument, query_type, meta_data_mgr):

        world_df = gpd.read_file(meta_data_mgr.json_filename)
        choro_map = folium.Map(location=[0, 0], tiles='Mapbox Bright', zoom_start=4)
        articles_per_country = pd.Series(meta_data_mgr.query_data_dict)
        world_df['article_count'] = world_df['id'].map(articles_per_country)

        world_df.head()
        world_df.plot(column='article_count')

        threshold_scale = None

        if articles_per_country.values.max() <= 16:
            threshold_scale = np.linspace(articles_per_country.values.min(), articles_per_country.values.max(), 6, dtype=int).tolist()

        elif 160 >= articles_per_country.values.max() > 16:
            threshold_scale = [articles_per_country.values.min(),
                               articles_per_country.values.max() // 16,
                               articles_per_country.values.max() // 8,
                               articles_per_country.values.max() // 4,
                               articles_per_country.values.max() // 2,
                               articles_per_country.values.max()]

        elif articles_per_country.values.max() > 160:
            threshold_scale = [0, 1, 2, 5, 10, articles_per_country.values.max()]

        choro_map.choropleth(geo_data=meta_data_mgr.json_geo_data,
                             name='choropleth',
                             data=world_df,
                             columns=['id', 'article_count'],
                             key_on='feature.id',
                             fill_color='PuBuGn',
                             # YlGrBu - RdYlGn - YlOrBr - RdYlBu - PuBuGn - YlOrRd
                             # Oranges - Greens -Purples - Reds - Greys - Blues
                             # Pastel1 - Pastel2 - Spectral - Set1 - Set2 - Set3 - Dark2
                             fill_opacity=0.7,
                             line_opacity=0.2,
                             threshold_scale=threshold_scale
                             )

        folium.TileLayer("MapQuest Open Aerial", attr="Data Attr").add_to(choro_map)
        folium.TileLayer("stamenwatercolor", attr='attr').add_to(choro_map)
        folium.TileLayer("cartodbdark_matter", attr='attr').add_to(choro_map)
        folium.TileLayer("Mapbox Control Room", attr='attr').add_to(choro_map)
        folium.LayerControl().add_to(choro_map)

        date = datetime.now()
        now = datetime.ctime(date)

        map_prefix = str(now).replace(' ', '_')
        map_prefix = map_prefix.replace(':', '-')

        filename = map_prefix + '_' + query_type + '_query_' + argument + '_choropleth_map.html'
        file_path = "staticoutput_maps\\" + filename


        # choro_html = choro_map.get_root().render()
        choro_map.save(CHORO_MAP_ROOT + filename)
        choro_html = choro_map.get_root().render()
        #print(isinstance(choro_html, str))
        #print(choro_html)

        print('type(choro_map.render()) = ' + str(type(choro_map.render())))
        print('type(choro_map.render) = ' + str(type(choro_map.render)))
        print('type(choro_map) = ' + str(type(choro_map)))




        iframe = choro_map._repr_html_()
        # display(HTML(iframe))
        display_html(iframe)
        # template_html_open = "{% extends 'news_mapper_web\\base.html' %} {% block choropleth %}"
        #
        # template_html_close = "{% endblock %}"
        #
        # # choro_template_html = template_html_open + " " + choro_html + " " + template_html_close



        #
        # with open(CHORO_MAP_ROOT + filename, "w") as file:
        #     file.write(choro_html)

        # with open("test_html.html", "w") as test_file:
        #     # test_file.write(template_html_open + '\n')
        #     test_file.write(choro_html)
        #     # test_file.write(template_html_close)
        #     # test_file.close()

        # open_test_file = open("test_html.html")


        # choro_map.save(os.path.join('media', 'news_mapper_web/html'))

        # choro_html = choro_map.render()

        # new_choro = self.save_choro_to_file(argument=argument, query_type=query_type, choro_map=choro_map)

        # logging.debug(type(new_choro), 'type(new_choro) from map_mgr.build_choropleth')
        # choro_map.render()
        # date = datetime.now()
        # now = datetime.ctime(date)
        # #
        # map_prefix = str(now).replace(' ', '_')
        # map_prefix = map_prefix.replace(':', '-')
        #
        # filename = '_query_' + argument + '_at_' + map_prefix + '_choropleth_map.html'
        #
        # choro_map.save('./static/news_mapper_web/' + filename)
        # choro_map.render()

        # if not os.path.exists('E:/Alpha/Software Development Capstone - 2905-01/My Files/Projects/news_mapper_django/app/news_mapper_web/static/news_mapper_web/output_maps/'):
        #     os.mkdir('E:/Alpha/Software Development Capstone - 2905-01/My Files/Projects/news_mapper_django/app/news_mapper_web/static/news_mapper_web/output_maps/')
        # with open(os.path.join('E:/Alpha/Software Development Capstone - 2905-01/My Files/Projects/news_mapper_django/app/news_mapper_web/static/news_mapper_web/output_maps/', filename), "w+") as target_file:
        #     target_file.write(choro_map)

        # return file, filename, choro_html

        # save_choro_to_file(argument, query_type, choro_map)

        return choro_map, choro_html, filename


def save_choro_to_file(argument, query_type, choro_map):
    date = datetime.now()
    now = datetime.ctime(date)

    map_prefix = str(now).replace(' ', '_')
    map_prefix = map_prefix.replace(':', '-')

    filename = query_type + '_query_' + argument + '_at_' + map_prefix + '_choropleth_map.html'

    choro_map.save(CHORO_MAP_ROOT + filename)
    choro_map.render()
    print('type(choro_map.render()) = ' + str(type(choro_map.render())))
    print('type(choro_map.render) = ' + str(type(choro_map.render)))
    print('type(choro_map) = ' + str(type(choro_map)))

    # choro_html = choro_map.render()
    # with open('static/output_maps/' + filename, 'w+') as choro_file:
    #     choro_file.write(choro_html)

    # ui.message(str(now))
    # new_file = open('../static/output_maps/' + filename, 'w+')
    # choro_map.save('../static/output_maps/' + filename)

    return choro_map
