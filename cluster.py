import random
from math import sqrt
import matplotlib.pyplot as plt


def get_distance_points(point, cluster):
    return round(sqrt((point[0] - cluster[0]) ** 2 + (point[1] - cluster[1]) ** 2), 2)


def get_rand_cen(no_points):
    points = set()

    for no_point in range(no_points):
        while 1:
            x = round(random.uniform(-2000, 2000), 2)
            y = round(random.uniform(-2000, 2000), 2)
            if (x, y) not in points:
                break
        points.add((x, y))

    return points


def get_all_points(points, no_points):
    for no_point in range(no_points):
        point = random.choice(tuple(points))
        while 1:
            x = round(random.uniform(point[0] - 100, point[0] + 100), 2)
            y = round(random.uniform(point[1] - 100, point[1] + 100), 2)
            if (x, y) not in points:
                break
        points.add((x, y))


def add_to_cluster(key, clusters, point):
    if clusters[key] == 0:
        clusters[key] = {}
        clusters[key][point] = point
    elif point not in clusters[key]:
        clusters[key][point] = point
        for cluster in clusters:
            if clusters[cluster] == 0 or cluster == key:
                continue
            if point in clusters[cluster]:
                del clusters[cluster][point]


def update_centroid(clusters):
    change = False
    for iteration in range(len(clusters)):
        cluster = list(clusters.keys())[0]
        x, y = 0, 0
        if clusters[cluster] == 0 or len(clusters[cluster]) == 0:
            clusters[cluster] = clusters.pop(cluster)
            continue
        for point in clusters[cluster]:
            x += point[0]
            y += point[1]
        new_key = (round(x / len(clusters[cluster]), 2), round(y / len(clusters[cluster]), 2))
        if new_key != cluster:
            change = True
        clusters[new_key] = clusters.pop(cluster)

    return change


def get_rand_med(points, no_clusters):
    init_medoid = set()

    while 1:
        if len(init_medoid) != no_clusters:
            init_medoid.add(random.choice(tuple(points)))
        else:
            break

    return init_medoid


def update_medoid(clusters):
    change = False

    for iteration in range(len(clusters)):
        cluster = list(clusters.keys())[0]
        dist_best = 0
        med_best = 0

        for new_med in clusters[cluster]:
            distance = 0

            for point in clusters[cluster]:
                distance += get_distance_points(point, new_med)
            if distance < dist_best or dist_best == 0:
                dist_best = distance
                med_best = new_med

        if med_best != cluster:
            change = True
        clusters[med_best] = clusters.pop(cluster)

    return change


def get_plt_var(clusters):
    colors = ["teal", "cyan", "deeppink", "plum", "indigo", "darkred", "olive", "turquoise", "grey",
              "purple", "lime", "chocolate", "orange", 'k', 'y', 'm', 'c', 'r', 'g', 'b']
    x_list = []
    y_list = []
    color = []
    for cluster in clusters:
        curr_color = colors.pop()
        if clusters[cluster] == 0:
            continue
        for point in clusters[cluster]:
            x_list.append(point[0])
            y_list.append(point[1])
            color.append(curr_color)

    plt.scatter(x_list, y_list, c=color)


def get_plt_center(clusters):
    colors = ["teal", "cyan", "deeppink", "plum", "indigo", "darkred", "olive", "turquoise", "grey",
              "purple", "lime", "chocolate", "orange", 'k', 'y', 'm', 'c', 'r', 'g', 'b']
    for cluster in clusters:
        color = colors.pop()
        if color != 'k':
            plt.plot(cluster[0], cluster[1], marker="X", color=color, mec='black')
        else:
            plt.plot(cluster[0], cluster[1], marker="X", color=color, mec='white')


