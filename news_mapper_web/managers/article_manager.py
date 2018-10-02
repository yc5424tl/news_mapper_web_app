from django.db import models
from app.news_mapper_web import api_mgr as QueryMgr

qm = QueryMgr.QueryManager
#
# class ArticleManager(models.Model):
#     def build_article_object(self, article_data):
#         title = qm.is_str(article_data['title'])
