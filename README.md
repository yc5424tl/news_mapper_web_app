# Map the News

A Django based web-app where a user's query returns a choropleth map of where related news stories were published. Authenticated users can not only make searches, but also save their results, post them, and comment on their's and other's posts too. 

<br>

## PREREQUISITES


### 1. Python

* Runtime 3.6.6



### 2. Pip

* Conda may be used in conjunction with, but not as a replacement for, pip. 
* Conda is able to install GDAL, Fiona, RTree, Shapely, and PyProj using standard commands. 
* On Windows OS, pip is succesful only when installing pre-compiled wheel files which match the system architecture.  
* Regardless of which method is used, pip is still required to install several packages which are not available using Conda. 



### 3. Dependencies listed in requirements.txt

* Windows Installation Details Below
* The requirements.txt file has no versions listed next to GDAL, RTree, PyProj, Shapely, or Fiona; this is intentional.



### 4. Environment Variables

* set NEWS_CLIENT_API_KEY to the value of an API Key from [newsapi.org](https://www.newsapi.org)
* set NEWS_MAPPER_SECRET to an appropriate **secret key** value of your choosing.



### 5. Virtual Environment Recommended

* Pip Example:
  ```
  virtualenv create venv
  ```
* Conda Example:
  ```
  conda create fooEnv
  ```

<br>

## NOTES AND KNOWN ISSUES

### 1. Building Queries
     
   * MAXIMUM OF 40,000 RESULTS PER DAY TOTAL allowed per api key, query with a purpose.
        
      * The number of results (articles) returned from querying the API has a maximum of 10,000
        
        * A maximum of 5,000 is currently hard-coded at api_mgr.query_api:
          ``` 
          line 44: top_range = 50
          ```
            
        * The top_range value has a functional range of 0-100
        
        
        * For a responsive top_range value, uncomment lines 39-42 (below), and comment out line 44 (above)
          ```
          line 39: top_range = ((article_count // 100) -1)
          ```
          ```
          line 40:
          ```  
          ```
          line 41: if top_range > 100:
          ```
          ```
          line 42:    top_range = 100
          ```
    
 
### 2. Query types (Map the News)
* Although listed, the 'headlines' option has limited capabilites, as paging through the API response is not yet in place
* The 'all' option should be solely used currently. 

   
### 3. Deleting Discussion Items
* Buttons to Delete Comments, Queries, and Posts are not yet finished, and if used will crash the program!

<hr>


## INSTALLING ON WINDOWS

### 1. Download and Install 'Build Tools for Visual Studio 2017' from [Microsoft](https://visualstudio.microsoft.com/downloads/)

### 2. Install GDAL, Fiona, Shapely, RTree, and PyProj
   
   * Windows has no native C compiler for which to compile the GDAL binaries, so pre-compiled versions are needed. 
    
        * **Using CONDA virtual env**:
        
            * The conda package manner can handle the installation out of the box:
               ```
               conda install gdal fiona shapely rtree pyproj pip
               ```
                
            * Install remaining dependencies:
              ```
              pip install --user -r requirements.txt
              ```
                
           
        * **Using PIP**:
        
            * Using ```pip install gdal fiona...``` will fail
            
            
            * Must install manually using the correct wheels for the host system
            
            
            * These wheels are currently hosted by Christoph Gohlke <a href="https://www.lfd.uci.edu/~gohlke/pythonlibs/">here</a>.
            
            
                * Be sure to get the correct wheels, matching both the python version and either 64/86 bit architecture. 
                
                
            * Either place wheels somewhere in the project folder, or note the (relative) path to where they are stored
            
            
            * In an active virtual env, install each individually (GDAL first) using:
              ```
              python -m pip install --user path\to\wheel\wheelfile.whl
              ```
                
            * Install remaining dependencies using:
              ```
              python -m pip install --user -r requirements.txt
              ```
                
                
                
### 3. Start App
* Using the command line from the project root (or another location, prepending the manage.py file with the relative path), enter:

  ```
  python manage.py createsuperuser (follow prompts)
  ```  
  ```
  python manage.py makemigrations"
  ```    
  ``` 
  python manage.py migrate
  ``` 
  ```   
  python manage.py runserver
  ```            
          
          
### 4. Visit Site
* Using a browser, navigate to either **localhost:8000** or **127.0.0.1:8000**
      
      
      
      
   
