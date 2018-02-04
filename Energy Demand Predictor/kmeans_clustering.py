import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import scale

# File paths
CONSUMPTION_DATA_FILE_PATH = 'E:\\per_capita_state_wise_2015_1.csv'
CALI_CONSUMPTION_DATA_FILE_PATH = 'E:\\cali_county_wise_electrcity_consumption_data1.csv'
STATE_CODES_FILE_PATH = 'E:\\state_codes.csv'
POPULATION_DATA_FILE_PATH = 'E:\\population_data_2004.csv'
COUNTY_POPULATION_DATA_FILE_PATH = 'E:\\county_population_data.csv'
COUNTY_PLOT_FILE = 'E:\\cali_county_wise_kmeans_6_clusters.png'
STATE_PLOT_FILE = 'E:\\statewise_kmeans_6_clusters.png'

# This method extracts the state wise population data from a CSV file and returns a dict for the same
def get_state_wise_population_data():
    state_population_map = {}
    with open(POPULATION_DATA_FILE_PATH) as file:
        for line in file:
            data = line.split(',')
            state_population_map[data[0].strip().lower()] = int(data[1].strip())

    return state_population_map


# This method extracts the state code data from a CSV file and returns a dict for the same
def get_state_codes():
    state_codes = {}
    with open(STATE_CODES_FILE_PATH) as file:
        for line in file:
            data = line.split(',')
            state_codes[data[0].strip()] = data[1].strip().lower()

    return state_codes


# Method to plot the k-means cluster
def plot_k_means_cluster(scaled_np_arr, num_clusters=4, file_name=None):
    plt.clf()
    plt.ylabel('Per Capita Energy Consumption')
    plt.xlabel('Total Energy Consumption')
    kmeans = KMeans(n_clusters=num_clusters, n_init=10, init='random').fit(scaled_np_arr)
    centroids = kmeans.cluster_centers_
    labels = kmeans.labels_

    plt.scatter(centroids[:, 0], centroids[:, 1],
                marker='x', s=169, linewidths=3,
                color='b', zorder=10)
    plt.scatter(scaled_np_arr[:, 0], scaled_np_arr[:, 1], c=labels.astype(np.float), edgecolor='k')

    if file_name is not None:
        plt.savefig(file_name)
        return

    plt.show()


# This method extracts the state wise energy consumption data from a CSV file and returns a dict for the same
def get_scaled_state_wise_consumption_data():
    state_population_map = get_state_wise_population_data()
    state_code_map = get_state_codes()
    state_wise_stats = {}
    with open(CONSUMPTION_DATA_FILE_PATH) as file:
        next(file)
        for line in file:
            data = line.strip().split(',')
            state_code = data[0].strip()
            if state_code not in state_code_map:
                continue
            state = state_code_map[state_code].lower()
            per_capita_energy_use = float(data[1].strip())
            total_consumption = state_population_map[state] * per_capita_energy_use
            state_wise_stats[state] = [total_consumption, per_capita_energy_use]

    np_arr = np.array(list(state_wise_stats.values()), dtype=np.float)
    np_arr_scaled = scale(np_arr)
    return np_arr_scaled


# This method extracts the county wise population data from a CSV file and returns a dict for the same
def get_county_wise_population_data_for_state(file_name, state_name=None):
    county_population_map = {}
    state_name = state_name.lower().strip()
    with open(file_name) as file:
        for line in file:
            data = line.split(',')
            if state_name is not None and data[0].strip().lower() != state_name:
                continue
            county_population_map[data[1].strip().lower()] = int(data[4].strip())

    return county_population_map


# This method extracts the county wise energy consumption data from a CSV file and returns a dict for the same
def get_county_wise_energy_consumption_data(file_name, county_population_map):
    county_energy_use_map = {}
    with open(file_name) as file:
        next(file)
        for line in file:
            data = line.split(',')
            county = data[0].strip().lower()
            if county not in county_population_map:
                continue
            energy_consumption = float(data[1].strip())
            per_capita_energy = energy_consumption / county_population_map[county]
            county_energy_use_map[county] = [energy_consumption, per_capita_energy]

    return county_energy_use_map


def get_scaled_county_wise_consumption_data(state):
    county_populaton_data = get_county_wise_population_data_for_state(COUNTY_POPULATION_DATA_FILE_PATH, state)
    county_wise_stats = get_county_wise_energy_consumption_data(CALI_CONSUMPTION_DATA_FILE_PATH, county_populaton_data)
    np_arr = np.array(list(county_wise_stats.values()))
    np_arr_scaled = scale(np_arr)
    return np_arr_scaled


# Plot state-level clusters
plot_k_means_cluster(get_scaled_state_wise_consumption_data(), 3, STATE_PLOT_FILE)


# Plot county-level clusters for California
plot_k_means_cluster(get_scaled_county_wise_consumption_data('California'), 4, COUNTY_PLOT_FILE)

