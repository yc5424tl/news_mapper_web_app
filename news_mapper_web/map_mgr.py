
import folium
import geopandas as gpd
import numpy as np
import pandas as pd
import pycountry
import os

from datetime import datetime

settings_dir = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.dirname(settings_dir))
CHORO_MAP_ROOT = os.path.join(PROJECT_ROOT, 'news_mapper_web/media/news_mapper_web/html/')


class GeoMapManager:

    @staticmethod
    def get_country_alpha_3_code(source_country):
        country = pycountry.countries.get( alpha_2=str(source_country).upper() )
        return country.alpha_3


    def map_source(self, source_name):
        if type(source_name) is None:
            return None
        else:
            country_alpha3 = self.get_country_alpha_3_code(source_name)
            return country_alpha3


    @staticmethod
    def build_choropleth(argument, query_type, meta_data_mgr):
        world_df = gpd.read_file(meta_data_mgr.json_filename)
        choro_map = folium.Map(location=[0, 0], tiles='Mapbox Bright', zoom_start=3)
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
                             threshold_scale=threshold_scale)

        folium.TileLayer("MapQuest Open Aerial", attr="Data Attr").add_to(choro_map)
        folium.TileLayer("stamenwatercolor", attr='attr').add_to(choro_map)
        folium.TileLayer("cartodbdark_matter", attr='attr').add_to(choro_map)
        folium.TileLayer("Mapbox Control Room", attr='attr').add_to(choro_map)
        folium.LayerControl().add_to(choro_map)

        date = datetime.now()
        now = datetime.ctime(date)
        map_prefix = str(now).replace(' ', '_')
        map_prefix = map_prefix.replace(':', '-')
        # choro_map.save(str(datetime.ctime(datetime.now())).replace(' ', '_').replace(':', '-') + '_' + query_type + '_query_' + argument + '_choropleth_map.html')
        filename = map_prefix + '_' + query_type + '_query_' + argument + '_choropleth_map.html'
        choro_map.save(CHORO_MAP_ROOT + filename)
        choro_html = choro_map.get_root().render()

        if save_choro_to_file(choro_html, filename):
            return choro_map, choro_html, filename

        else:
            return None


def save_choro_to_file(choro_html, filename):
    try:
        with open(CHORO_MAP_ROOT + filename, "w") as file:
            file.write(choro_html)
        return True

    except FileNotFoundError:
        return False
