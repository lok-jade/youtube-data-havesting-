from googleapiclient.discovery import build
import pymongo
import psycopg2
import pandas as pd
import logging
import streamlit as st


#connect_Api_youtube
def API_Connection():
    APT_ID='AIzaSyAuBwKXD45fTlyRQNvzMyXsVYrGoQH9new'
    API_version ='v3'
    API_Name='youtube'
    Youtube =build(API_Name,API_version,developerKey=APT_ID)
    return Youtube
Connection = API_Connection()

#get channel_detals from youtube 
def Get_Channel_details(Channel_ID):
    request  = Connection.channels().list(
    part ="snippet,ContentDetails,statistics",
    id = Channel_ID
    )
    Response = request.execute()  
    for i in  Response['items']:
        Data = dict(Channel_name = i["snippet"]["title"],
                    Channel_id = i["id"],
                    subscribers = i["statistics"]["subscriberCount"],
                    views = i["statistics"]["viewCount"],
                    Totalvideos = i["statistics"]["videoCount"],
                    Channel_description = i["snippet"]["description"],
                    Playlist_ID = i["contentDetails"]["relatedPlaylists"]["uploads"])
    return Data

#getting videoid  details form youtube 
def Get_video_id(Channel_ID):
    Video_ID=[]
    Response = Connection.channels().list(id=Channel_ID,
                                          part ='contentDetails').execute()
    playlist_id=Response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    page_token = None
    while True:
        response_1 = Connection.playlistItems().list(
            part='snippet',playlistId = playlist_id,maxResults = 50,
            pageToken = page_token
        ).execute()
    
        for i in range(len(response_1['items'])):
            Video_ID.append(response_1['items'][i]['snippet']["resourceId"]["videoId"])
            page_token = response_1.get('nextPageToken')
        
        if page_token is None:
            break
    return Video_ID

#using video id getting the basic information of the video from the api
def get_video_data(video_id):
    Video_data=[]
    for video in video_id:
        request = Connection.videos().list(
            part ="snippet,contentDetails,statistics",
            id = video
        )
        response = request.execute()

        for item in response["items"]:
            data = dict(Channel_name = item['snippet']['channelTitle'],
                        Channel_Id = item['snippet']['channelId'],
                        Video_ID=item['id'],
                        Title = item['snippet'].get("title"),
                        tags=item['snippet'].get('tags'),
                        thumbnail = item['snippet']['thumbnails']['default']['url'],
                        description=item['snippet'].get('description'),
                        published_date =item['snippet']['publishedAt'],
                        duration = item['contentDetails']['duration'],
                        comment = item['statistics'].get('commentCount'),
                        view = item['statistics'].get('viewCount'),
                        likes = item['statistics'].get('likeCount'),
                        fav_count = item['statistics']['favoriteCount'],
                        definition = item['contentDetails']['definition'],
                        caption = item['contentDetails']['caption'])
            Video_data.append(data)
    return(Video_data)
