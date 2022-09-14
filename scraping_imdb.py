import os
from mysql.connector import connect, Error
from bs4 import BeautifulSoup
import requests, pandas as pd

try:
    source_url = 'https://www.imdb.com/chart/toptv/?ref_=nv_tvv_250'
    response = requests.get(source_url)
    response.raise_for_status()

    imdb_doc = BeautifulSoup(response.text, 'html.parser')
    
    rank_tags = imdb_doc.find_all('td', class_='titleColumn')
     
    yor_list_tags = imdb_doc.find_all('span', class_='secondaryInfo')
    
    star_tags = imdb_doc.find_all('td', class_='ratingColumn imdbRating')
    
    rank_list = []
    title_list = []
    yor_list = []
    rating_list = []
    
    for tag in rank_tags:
        ranks = tag.text.strip().split('.')[0]
        rank_list.append(ranks)

        a = tag.text.strip().split()[1:-1]
        title = ' '.join(a) #.replace('\'','')
        title_list.append(title)

    for tag in yor_list_tags:
        release_year = tag.text.strip('()')
        yor_list.append(release_year)
        
    for tag in star_tags:
        ratings = tag.text
        rating_list.append(ratings)

    
    imdb_dict = {
        'Rank' : rank_list,
        'Title' : title_list,
        'Year of Release' : yor_list,
        'Ratings' : rating_list
    }    
    
    imdb_df = pd.DataFrame(imdb_dict)
    imdb_df.to_excel('Top 250 TV Shows.xlsx', index=False)
        
except Exception as e:
    print(e)

try:
    with connect(
        host = 'localhost',
        user = os.environ.get('SQL_USER'),
        passwd = os.environ.get('SQL_PASS'),
        database = 'imdb_250',
    ) as connection:
        #create_db_query = 'CREATE DATABASE imdb_250'
        #with connection.cursor() as cursor:
        #    cursor.execute(create_db_query)
        create_table_query = '''CREATE TABLE top250(position INT, 
            title VARCHAR(500), 
            release_year INT(15), 
            ratings FLOAT(10)
            );
           '''
        
        with connection.cursor() as cursor:
            cursor.execute(create_table_query)
                       
            for index, row in imdb_df.iterrows():
                    
                rank = rank_list[index]
                title = title_list[index]
                yor = yor_list[index]
                rating = rating_list[index]
                query = "INSERT INTO top250 VALUES(" + rank + "," + "\"" + title + "\"" + "," + "\"" + yor + "\"" + "," + rating + ")"
                print(query)
                cursor.execute(query)
                
        connection.commit()
                

except Error as e:
    print(e)
