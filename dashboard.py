import streamlit as st
import pandas as pd
import altair as alt

def get_data(dir):
    df = pd.read_csv(dir, encoding='ISO-8859-15')
    spotify_cleaned = df.dropna()
    spotify_filtered = spotify_cleaned.loc[spotify_cleaned['streams'].str.isnumeric(), :]
    spotify_filtered.loc[:, 'streams'] = spotify_filtered['streams'].astype(int)
    spotify_filtered.loc[:, 'in_deezer_playlists'] = spotify_filtered['in_deezer_playlists'].astype(str)
    spotify_filtered.loc[:, 'in_deezer_playlists'] = spotify_filtered['in_deezer_playlists'].str.replace(',', '').astype(int)
    spotify_filtered = spotify_filtered.sort_values('streams', ascending=False)
    spotify_filtered = spotify_filtered.head(100)
    spotify_filtered['spotify_rank'] = spotify_filtered['in_spotify_playlists'].rank(method='min', ascending=False)
    spotify_filtered['apple_rank'] = spotify_filtered['in_apple_playlists'].rank(method='min', ascending=False)
    spotify_filtered['deezer_rank'] = spotify_filtered['in_deezer_playlists'].rank(method='min', ascending=False)
    return spotify_filtered

def plot_popularity(top_n_songs_sorted_reset_index, songs_count_selector):
    max_range = songs_count_selector[1]
    # Define selections
    selection= alt.selection_point(fields=['track_name'])
    
    # Bar Plot
    bar_plot = alt.Chart(top_n_songs_sorted_reset_index).mark_bar().encode(
        x=alt.X('streams:Q', title='Streams'),
        y=alt.Y('track_name:N', sort='-x', title='Track Name'),
        color=alt.condition(
            selection,
            alt.ColorValue("steelblue"),
            alt.ColorValue("lightgray")
        ),
        tooltip=[alt.Tooltip('track_name:N', title='Track Name'), 
                 alt.Tooltip('artist(s)_name:N', title='Artist(s) Name'), 
                 alt.Tooltip('spotify_rank:N', title='Spotify Rank'), 
                 alt.Tooltip('apple_rank:N', title='Apple Rank'), 
                 alt.Tooltip('deezer_rank:N', title='Deezer Rank'), 
                 alt.Tooltip('streams:Q', title='Streams')]
    ).properties(
        width=300,
        height=300,
        title=f'Top {max_range} Songs Streaming on Spotify'
    ).add_params(selection).add_params(selection)

    # Scatterplot
    scatter_plot = alt.Chart(top_n_songs_sorted_reset_index).mark_circle().encode(
        x=alt.X('spotify_rank:Q', title='Spotify Rank'),  
        y=alt.Y('apple_rank:Q', title='Apple Rank'),     
        size=alt.Size('deezer_rank:Q', title='Deezer Rank'),
        color=alt.condition(
            selection,
            alt.ColorValue("steelblue"),
            alt.ColorValue("lightgray")
        ),
        tooltip=[alt.Tooltip('track_name:N', title='Track Name'), 
                 alt.Tooltip('artist(s)_name:N', title='Artist(s) Name'), 
                 alt.Tooltip('spotify_rank:N', title='Spotify Rank'), 
                 alt.Tooltip('apple_rank:N', title='Apple Rank'), 
                 alt.Tooltip('deezer_rank:N', title='Deezer Rank'), 
                 alt.Tooltip('streams:Q', title='Streams')]
    ).properties(
        width=300,
        height=300,
        title=f'Top {max_range} Songs Platform Ranking'
    ).add_params(selection).add_params(selection)

    return (bar_plot | scatter_plot)

# Donut chart
def make_donut(input_response, input_text, other_text, input_color):
    if input_color == 'blue':
        chart_color = ['#29b5e8', '#155F7A']
    if input_color == 'green':
        chart_color = ['#27AE60', '#12783D']
    if input_color == 'orange':
        chart_color = ['#F39C12', '#875A12']
    if input_color == 'red':
        chart_color = ['#E74C3C', '#781F16']
    
    source = pd.DataFrame({
        "Topic": [other_text, input_text],
        "% value": [100-input_response, input_response]
    })
    source_bg = pd.DataFrame({
        "Topic": [other_text, input_text],
        "% value": [100, 0]
    })
    
    plot = alt.Chart(source).mark_arc(innerRadius=45, cornerRadius=25).encode(
        theta="% value",
        color= alt.Color("Topic:N",
                        scale=alt.Scale(
                            #domain=['A', 'B'],
                            domain=[input_text, other_text],
                            # range=['#29b5e8', '#155F7A']),  # 31333F
                            range=chart_color),
                        legend=None),
    ).properties(width=150, height=150)
    
    text = plot.mark_text(align='center', color="#29b5e8", font="Lato", fontSize=32, fontWeight=700, fontStyle="italic").encode(text=alt.value(f'{input_response} %'))
    plot_bg = alt.Chart(source_bg).mark_arc(innerRadius=45, cornerRadius=20).encode(
        theta="% value",
        color= alt.Color("Topic:N",
                        scale=alt.Scale(
                            domain=[input_text, other_text],
                            range=chart_color),  # 31333F
                        legend=None),
    ).properties(width=150, height=150)
    return plot_bg + plot + text

