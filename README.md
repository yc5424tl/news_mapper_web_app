# news_mapper_web_app
Choropleth Maps of the News 

======================================== REQUIRED ===========================================

    - Python Runtime 3.6.6
    
    - Dependencies listed in requirements.txt
        - ****Windows Installation Details Below****
    
    - Environment Variables
        - 'NEWS_CLIENT_API_KEY' == API Key from <a href="www.newsapi.org">newsapi.org</a>
        - 'NEWS_MAPPER_SECRET'  == Arbitrary user defined value for the encryption key
    
============ VIRTUAL ENVIRONMENT RECOMMENDED (conda and pip used in development) ============








==================================== NOTES AND KNOWN ISSUES =================================

1. The number of results (articles) returned from querying the API has a maximum of 10,00

        -  MAXIMUM OF 40,000 RESULTS PER DAY TOTAL allowed per api key, query with intent. 

        - A maximum of 5,000 is currently hard-coded at api_mgr.query_api:
        
        <blockquote>line 44: top_range = 50</blockquote>
        
        - the top_range value has a functional range of 0-100
        
        - For a responsive top_range value, uncomment lines 39-42 (below), and comment out line 44 (above)
        
        <blockquote>
            line 39: top_range = ((article_count // 100) -1)
            line 40:
            line 41: if top_range > 100:
            line 42:    top_range = 100
        </blockquote>
        
        
2. Query types (Map the News):
    
        - Although listed, the 'headlines' option has limited capabilites, as paging through the API response is not yet in place
        - The 'all' option should be solely used currently. 



3. Delete Foo

    - Buttons to Delete Comments, Queries, and Posts are not yet functional, although visible. 








==================================== WINDOWS INSTALLATION ===================================

1. Download and Install 'Build Tools for Visual Studio 2017' from <a href="https://visualstudio.microsoft.com/downloads/">Microsoft</a>



2. Install GDAL, Fiona, Shapely, RTree, and PyProj

    - Windows lacks the C++ Libraries to install these as is
    
    - Using CONDA virtual env, the conda package manner can handle the installation out of the box:
          - i.e. "conda install gdal fiona shapely rtree pyproj pip"
          - then "pip install --user -r requirements.txt"
          
    - Using PIP:
          - Using "pip install gdal fiona..." will fail
          - Must install manually using the correct wheels for the host system
          - These wheels are currently hosted by Christoph Gohlke <a href="https://www.lfd.uci.edu/~gohlke/pythonlibs/">here</a>.
                - Be sure to get the correct wheels, matching both the python version and either 64/86 bit system. 
          - Either place wheels somewhere in the project folder, or note the (relative) path to where they are stored
          - In an active virtual env, install each individually (GDAL first) using "python -m pip install --user path\to\wheel\wheelfile.whl"
          - Install remaining dependencies using "python -m pip install --user -r requirements.txt"
          
          
3. Start App
      - Using the command line from the project root (or another location, prepending the manage.py file with the relative path), enter:
      - "python manage.py createsuperuser", follow prompts
      - "python manage.py makemigrations"
      - "python manage.py migrate"
      - "python manage.py runserver"
          
4. Visit Site:
      - Using a browser, navigate to either localhost:8000 or 127.0.0.1:8000
      
      
      
      
   
