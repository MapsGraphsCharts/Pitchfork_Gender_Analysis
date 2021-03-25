import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import os
cwd = os.getcwd()
image_path = os.path.join(cwd, "tool-4958040_1920.jpg")

st.title('Pitchforked')
st.image("tool-4958040_1920.jpg", caption="Empirically visualizing gender & racial disparity in the music review business.")
st.header("Premise")
st.write("""
            As a big indie music fan, I'm no stranger to Pitchfork, the world's largest independent music review 
            publication. In earlier days Pitchfork was known for writing unpredictable, at times scathing, and often early 
            released album reviews that could make or break an emerging artists. This eventually culminated in 
            Pitchfork being purchased by the media conglomerate Conde Nast for an undisclosed amount in 2015. 
         
         """)

st.write("""
            In February 2020 I decided it would be a fun project to 'web-scrape' every historical
            Pitchfork review to look for interesting trends in music.            
            
            While reviewing the initial dataset, my wife posed a great question..."How many of these reviews do you 
            think were written by men?" With a bit of python skill, the reviewers names, and some free time
            I set out to answer that question with my HR analyst hat on...
            
            As this is an article on Pitchfork and not coding, I only want to make a brief mention of how gender/ethnicity was 
            derived. 
            
            -   Genders were derived by sending first/last name to Namesor API, this tool is frequently used in 
                commercial/academic situations where this type of work could be of high importance.
            -   I've set the default gender confidence to 90%+ in these charts, you are welcome to change this in the sidebar and encouraged to play around.
            -   Gender is non-binary, however, for statistical analysis, this is the best means of getting at the issue for the greater good.
            
            Without further ado...
        """)
st.header("Gender Analysis")



# Functions

def load_data(path):
    data = pd.read_pickle(path)
    return data


#                                       LOAD AND CLEAN DATASET


pitchfork_authors = load_data("/data/pitchfork_authors")
pitchfork_dataset = load_data("/data/data_original/pitchforked_clean")

drop_cols = ['nh_white',
             'nh_black',
             'hispanic',
             'asian',
             'race',
             'gender',
             'genre_4',
             'genre_3',
             'genre_2',
             'pitchfork_review_text',
             'pitchfork_review_abstract',
             ]

pitchfork_dataset.drop(drop_cols, inplace=True, axis=1)

pitchfork_dataset = pitchfork_dataset.merge(pitchfork_authors)

drop_cols = ['pitchfork_author_first_name',
             'pitchfork_author_last_name',
             'genderscale',
             'gender_score',
             'race_ethnicity_alt',
             ]
pitchfork_dataset.drop(drop_cols, inplace=True, axis=1)
pitchfork_dataset.reset_index()
pd.to_datetime(pitchfork_dataset['pitchfork_review_date'])

#                                        SETUP SIDEBAR & GLOBAL FILTERS

gender_confidence_filter = st.sidebar.slider('Gender Confidence',min_value=50, max_value=100, value=90)
filtered_confidence = pitchfork_dataset[pitchfork_dataset['probabilitycalibrated']*100 >= gender_confidence_filter]

years_to_filter = st.sidebar.slider('Select Years', 1999, 2021, [2000, 2020])
filtered_data = pitchfork_dataset[(pitchfork_dataset['pitchfork_review_date_year'] >= years_to_filter[0]) & \
                (pitchfork_dataset['pitchfork_review_date_year'] <= years_to_filter[1])]


#                                        VISUALIZE GENDER COUNT BY YEAR

gender_by_year = filtered_data.groupby(by=['likelygender', 'pitchfork_review_date_year']).agg(
    total_reviews=pd.NamedAgg(column='likelygender', aggfunc='count'),
    average_album_score=pd.NamedAgg(column='album_score', aggfunc='mean'),
    minimum_album_score=pd.NamedAgg(column='album_score', aggfunc='min'),
    maximum_album_score=pd.NamedAgg(column='album_score', aggfunc='max')

).reset_index()

gender_by_year['pitchfork_review_date_year'] = pd.to_datetime(gender_by_year['pitchfork_review_date_year'], format='%Y')


gender_plot = alt.Chart(gender_by_year).mark_line(clip=True).encode(
    alt.X('year(pitchfork_review_date_year)', title='Review Year'),
    alt.Y('total_reviews', title='Total Reviews'),
    color=alt.Color('likelygender', legend=alt.Legend(title='Gender')),
    strokeDash='likelygender',
    tooltip=['total_reviews', 'pitchfork_review_date_year'],
    ).properties(title='Reviews per year by Gender')

st.write("""
         If we begin by looking at the chart below which shows the total number of reviews per year by gender (at 90% gender confidence),
          it's easy to begin
         formulating a story without much persuasion, Pitchfork has clearly been dominated by male reviewers
         throughout its history, there are however some encouraging signs.
         -  In 2010, near the peak of disparity, there were 957 male reviews and 59 female, roughly 6% of reviews were women.
         -  By 2020, ten years later, the playing field has begun to level, women accounted flor roughly 34% of reviews. 
            *   Could this be a combination of #MeToo movement and Conde Nast purchasing Pitchfork in 2015?   
         
         
         """)
st.altair_chart(gender_plot, use_container_width=True)

#                                          VISUALIZE COUNT OF REVIEWERS BY GENDER PER YEAR

unique_gender_count_by_year = filtered_data.groupby(by=['likelygender', 'pitchfork_review_date_year']).pitchfork_author.nunique().reset_index()
unique_gender_count_by_year['pitchfork_review_date_year'] = pd.to_datetime(unique_gender_count_by_year['pitchfork_review_date_year'], format='%Y')