def k_means(center, points, no_clusters):
    if center == 'c':
        clusters = dict.fromkeys(get_rand_cen(no_clusters), 0)
    elif center == 'm':
        clusters = dict.fromkeys(get_rand_med(points, no_clusters), 0)
    elif center == 'd':
        clusters = dict.fromkeys(get_rand_cen(2), 0)
    else:
        return

    change = True
    dist_lw_500 = 0

    while change and not dist_lw_500:
        dist_lw_500 = True
        for point in points:
            distance = []
            for cluster in clusters:
                distance.append((get_distance_points(point, cluster), cluster))
            min_distance = min(distance)
            dist_lw_500 += min_distance[0]
            add_to_cluster(min_distance[1], clusters, point)

        if center != 'd':
            do_plt(clusters)

        if center == 'c' or center == 'd':
            change = update_centroid(clusters)
        elif center == 'm':
            change = update_medoid(clusters)

    if center == 'c' or center == 'm':
        if (dist_lw_500 / len(points)) <= 500:
            print("k-means je uspesny")
        else:
            print("k-means je neuspesny")
    elif center == 'd':
        return clusters, dist_lw_500

    do_plt(clusters)


def do_plt(clusters):
    get_plt_var(clusters)
    get_plt_center(clusters)
    plt.xlim(-2000, 2000)
    plt.ylim(-2000, 2000)
    plt.show()


def get_worst_cluster(clusters):
    worst_dist = 0
    worst_cluster = 0

    for cluster in clusters:
        dist = 0
        for point in clusters[cluster]:
            dist += get_distance_points(point, cluster)
        dist /= len(clusters[cluster])
        if dist > worst_dist:
            worst_dist = dist
            worst_cluster = cluster

    clus = clusters[worst_cluster]
    del clusters[worst_cluster]
    return clus


def div_clustering(points, no_clusters):
    global dist_lw_500
    clusters, dist_lw_500 = k_means('d', points, "")
    do_plt(clusters)
    while no_clusters != len(clusters):
        cluster = get_worst_cluster(clusters)
        new_points = set(cluster.values())
        while 1:
            new_clusters, dist_lw_500 = k_means('d', new_points, "")
            if 0 not in new_clusters.values():
                break
        clusters = {**clusters, **new_clusters}
        do_plt(clusters)

    if (dist_lw_500 / len(points)) <= 500:
        print("divízne zhlukovanie je uspesne")
    else:
        print("divízne zhlukovanie je neuspesne")


def aggl_clustering(points, no_cluster):
    my_iter, curr_iter, out_iter = 0, 0, 0
    end = False

    clusters = get_init_clust(points)

    while not end:
        curr_iter, my_iter, out_iter = add_closest_clusters(clusters, curr_iter, my_iter, out_iter)

        if len(clusters) <= 20:
            do_plt(clusters)
        update_centroid(clusters)
        if len(clusters) == no_cluster:
            end = True
            break
        if my_iter < curr_iter:
            out_iter += 1

    dist_lw_500 = get_total_dist(clusters)

    if (dist_lw_500 / len(points)) <= 500:
        print("aglomeratívne zhlukovanie je uspesne")
    else:
        print("aglomeratívne zhlukovanie je neuspesne")


def get_init_clust(points):
    clusters = {}
    for point in points:
        clusters[point] = {point: point}
    return clusters


def get_total_dist(clusters):
    dist_lw_500 = 0
    for cluster in clusters:
        for point in clusters[cluster]:
            dist_lw_500 += get_distance_points(point, cluster)

    return dist_lw_500


def add_closest_clusters(clusters, curr_iter, my_iter, out_iter):
    if out_iter == len(clusters):
        out_iter = 0
    cluster = list(clusters.keys())[out_iter]
    best_dist = 0, 0
    for iteration in range(len(clusters)):
        other_clust = list(clusters.keys())[iteration]
        dist_clusters = get_distance_points(other_clust, cluster)
        if dist_clusters == 0:
            my_iter = iteration
        else:
            if dist_clusters < best_dist[0] or best_dist[0] == 0:
                best_dist = dist_clusters, other_clust
                curr_iter = iteration
    clusters[cluster] = {**clusters[cluster], **clusters[best_dist[1]]}
    del clusters[best_dist[1]]

    return curr_iter, my_iter, out_iter


points = get_rand_cen(20)
get_all_points(points, 1000)

# k_means('c', points, 5)
# k_means('m', points, 5)
# div_clustering(points, 5)
# aggl_clustering(points, 5)