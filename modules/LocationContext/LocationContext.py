import datetime, folium, random, numpy as np, pandas as pd
from bs4 import BeautifulSoup

def parse_kml(filename):
    """Parses a KML file into a Pandas DataFrame"""
    with open(filename) as f:
        rows = []
        soup = BeautifulSoup(f)
        for time, coords in zip(soup.findAll('when'), soup.findAll('gx:coord')):
            timestamp = time.string
            coords = coords.string.split(' ')[:2]
            latitude = float(coords[0])
            longitude = float(coords[1])
            rows.append([timestamp, latitude, longitude])
        df = pd.DataFrame(rows, columns=['Timestamp', 'Longitude', 'Latitude'])
        df['Timestamp'] = pd.to_datetime(df.Timestamp.str.slice(0,23), format='%Y-%m-%dT%H:%M:%S.%f')
        return df

def clean_data(df):
    """Only look at data within 75 miles of the median latitude and longitude."""
    miles = 75.0
    degrees = miles / 69.11
    for col in ('Latitude', 'Longitude'):
        median = df[col].median()
        df = df[(df[col] >= median - degrees) & (df[col] <= median + degrees)]
    return df

def get_work_df(df):
    """Get all data between 10AM and 4PM Monday-Friday"""
    return df[(df.hour >= 10) & (df.hour <= 16) & (df.day >= 0) & (df.day <= 4)]

def get_home_df(df):
    """Get all data between 11PM and 5AM Monday-Thursday"""
    return df[((df.hour >= 23) | (df.hour <= 5)) & (df.day >= 0) & (df.day <= 3)]

def format_for_clustering(df):
    """Format data for the clustering algorithm"""
    lng = df.Longitude
    lat = df.Latitude
    return np.array(zip(lng, lat))


# Clustering algorithm from the internet
# ------------------------------------- #
def cluster_points(X, mu):
    clusters  = {}
    for x in X:
        bestmukey = min([(i[0], np.linalg.norm(x-mu[i[0]])) for i in enumerate(mu)], key=lambda t:t[1])[0]
        try:
            clusters[bestmukey].append(x)
        except KeyError:
            clusters[bestmukey] = [x]
    return clusters
 
def reevaluate_centers(mu, clusters):
    newmu = []
    keys = sorted(clusters.keys())
    for k in keys:
        newmu.append(np.mean(clusters[k], axis = 0))
    return newmu
 
def has_converged(mu, oldmu):
    return (set([tuple(a) for a in mu]) == set([tuple(a) for a in oldmu]))

def find_centers(X, K):
    # Initialize to K random centers
    oldmu = random.sample(X, K)
    mu = random.sample(X, K)
    while not has_converged(mu, oldmu):
        oldmu = mu
        # Assign all points in X to clusters
        clusters = cluster_points(X, mu)
        # Reevaluate centers
        mu = reevaluate_centers(oldmu, clusters)
    return {'centers': mu, 'datapoints': clusters}
# ------------------------------------- #

def setup():
    """Set up the master DataFrame"""
    df = parse_kml('brady_location.kml')
    df = clean_data(df)
    df['hour'] = df.Timestamp.map(lambda x: x.hour)
    df['day'] = df.Timestamp.map(lambda x: x.dayofweek)
    return df

def get_location(df, location_func, n):
    """Use clustering to get a location for a certain time period"""
    location_df = location_func(df)
    location_data = format_for_clustering(location_df)
    location_cluster = find_centers(location_data, n)
    def f(x):
        err1 = abs(x[0] - location_df.Longitude.median())
        err2 = abs(x[1] - location_df.Latitude.median())
        return err1 + err2
    location_result = min(location_cluster['centers'], key=lambda x: f(x))
    return location_result

def display(initial_lat, initial_long, locations, map_path):
    """Use folium to display locations"""
    fmap = folium.Map(location=[initial_lat, initial_long], zoom_start=13)
    for location in locations:
        fmap.simple_marker([location[0][1], location[0][0]], popup=location[1])
    fmap.create_map(path=map_path)

def main():
    """Main function"""
    df = setup()
    work_location = get_location(df, get_work_df, 6)
    home_location = get_location(df, get_home_df, 6)
    locations = [(work_location, 'Work'), (home_location, 'Home')]
    display(df.Latitude.irow(0), df.Longitude.irow(0), locations, "map.html")
    return locations

main()
