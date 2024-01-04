import numpy as np
import pandas as pd
import sqlite3 as sql
from math import floor
from uuid import uuid4
from time import mktime
from os import path, mkdir
from random import choices
import ciso8601 as fasttime
from itertools import cycle, permutations, repeat
rng = np.random.default_rng()


def time_dependent_random(independent_time, dependent_time, random_func, offset=0):
    start_time, end_time = dependent_time.min(), dependent_time.max()
    batch_independent_timestamps = np.concatenate([[0], independent_time[np.where(independent_time <= end_time)], [2147483647]])
    independent_count = np.where(independent_time <= start_time)[0].shape[0]
    batch_pointer_idx = 0
    minibatch_lst = []

    for idx in range(len(batch_independent_timestamps)-1):
        if independent_count == 0:
            independent_count += 1
            batch_pointer_idx += np.where(dependent_time < independent_time[idx])[0].shape[0]
            continue

        lower_time, upper_time = batch_independent_timestamps[idx:idx+2]
        minibatch = np.where(np.logical_and(lower_time <= dependent_time, dependent_time < upper_time))[0]
        if minibatch.shape[0] == 0:
            continue

        joined_index = np.cumsum(
            np.clip(
                np.round(
                    random_func(size=minibatch.shape[0])+1
                ),
                a_min=0,
                a_max=independent_count
            ),
            dtype=int
        )
        joined_choice = np.random.choice(np.arange(0, independent_count), size=joined_index[-1]).astype(int)

        minibatch_lst.append(
            np.column_stack((
                joined_choice,
                np.repeat(
                    np.arange(batch_pointer_idx, batch_pointer_idx+minibatch.shape[0]),
                    np.insert(np.ediff1d(joined_index), 0, joined_index[0])
                ).astype(int)
            ))
        )
        batch_pointer_idx += minibatch.shape[0]
        independent_count += 1

    result = np.vstack(minibatch_lst)
    result[:, 1] += offset
    return result

# Constants
user_count = 50_000
batch_size = 100_000
batch_count = 1_000_000//batch_size
random_func = lambda size: np.zeros(shape=size)
start_time = mktime(fasttime.parse_datetime("2009-05-20").timetuple())
end_time = mktime(fasttime.parse_datetime("2023-12-28").timetuple())
batch_timediff = (end_time - start_time)/batch_count
user_timestamps = np.transpose(pd.read_csv("./database/csv/users_table.csv", usecols=["creation_timestamp"]).to_numpy())[0]
image_timestamps = np.transpose(pd.read_csv("./database/csv/image_timestamps.csv", usecols["creation_timestamp"]).to_numpy())[0]

# Image Resolution constants
common_aspect_ratios = [(1, 1), (3, 2), (5, 4), (1, 2), (2, 1)]
custom_uncommon_ratios = [(h, w) for h,w in permutations(range(3, 11), r=2)]

image_sizes = ["800x600", "1080x1080", "1350x1080", "1280x720", "1240x1754", "1960x1080", "3840x2160"]
pixelart_heights = [64, 128, 256, 512]
custom_image_heights = [*range(300, 2050, 50)]

custom_common_image_sizes = []
for ratio in common_aspect_ratios:
    for height in custom_image_heights:
        custom_common_image_sizes.append(f"{ratio[0]*height}x{ratio[1]*height}")

custom_uncommon_image_sizes = []
for ratio in custom_uncommon_ratios:
    for height in custom_image_heights:
        custom_uncommon_image_sizes.append(f"{ratio[0]*height}x{ratio[1]*height}")

custom_pixelart_sizes = []
for ratio in common_aspect_ratios:
    for height in pixelart_heights:
        custom_pixelart_sizes.append(f"{ratio[0]*height}x{ratio[1]*height}")

# Text padding
description = cycle([""])

for idx in range(batch_count):
    index = np.arange(batch_size*idx, batch_size*(idx+1))
    
    # Image URLs and UUIDs
    urls = np.array([
        f"https://www.{tup[0]}.{tup[1]}.{tup[2]}.{tup[3]}"
        for tup in rng.choice(a=list(range(256)), size=(batch_size, 4))
    ])
    blob_uuids = [uuid4().bytes for _ in range(batch_size)]

    # Image Resolutions
    image_shape = rng.choice(
        [
            *image_sizes,
            *custom_common_image_sizes,
            *custom_uncommon_image_sizes,
            *custom_pixelart_sizes,
        ],
        size=batch_size,
        p=[
            0.03, 0.06, 0.10, 0.06, 0.03, 0.39, 0.20,
            *repeat(0.08/len(custom_common_image_sizes), len(custom_common_image_sizes)),
            *repeat(0.04/len(custom_uncommon_image_sizes), len(custom_uncommon_image_sizes)),
            *repeat(0.01/len(custom_pixelart_sizes), len(custom_pixelart_sizes)),
        ]
    )

    image_dates = np.sort(np.array([
        mktime(fasttime.parse_datetime(t).date().timetuple())
        for t in image_timestamps.astype("datetime64[s]").astype(str)
    ])).astype(int)

    # Status ID
    temp_status_id = rng.choice(
        a=range(7),
        size=batch_size,
        p=[0.05, 0.01, 0.02, 0.74, 0.03, 0.01, 0.14]
    )

    image_status = np.array([
        3 if t < int(mktime(fasttime.parse_datetime("2023-12-21").timetuple())) else temp_status_id[idx]
        for idx, t in enumerate(image_timestamps)
    ])

    # Uploader ID
    uploader_id = time_dependent_random(independent_time=user_timestamps, dependent_time=image_timestamps, random_func=random_func, offset=0)[:, 0]
    if uploader_id.shape[0] != batch_size:
        uploader_id = np.concatenate([np.full(shape=batch_size-uploader_id.shape[0], fill_value=-1), uploader_id])

    # Likes and Dislike
    likes = np.random.geometric(0.01, size=batch_size)
    dislikes = np.random.geometric(0.02, size=batch_size)


    with sql.connect("./database/website_database.db") as con:
        con.executemany(
            """
            INSERT INTO images_table (
                image_id,
                source_url,
                blob_storage_uuid,
                shape,
                upload_timestamp,
                upload_date,
                status_id,
                description,
                uploader_id,
                likes,
                dislikes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            zip(
                index.astype(str), urls.astype(str), blob_uuids,
                image_shape.astype(str), image_timestamps[batch_size*idx:batch_size*(idx+1)].astype(str),
                image_dates.astype(str), image_status.astype(str),
                description, uploader_id.astype(str), likes.astype(str),
                dislikes.astype(str)
            )
        )

del ( 
    batch_size, batch_count, common_aspect_ratios, custom_uncommon_ratios, image_sizes, pixelart_heights, custom_image_heights,
    custom_pixelart_sizes, custom_common_image_sizes, custom_uncommon_image_sizes, ratio, height, idx, urls, blob_uuids,
    image_shape, image_timestamps, image_dates, temp_status_id, image_status, uploader_id, likes, dislikes,
    description, index, user_count, start_time, end_time, batch_timediff, user_timestamps
)