def plot_musicality(top_n_songs_sorted_reset_index, top_range=(0, 10), x_axis='energy_%', y_axis='danceability_%'):
    # Define selections
    selection= alt.selection_point(fields=['track_name'])
    
    # dot plot
    dots = alt.Chart(top_n_songs_sorted_reset_index).transform_fold(
        ['danceability_%', 'valence_%', 'energy_%', 'acousticness_%', 'liveness_%', 'speechiness_%'],
        as_=['Metric', 'Value']
    ).mark_circle().encode(
        x=alt.X('Value:Q', title='Value'),
        y=alt.Y('Metric:N', title=None, sort='-x', axis=alt.Axis(titleFontSize=12, labelFontSize=10)),
        color=alt.condition(selection, alt.value('darkgreen'), alt.value('lightgray')),
        tooltip=[alt.Tooltip('track_name:N', title='Track Name'), alt.Tooltip('artist(s)_name:N', title='Artist(s) Name'), alt.Tooltip('Value:Q', title='Metric'), 'streams:Q', alt.Tooltip('spotify_rank:N', title='Spotify Rank'), 'streams:Q']
    ).properties(
        width=350,
        height=200,
        title='Music Metric Distribution'
    ).add_params(selection)

    # scatter plot
    scatter_base = alt.Chart(top_n_songs_sorted_reset_index).mark_point().encode(
        x=alt.X(x_axis + ':Q', title=x_axis.replace('_', ' ').title()),
        y=alt.Y(y_axis + ':Q', title=y_axis.replace('_', ' ').title()),
        color=alt.condition(selection, alt.value('darkgreen'), alt.value('lightgray')),
        tooltip=[alt.Tooltip('track_name:N', title='Track Name'), alt.Tooltip('artist(s)_name:N', title='Artist(s) Name'), alt.Tooltip(x_axis + ':Q', title=x_axis.replace('_', ' ').title()), alt.Tooltip(y_axis + ':Q', title=y_axis.replace('_', ' ').title()), 'streams:Q']
    ).properties(
        width=200,
        height=200,
        title='Music Metric Correlation'
    ).add_params(selection)
    return (dots | scatter_base)

# Heatmap Plot
def make_heatmap(data, metrics, x_field, color_field, selected_color_theme='greens'):
    # Create a DataFrame for the heatmap
    heatmap_df = pd.DataFrame({
        'Metric': [],
        'Track': [],
        'Streams': [],
        'Value': []
    })

    # Iterate over each metric
    for metric in metrics:
        metric_data = data[[x_field, 'streams', metric]].copy()
        metric_data.rename(columns={metric: 'Value'}, inplace=True)
        metric_data['Metric'] = metric
        heatmap_df = pd.concat([heatmap_df, metric_data], ignore_index=True)

    # Sort the DataFrame based on the 'streams' column
    heatmap_df = heatmap_df.sort_values(by='Streams', ascending=False)

    # Create the heatmap using Altair
    heatmap = alt.Chart(heatmap_df).mark_rect().encode(
        y=alt.Y(f'{x_field}:N', title='Track',sort='-x'),
        x=alt.X('Metric:N', title='Metric', sort=metrics),
        color=alt.Color('Value:Q', scale=alt.Scale(scheme=selected_color_theme)),
        tooltip=[alt.Tooltip(x_field + ':N', title='Track'), 'Metric:N', 'Value:Q']
    ).properties(
        width=400,
        height=600,
        title='Music Metric Heatmap'
    )

    return heatmap

