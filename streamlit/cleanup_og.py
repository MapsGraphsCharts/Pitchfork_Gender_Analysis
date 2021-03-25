import streamlit as st
import pandas as pd
import numpy as np
# import pandas_profiling
# from streamlit_pandas_profiling import st_profile_report
from namsorclient import NamsorClient
from namsorclient.country_codes import CountryCodes
from namsorclient.request_objects import *

st.title('Pitchforked')
st.image('/home/tim/dev/notebooks/pitchforked/images/tool-4958040_1920.jpg',
         caption="Visualizing gender & ethnic disparities in the music review industry.")


# Functions

def load_data():
    data = pd.read_pickle("/home/tim/dev/streamlit_projects/pitchforked/data/data_original/pitchforked_clean")
    return data


pf_sorta_clean = load_data().copy()
st.write(pf_sorta_clean.head(100))

st.write("I've loaded the first one hundred rows of scraped data, "
         "let's drop some columns we aren't going to be using")

to_drop = ['genre_2',
           'genre_3',
           'genre_4',
           'gender',
           'race',
           'asian',
           'hispanic',
           'nh_black',
           'nh_white']
st.write("Let's drop the following columns", to_drop)

pf_sorta_clean.drop(to_drop, inplace=True, axis=1)

st.write("Now, let's take the unique reviewers only, I'd like to pass them through the Namsor API")
unique_reviewers = pf_sorta_clean.drop_duplicates(subset=['pitchfork_author']).reset_index()

to_drop2 = ['artist',
            'best_new_music',
            'album_name',
            'album_score',
            'album_label',
            'album_year',
            'pitchfork_review_date',
            'pitchfork_review_abstract',
            'genre',
            'pitchfork_review_date',
            'pitchfork_review_text',
            'pitchfork_review_date_year',
            'index'
            ]
unique_reviewers.drop(to_drop2, inplace=True, axis=1)
st.write(unique_reviewers)

st.write("Roughly, 447 reviewers in the history of Pitchfork, Now we will use the api provided by Namsor to attempt "
         "to label gender "
         "and ethnicity to our reviewers. To begin let's import the Namsor python library, let's write some functions "
         "to grab the data")

def get_gender():
    client = NamsorClient("1d3f59671191623ca94925199d974856")
    gender_container = []
    for index, row in unique_reviewers.iterrows():
        first_name = row['pitchfork_author_first_name']
        last_name = row['pitchfork_author_last_name']
        search = client.gender(first_name=first_name, last_name=last_name)
        gender_results = {
            'pitchfork_author_first_name': search.first_name,
            'pitchfork_author_last_name': search.last_name,
            'likelygender': search.likely_gender,
            'genderscale': search.gender_scale,
            'gender_score': search.score,
            'probabilitycalibrated': search.probability_calibrated
        }
        gender_container.append(gender_results)
    return pd.DataFrame.from_dict(gender_container)


def get_race_ethnicity():
    client = NamsorClient("1d3f59671191623ca94925199d974856")
    ethnicity_container = []
    for index, row in unique_reviewers.iterrows():
        first_name = row['pitchfork_author_first_name']
        last_name = row['pitchfork_author_last_name']
        search = client.usRaceEthnicity(first_name=first_name, last_name=last_name)
        ethnicity_results = {
            'pitchfork_author_first_name': search.first_name,
            'pitchfork_author_last_name': search.last_name,
            'race_ethnicity': search.race_ethnicity,
            'race_ethnicity_alt': search.race_ethnicity_alt,
            'ethnicity_score': search.score,

        }
        ethnicity_container.append(ethnicity_results)
    return pd.DataFrame.from_dict(ethnicity_container)


# gender_results = get_gender()
# ethnicity_results = get_race_ethnicity()
#
#
# unique_reviewers = pd.merge(unique_reviewers, gender_results,
#                             on=['pitchfork_author_first_name',
#                                 'pitchfork_author_last_name'])
#
# unique_reviewers = pd.merge(unique_reviewers, ethnicity_results,
#                             on=['pitchfork_author_first_name',
#                                 'pitchfork_author_last_name'])

st.write(unique_reviewers)

pd.to_pickle(unique_reviewers, "/home/tim/dev/streamlit_projects/pitchforked/data/pitchfork_authors")

test = pd.read_pickle("/home/tim/dev/streamlit_projects/pitchforked/data/pitchfork_authors")

st.write(test)