#getting comment details of the gven video id 
def get_comment_data(video_id):
    try:
        
        Comment_data=[]
        for video in video_id:
                request = Connection.commentThreads().list(
                    part ="snippet",
                    videoId = video,
                    maxResults = '50'
                )
                response = request.execute()
                
                for item in response['items']:
                    data = dict(commentID =item['snippet']['topLevelComment']['id'],
                                videoID =item['snippet']['topLevelComment']['snippet']['videoId'],
                                comment_text =item['snippet']['topLevelComment']['snippet']['textDisplay'],
                                Comment_Author=item['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                                Comment_PublishedOn=item['snippet']['topLevelComment']['snippet']['publishedAt']
                            )
                    Comment_data.append(data)
                
    except:
        pass
    return Comment_data
#fetching playlist details using channelID 

def playlist_data(Channel_id):
    Playlist_data =[]
    Next_page_token = None
    while True:
        request = Connection.playlists().list(
                            part ="snippet,contentDetails",
                            channelId= Channel_id,
                            pageToken = Next_page_token
                        )
        response= request.execute()
        for item in response['items']:
            data = dict(playlist_Id = item['id'],
                        title = item['snippet']['title'],
                        channel_id = item['snippet']['channelId'],
                        Channel_name = item['snippet']['channelTitle'],
                        publishedAt=item['snippet']['publishedAt'],
                        videoCount =item['contentDetails']['itemCount'])
            
            Playlist_data.append(data)
        Next_page_token = response.get('nextPageToken')
        if Next_page_token is None:
            break
    return Playlist_data

#connection string to Connect Mongo DB
CLient =pymongo.MongoClient("mongodb+srv://Lokesh:lok0798@ database.igwc2md.mongodb.net/?retryWrites=true&w=majority&appName=database")
db=CLient['youtube_visualize']


#compiling the data from video and uploadind to mongo db
def channel_details(channel_id):
    Ch_details=Get_Channel_details(channel_id)
    pl_details=playlist_data(channel_id)
    video_id=Get_video_id(channel_id)
    video_data=get_video_data(video_id)
    comment_details =get_comment_data(video_id)
    coll1 =db["channel_details"]
    coll1.insert_one({"Channel_information":Ch_details,"playlist_information":pl_details,"video_information":video_data,"comment_information":comment_details})
    return "uploaded sucessfully"

#Uploading data from mongo db to posgres sql using data frames 

#uploading data for channel data 
def channel_into_database():
    mydb = psycopg2.connect(host='localhost',
                            user='postgres',
                            password='1234',
                            database='youtube_scrape',
                            port='5432')
    cursor=mydb.cursor()

    drop_Query = '''drop table if exists channels'''
    cursor.execute(drop_Query)
    mydb.commit()
    try:
        Create_query='''Create table if not exists channels(channel_name varchar(200),
                                                            channel_id varchar(100) primary key,
                                                            subcribers bigint,
                                                            views bigint,
                                                            total_videos int,
                                                            channel_description text,
                                                            playlist_id varchar(80))'''
        cursor.execute(Create_query)
        mydb.commit()
    except:
        print ('error')


    Ch_data=[]
    db=CLient["youtube_visualize"]
    coll1=db["channel_details"]
    for channel_data in coll1.find({},{"_id":0,"Channel_information":1}):
        Ch_data.append(channel_data['Channel_information'])
    df = pd.DataFrame(Ch_data)


    for index,row in df.iterrows():
            insert_query='''insert into channels(
                                            channel_name 		
                                            ,channel_id 			
                                            ,subcribers 			
                                            ,views 				
                                            ,total_videos 		
                                            ,channel_description 
                                            ,playlist_id) 
                                            values (%s,%s,%s,%s,%s,%s,%s)'''
            values = (row['Channel_name'],		
                    row['Channel_id'], 			
                    row['subscribers'],			
                    row['views'],				
                    row['Totalvideos'], 		
                    row['Channel_description'], 
                    row['Playlist_ID'])	
            try:
                    cursor.execute(insert_query,values)
                    mydb.commit()
            except:
                    print ('insertion error')
   


#uploading data of playlist 
def playlist_into_database():
    mydb = psycopg2.connect(host='localhost',
                                user='postgres',
                                password='1234',
                                database='youtube_scrape',
                                port='5432')
    cursor=mydb.cursor()

    drop_Query = '''drop table if exists playlists'''
    cursor.execute(drop_Query)
    mydb.commit()
    Create_query='''Create table if not exists playlists(playlist_Id varchar(200) primary key,
                                                        title text ,
                                                        channel_id varchar(100),
                                                        Channel_name varchar(100),
                                                        publishedAt timestamp,
                                                        videoCount int
                                                        )'''
    cursor.execute(Create_query)
    mydb.commit()

    PL_data=[]
    db=CLient["youtube_visualize"]
    coll1=db["channel_details"]
    for playlist_data in coll1.find({},{"_id":0,"playlist_information":1}):
        for i in range(len(playlist_data['playlist_information'])):
            PL_data.append(playlist_data['playlist_information'][i])
    df_1 = pd.DataFrame(PL_data)

    for index,row in df_1.iterrows():
            insert_query = '''INSERT INTO playlists(
                                        playlist_Id,  		
                                        title, 			
                                        channel_id, 			
                                        Channel_name, 				
                                        publishedAt, 		
                                        videoCount) 
                            VALUES (%s, %s, %s, %s, %s, %s)'''
            
            values = (row['playlist_Id'],		
                    row['title'], 			
                    row['channel_id'],			
                    row['Channel_name'],				
                    row['publishedAt'], 		
                    row['videoCount'])
        
            cursor.execute(insert_query,values)
            mydb.commit()

#uploding Video details to postgres

def video_into_database():
    mydb = psycopg2.connect(host='localhost',
                                user='postgres',
                                password='1234',
                                database='youtube_scrape',
                                port='5432')
    cursor=mydb.cursor()

    drop_Query = '''drop table if exists videos'''
    cursor.execute(drop_Query)
    mydb.commit()
    try:
        Create_query='''Create table if not exists videos(Channel_name varchar(100),
                                                        Channel_Id varchar(100),
                                                        Video_ID varchar(100) primary key,
                                                        Title  text,
                                                        tags text,
                                                        thumbnail varchar(200),
                                                        description text,
                                                        published_date timestamp,
                                                        duration interval,
                                                        comment int,
                                                        view bigint,
                                                        likes bigint,
                                                        fav_count int,
                                                        definition varchar(10),
                                                        caption varchar(20))'''
        cursor.execute(Create_query)
        mydb.commit()
    except:
        print ('error')
    #dataframe conversion 
    vid_data=[]
    db=CLient["youtube_visualize"]
    coll1=db["channel_details"]
    for video_data in coll1.find({},{"_id":0,"video_information":1}):
        for i in range(len(video_data['video_information'])):
            vid_data.append(video_data['video_information'][i])
    df_2 = pd.DataFrame(vid_data)

    #postgres db insertion 
    for index, row in df_2.iterrows():
            insert_query = '''INSERT INTO videos(
                                            Channel_name,  		
                                            Channel_Id, 			
                                            Video_ID, 			
                                            Title, 				
                                            thumbnail, 		
                                            description,
                                            published_date,
                                            duration,
                                            comment,
                                            view,
                                            likes,
                                            fav_count,
                                            definition,
                                            caption) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
            
            values = (
                row['Channel_name'],		
                row['Channel_Id'], 			
                row['Video_ID'],			
                row['Title'],				
                row['thumbnail'], 		
                row['description'],
                row['published_date'], 			
                row['duration'],			
                row['comment'],				
                row['view'], 		
                row['likes'],
                row['fav_count'],
                row['definition'],
                row['caption']
            )
            try:
                cursor.execute(insert_query,values)
                mydb.commit()
            except:
                print('inertion error')
    cursor.close()
    mydb.close()

#uploading commentdata to postgres

def comment_into_database():
    mydb = psycopg2.connect(host='localhost',
                                    user='postgres',
                                    password='1234',
                                    database='youtube_scrape',
                                    port='5432')
    cursor=mydb.cursor()
    drop_Query = '''drop table if exists comments'''
    cursor.execute(drop_Query)
    mydb.commit()
    try:
        Create_query='''Create table if not exists comments(
                                    commentID varchar(100),
                                    videoID varchar(100),
                                    comment_text text,
                                    Comment_Author varchar(100),
                                    Comment_PublishedOn timestamp
        )'''
        cursor.execute(Create_query)
        mydb.commit()
    except:
        print ('error')
    #dataframe conversion 
    comment_data=[]
    db=CLient["youtube_visualize"]
    coll1=db["channel_details"]
    for com_data in coll1.find({},{"_id":0,"comment_information":1}):
        for i in range(len(com_data['comment_information'])):
            comment_data.append(com_data['comment_information'][i])
    df_3 = pd.DataFrame(comment_data)
    for index, row in df_3.iterrows():
                insert_query = '''INSERT INTO comments(
                                                commentID,  		
                                                videoID, 			
                                                comment_text, 			
                                                Comment_Author, 				
                                                Comment_PublishedOn	
                                                ) 
                                VALUES (%s, %s, %s, %s, %s)'''

                values = (
                    row['commentID'],		
                    row['videoID'], 			
                    row['comment_text'],			
                    row['Comment_Author'],				
                    row['Comment_PublishedOn']
                )

                cursor.execute(insert_query,values)
                mydb.commit()

    cursor.close()
    mydb.close()
#Compiling all the data and inserting into the database 
def tables():
    channel_into_database()
    playlist_into_database()
    video_into_database()
    comment_into_database()
    return ('table created')

#Displaying the data of the tables 

def show_channel_det():
    Ch_data=[]
    db=CLient["youtube_visualize"]
    coll1=db["channel_details"]
    for channel_data in coll1.find({},{"_id":0,"Channel_information":1}):
        Ch_data.append(channel_data['Channel_information'])
    df = st.dataframe(Ch_data)
    return df
def show_playlist_det():
    PL_data=[]
    db=CLient["youtube_visualize"]
    coll1=db["channel_details"]
    for playlist_data in coll1.find({},{"_id":0,"playlist_information":1}):
        for i in range(len(playlist_data['playlist_information'])):
            PL_data.append(playlist_data['playlist_information'][i])
    df_1 = st.dataframe(PL_data)
    return df_1
def show_video_det():
    vid_data=[]
    db=CLient["youtube_visualize"]
    coll1=db["channel_details"]
    for video_data in coll1.find({},{"_id":0,"video_information":1}):
        for i in range(len(video_data['video_information'])):
            vid_data.append(video_data['video_information'][i])
    df_2 = st.dataframe(vid_data)
    return df_2
def show_comment_det():
    comment_data=[]
    coll1=db["channel_details"]
    for com_data in coll1.find({},{"_id":0,"comment_information":1}):
        for i in range(len(com_data['comment_information'])):
            comment_data.append(com_data['comment_information'][i])
    df_3 = st.dataframe(comment_data)
    return df_3


#streamlit code 
#steamlit part

with st.sidebar:
    st.title(":red[Youtube Datahouse warehousing]")
    st.header("key take away")
    st.caption("python scripting")
    st.caption("data collection")
    st.caption ("mongo and postgres sql")


Channel_id=st.text_input("enter the Channel ID")
if st.button("Collect and store data"):
    ch_ids=[]
    db=CLient["youtube_visualize"]
    coll1=db["channel_details"]
    for ch_data in coll1.find({},{"_id":0,"channel_information":1}):
        ch_ids.append(ch_data["channel_information"]["Channel_Id"])

    if Channel_id in ch_ids:
        st.success("Channel Details of the given channel id already exists")

    else:
        insert=channel_details(Channel_id)
        st.success(insert,icon="✅")


if st.button("migrate to sql"):
    Tables = tables()
    st.success('Migrated sucessfully!', icon="✅")

show_table = st.radio("SELECT THE TABLE FOR VIEW",("Channel","playlist","videos","comments"))

if show_table == "Channel":
    show_channel_det()
elif show_table == "playlist":
    show_playlist_det()
elif show_table == "videos":
    show_video_det()
elif show_table == "comments":
    show_comment_det()
mydb = psycopg2.connect(host='localhost',
                                    user='postgres',
                                    password='1234',
                                    database='youtube_scrape',
                                    port='5432')
cursor=mydb.cursor()
question= st.selectbox("Selelct your question",("1.What are the names of all the videos and their corresponding channels",
                                                 "2.channels have the most number of videos and count of the video",
                                                "3.the top 10 most viewed videos",
                                                "4.comments were made on each video, and their corresponding video names",
                                                "5.videos have the highest number of likes, and their corresponding channel names",
                                                "6.total number of likes and dislikes for each video",
                                                "7.total number of views for each channel, and their  corresponding channel names",
                                                "8.names of all the channels that have published videos in the year 2022",
                                                "9.average duration of all videos in each channel",
                                                "10.videos have the highest number of comments"))

if question=="1.What are the names of all the videos and their corresponding channels":
    query1='''select title as videos,channel_name as channelname from videos'''
    cursor.execute(query1)
    mydb.commit()
    t1=cursor.fetchall()
    df=pd.DataFrame(t1,columns=["video title","channel name"])
    st.write(df)

elif question=="2.channels have the most number of videos and count of the video":
    query2='''select channel_name as channelname,total_videos as no_videos from channels 
                order by total_videos desc'''
    cursor.execute(query2)
    mydb.commit()
    t2=cursor.fetchall()
    df2=pd.DataFrame(t2,columns=["channel name","No of videos"])
    st.write(df2)

elif question=="3.the top 10 most viewed videos":
    query3='''select view as views,channel_name as channelname,title as videotitle from videos 
                where view is not null order by views desc limit 10'''
    cursor.execute(query3)
    mydb.commit()
    t3=cursor.fetchall()
    df3=pd.DataFrame(t3,columns=["views","channel name","videotitle"])
    st.write(df3)

elif question=="4.comments were made on each video, and their corresponding video names":
    query4='''select comment as no_comments,title as videotitle from videos where comment is not null'''
    cursor.execute(query4)
    mydb.commit()
    t4=cursor.fetchall()
    df4=pd.DataFrame(t4,columns=["no of comments","videotitle"])
    st.write(df4)

elif question=="5.videos have the highest number of likes, and their corresponding channel names":
    query5='''select title as videotitle,channel_name as channelname,likes as likecount
                from videos where likes is not null order by likes desc'''
    cursor.execute(query5)
    mydb.commit()
    t5=cursor.fetchall()
    df5=pd.DataFrame(t5,columns=["videotitle","channelname","likecount"])
    st.write(df5)

elif question=="6.total number of likes and dislikes for each video":
    query6='''select likes as likecount,title as videotitle from videos'''
    cursor.execute(query6)
    mydb.commit()
    t6=cursor.fetchall()
    df6=pd.DataFrame(t6,columns=["likecount","videotitle"])
    st.write(df6)

elif question=="7.total number of views for each channel, and their  corresponding channel names":
    query7='''select channel_name as channelname ,views as totalviews from channels'''
    cursor.execute(query7)
    mydb.commit()
    t7=cursor.fetchall()
    df7=pd.DataFrame(t7,columns=["channel name","totalviews"])
    st.write(df7)

elif question=="8.names of all the channels that have published videos in the year 2022":
    query8='''select title as video_title,published_date as videorelease,channel_name as channelname from videos
                where extract(year from published_date)=2022'''
    cursor.execute(query8)
    mydb.commit()
    t8=cursor.fetchall()
    df8=pd.DataFrame(t8,columns=["videotitle","published_date","channelname"])
    st.write(df8)

elif question=="9.average duration of all videos in each channel":
    query9='''select channel_name as channelname,AVG(duration) as averageduration from videos group by channel_name'''
    cursor.execute(query9)
    mydb.commit()
    t9=cursor.fetchall()
    df9=pd.DataFrame(t9,columns=["channelname","averageduration"])

    T9=[]
    for index,row in df9.iterrows():
        channel_title=row["channelname"]
        average_duration=row["averageduration"]
        average_duration_str=str(average_duration)
        T9.append(dict(channeltitle=channel_title,avgduration=average_duration_str))
    df1=pd.DataFrame(T9)
    st.write(df1)

elif question=="10.videos have the highest number of comments":
    query10='''select title as videotitle, channel_name as channelname,comment as comments from videos where comment is
                not null order by comments desc'''
    cursor.execute(query10)
    mydb.commit()
    t10=cursor.fetchall()
    df10=pd.DataFrame(t10,columns=["video title","channel name","comments"])
    st.write(df10)