def mode_plot(top_n_songs, spotify_filtered, max_dim):
    # Get unique keys from the entire spotify_filtered dataset and sort them in descending order
    all_keys_sorted = sorted(spotify_filtered['key'].unique(), reverse=True)
    
    # Create a base chart
    base = alt.Chart(top_n_songs).transform_calculate(
        mode=alt.expr.if_(alt.datum.mode == 'Minor', 'Minor', 'Major')
    ).properties(
        width=100,
        height=150
    )
    
    base0 = alt.Chart(spotify_filtered).transform_calculate(
        mode=alt.expr.if_(alt.datum.mode == 'Minor', 'Minor', 'Major')
    ).properties(
        width=100,
        height=150
    )

    # Left chart - Minor Mode
    left = base.transform_filter(
        alt.datum.mode == 'Minor'
    ).encode(
        y=alt.Y('key:N', axis=alt.Axis(labels=False), scale=alt.Scale(domain=all_keys_sorted)),
        x=alt.X('count(key):N', title='# of Songs', sort=alt.SortOrder('descending'), scale=alt.Scale(domain=[0, max_dim])),
        color=alt.value('#875A12'),
        tooltip=['mode:N', 'key:N', 'count(mode):N']
    ).mark_bar().properties(title='Minor')

    # Middle chart - Spacer
    middle = base0.encode(
        y=alt.Y('key:N', axis=None, scale=alt.Scale(domain=all_keys_sorted)),
        text=alt.Text('key:N')
    ).mark_text().properties(
        width=5
    )

    # Right chart - Major Mode
    right = base.transform_filter(
        alt.datum.mode == 'Major'
    ).encode(
        y=alt.Y('key:N', axis=alt.Axis(labels=False), scale=alt.Scale(domain=all_keys_sorted)),
        x=alt.X('count(key):N', title='# of Songs', scale=alt.Scale(domain=[0, max_dim])),
        color=alt.value('orange'),
        tooltip=['mode:N', 'key:N', 'count(mode):N']
    ).mark_bar().properties(title='Major')

    # Concatenate charts
    modes = left | middle | right
    
    return modes