unique_genders_plot = alt.Chart(unique_gender_count_by_year).mark_line(clip=True).encode(
    alt.X('year(pitchfork_review_date_year)', title='Review Year'),
    alt.Y('pitchfork_author', title='Unique Reviewers'),
    color=alt.Color('likelygender', legend=alt.Legend(title='Gender')),
    strokeDash = 'likelygender',
    tooltip=['pitchfork_author', 'pitchfork_review_date_year']
)

st.write("""
            So far, we've only looked at the total volume of reviews, what if we wanted to get an idea of how many 
            unique women/men have written reviews over the years, the below chart shows this view.
            
        -   in 2010, there were 4 unique women who contributed reviews, along with 43 men, that's 8.5% women. (ouch)
        -   In 2020, there were 60 unique women who contributed reviews, along with 117 men, that's 34% women. (improving)
        
            It's clear from this data that recent years have caused a huge shift in Pitchfork's gender values 
            when it comes to who should be writing music reviews.
            
            Have they done enough?...I can't attest to that, I've spent much of my career in HR, it isn't easy.
         
         
         """)
st.altair_chart(unique_genders_plot, use_container_width=True)

st.write('The table below is sampling 200 names with a gender confidence of 90 or greater, so that you may agree/disagree with '
         'the classifications, feel free to increase/decrease the gender probability to update charts.')
st.write(filtered_confidence[['pitchfork_author', 'likelygender', 'probabilitycalibrated']].drop_duplicates(subset=['pitchfork_author'])
         .sample(200)
         .sort_values(by=['likelygender'])
         .reset_index(drop=True))


#                                            VISUALIZE ETHNICITY & GENDER

st.header("Ethnicity Analysis")
st.write("""
            Finally, let's attempt to gain insight into ethnicity disparities over time. Accurately 
            discerning ethnicity from a first and last name is challenging, if not impossible at times, though we can again
            leverage a confidence score to gain a more accurate birds eye view.

            Below is a chart showing the four racial classes we are utilizing here: Asian, Black-Non-Latino, 
            Hispanic-Latino, and White-Non-latino.

            If you are willing to place any faith in this analysis, a few things become pretty clear immediately.

            -   The world of indie music reviews until recently was almost entirely controlled by well...white people.
            -   We can see starting in 2015 and continuing since, a dramatic decrease in the total review count of White Non-Latinos.
            -   There are many other assumptions one could make here, but they would all need much more rigorous analysis.
         """)

eth_confidence_number = st.slider(label="Ethnicity Confidence Filter",min_value=0, max_value=80, value=10)
eth_confidence_filter = filtered_data[filtered_data['ethnicity_score'] >= eth_confidence_number]



ethnicity_by_year = eth_confidence_filter.groupby(by=['race_ethnicity', 'pitchfork_review_date_year']).agg(
    total_reviews=pd.NamedAgg(column='likelygender', aggfunc='count'),
).reset_index()


ethnicity_by_year['pitchfork_review_date_year'] = pd.to_datetime(ethnicity_by_year['pitchfork_review_date_year'], format='%Y')

gender_eth_plot = alt.Chart(ethnicity_by_year).mark_line(clip=True).encode(
    alt.X('year(pitchfork_review_date_year)', title='Review Year'),
    alt.Y('total_reviews', title='Total Reviews'),
    color=alt.Color('race_ethnicity', legend=alt.Legend(title='Gender')),
    strokeDash='race_ethnicity',
    tooltip=['total_reviews', 'pitchfork_review_date_year'],
    ).properties(title='Reviews per year by Gender')






st.altair_chart(gender_eth_plot, use_container_width=True)


st.write("""
    -   Feel free to reduce/increase the confidence measure above, I've sampled a table below of 100 sample names, so you may find a confidence number you agree with.
        """)
st.write(eth_confidence_filter[['pitchfork_author', 'race_ethnicity', 'ethnicity_score']].drop_duplicates(subset=['pitchfork_author'])
         .sample(100)
         .sort_values(by=['race_ethnicity'])
         .reset_index(drop=True))

st.header("Closing Thoughts")

st.write("""
         It's clear that until around 2015, Pitchfork was comprised of almost entirely white male reviewers. The 
         "advent of #MeToo along with the Conde Nast purchase clearly forced Pitchfork to implement some diversity 
         measures. In 2010, men were contributing nearly 10:1 the amount of reviews, that number has seemingly been reduced to a near 
         3:1 margin at the end of 2020.
         
         I'm less sold on the ethnic diversity changes, they are harder to visualize, harder to measure, 
         and certainly harder for HR teams to positively change as well.
         
         All in all, two things are very evident.
         
         -  Strong social movements ABSOLUTELY work.
         -  Large faceless corporate entities such as Conde Nast are much more prone to these movements than small 
            independent businesses who need not react as quickly.
         
         Thanks for reading, if you found this particularly thought provoking and/or interesting, I'd love to hear 
         from you, catch me at tim@timothystafford.com. In the event you have an amazing opportunity that involves serious 
         data analysis with fun tools such as the below, I'm all ears!
         
         """)

st.header("Software Utilized")
st.write("""
        -   Streamlit (bless this amazing new library)
        -   Scrapy (webscraping in python)
        -   Python/Pandas (number crunching)
        -   Altair (Viz)
        -   Namesor (API for gender/ethnicity classifying)

""")