def main():
    # Page configuration
    st.set_page_config(
        page_title="Top 100 Spotify Music Analysis",
        page_icon="🎵",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    alt.themes.enable("dark")
    
    dir = "https://tinyurl.com/y822sfzy"
    spotify_filtered = get_data(dir)
    
    # Displaying the image as a headline
    st.image("headline.jpeg", use_column_width=True)
    st.write("")  
    st.write("Nowadays, music streaming has played a very important role in people’s entertainment life. Along with the platforms, the music streaming market worldwide is projected to reach a revenue of **US$29.60bn** in 2024 with a revenue growth rate at **14.6%**, according to Statista. Among the multitude of platforms available, Spotify stands out as one of the most popular music streaming services.")
    st.write("Our website attempts to explore the essence of what makes songs famous to the top of Spotify's charts in 2023, comparing their popularity across various platforms. Through insightful visualizations, we aim to assist industry experts in crafting the next big hits for business growth, while also guiding music enthusiasts to discover songs with similar characteristics to their favorites. **Join us in exploring the heartbeat of today's music scene !**")
    
    with st.sidebar:
        st.title('🎵 Top 100 Spotify Music Analysis')

        songs_count_selector = st.slider('Top Songs', 0, 100, (0, 10), key='top_songs')

        with st.expander('About', expanded=True):
            st.write("")
            st.write('''
                - **Data Souce**: The original dataset is extracted from the [Spotify API](<https://developer.spotify.com/documentation/web-api>). Our work is built on a pre-extracted dataset thanks to the Kaggle contributor [Spotify-2023](<https://www.kaggle.com/datasets/nelgiriyewithana/top-spotify-songs-2023/data>).
                - **Musicality Metrics**:
                    - :orange[**danceability_%**]: Percentage indicating how suitable the song is for dancing
                    - :orange[**valence_%**]: Positivity of the song's musical content
                    - :orange[**energy_%**]: Perceived energy level of the song 
                    - :orange[**acousticness_%**]: Amount of acoustic sound in the song
                    - :orange[**instrumentalness_%**]: Amount of instrumental content in the song
                    - :orange[**liveness_%**]: Presence of live performance elements
                    - :orange[**speechiness_%**]: Amount of spoken words in the song
                ''')

    min_range = 0  # Minimum range remains 0
    max_range = songs_count_selector[1]  # Maximum range is set to the second value of the slider tuple
    range_val = max_range - min_range
    max_dim = range_val / 6
    
    top_n_songs = spotify_filtered.iloc[min_range:max_range]
    top_n_songs_sorted = top_n_songs.sort_values(by="streams", ascending=False)
    top_n_songs_sorted_reset_index = top_n_songs_sorted.reset_index(drop=True)
    top_n_songs_sorted_reset_index.index += 1
    top_n_songs_sorted_reset_index = top_n_songs_sorted_reset_index.rename_axis('Rank')
    
    # DataFrame Container
    with st.container():
        col = st.columns((10,4), gap='medium')
        
        with col[0]: 
            st.write(f'#### 🏆 Top {max_range} Song Streams on Spotify')
            st.dataframe(top_n_songs_sorted_reset_index,
                         column_order=("Rank", "track_name", "streams", "artist(s)_name"),
                         hide_index=False,
                         width=700,
                         column_config={
                              "Rank": st.column_config.TextColumn("Rank"),  
                              "track_name": st.column_config.TextColumn("Track Name"),
                              "artist(s)_name": st.column_config.TextColumn("Artist(s)"),
                              "streams": st.column_config.ProgressColumn(
                                  "Streams",
                                  format="%f",  
                                  min_value=0,
                                  max_value=max(top_n_songs_sorted.streams),
                              )}
                        )
        with col[1]:
            st.write(f'####  ')
            # Calculate the percentage of streams for the selected top songs
            total_streams_top_songs = top_n_songs_sorted_reset_index['streams'].sum()
            percentage_streams_top_songs = total_streams_top_songs / spotify_filtered['streams'].sum() * 100
            st.write("")  
            # Plot the donut chart
            st.write(f' Percentage of Total Streams')
            donut_chart = make_donut(round(percentage_streams_top_songs), f'Top {max_range} Song Stream Percentage', 'Other Songs', 'red')
            st.altair_chart(donut_chart, use_container_width=True)
                
        st.info("* Note the Rank above refers to the amount of streams on Spotify. The 'Platform' Rank referes to another algorithm which is based on the number of playlists on according to each platform.")

    with st.container():
        col = st.columns((8,2), gap='small')
        
        with col[0]:
            st.markdown(f'#### Popularity of Tracks')
            plot = plot_popularity(top_n_songs_sorted_reset_index, songs_count_selector)
            st.altair_chart(plot, use_container_width=True)
          
    # Tech Container
    with st.container():
        st.markdown(f'#### Musicality of Tracks')
        col = st.columns((10, 3), gap='large')
        with col[1]:
            x_axis = st.selectbox('X-Axis', ['danceability_%', 'valence_%', 'energy_%', 'acousticness_%', 'liveness_%', 'speechiness_%'], key='x_axis', index=0, format_func=lambda x: x.replace('_', ' ').title())
            y_axis = st.selectbox('Y-Axis', ['valence_%', 'energy_%', 'acousticness_%', 'liveness_%', 'speechiness_%', 'danceability_%'], key='y_axis', index=1, format_func=lambda x: x.replace('_', ' ').title())
          
        with col[0]:  
            plot_2 = plot_musicality(top_n_songs_sorted_reset_index, x_axis=x_axis, y_axis=y_axis)
            st.altair_chart(plot_2, use_container_width=True)
            
    # Tech Container
    with st.container():
        col = st.columns((6, 4), gap='large')
        
        with col[1]:
            st.write("###### Mode Distribution")
            # Calculate the percentage of modes for the selected top songs
            top_songs_count = top_n_songs_sorted_reset_index['mode'].count()
            major_count = top_n_songs_sorted_reset_index['mode'][top_n_songs_sorted_reset_index['mode'] == 'Major'].count()
            percentage_major = major_count / top_songs_count * 100
            
            # Plot the donut chart
            donut_chart_mode = make_donut(round(percentage_major), 'Major Percentage', 'Minor Percentage', 'orange')
            st.write(f' Percentage of Modes')
            st.altair_chart(donut_chart_mode, use_container_width=True)

            # Plot the key-mode
            base_mode = mode_plot(top_n_songs_sorted_reset_index, spotify_filtered, max_dim)
            st.altair_chart(base_mode, use_container_width=True)        
        
        with col[0]:  
            metrics = ['danceability_%', 'valence_%', 'energy_%', 'acousticness_%', 'liveness_%', 'speechiness_%']
            heatmap = make_heatmap(top_n_songs_sorted_reset_index, metrics, 'track_name', 'value_of_each_metrics', selected_color_theme='greens')
            st.altair_chart(heatmap, use_container_width=True)
  
if __name__ == "__main__":
    main()
