import numpy as np
import pandas as pd
from math import floor
from uuid import uuid4
from time import mktime
from os import path, mkdir
from random import choices
import ciso8601 as fasttime
from itertools import cycle, permutations, repeat

if not path.exists("./database/csv"):
    mkdir("./database/csv")

rng = np.random.default_rng()


## Time Dependent Random Generator
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


def main():
    ## Status Reference Table (21 rows)
    if not path.exists("./database/csv/status_reference.csv"):
        print("Creating status reference table.")

        try:
            status_reference = [
                {"status_id": 0, "name": "image_pending", "category": "actionable_timed", "description": "Image under review."},
                {"status_id": 1, "name": "image_appealed", "category": "actionable_timed", "description": "Image to be reassessed."},
                {"status_id": 2, "name": "image_reported", "category": "actionable_untimed", "description": "Image reported, pending review."},
                {"status_id": 3, "name": "image_accepted", "category": "decision", "description": "Image approved for display."},
                {"status_id": 4, "name": "image_rejected", "category": "decision", "description": "Image rejected."},
                {"status_id": 5, "name": "image_marked_deletion", "category": "decision", "description": "Image marked for deletion, will automatically delete after 7 days."},
                {"status_id": 6, "name": "image_deleted", "category": "decision_final", "description": "Image deleted, do not display."},
                {"status_id": 7, "name": "user_acceptable", "category": "decision", "description": "User fine, no action neede."},
                {"status_id": 8, "name": "user_reported", "category": "actionable_untimed", "description": "User reported, pending review."},
                {"status_id": 9, "name": "user_muted", "category": "decision", "description": "User muted, cannot post comments or upload images."},
                {"status_id": 10, "name": "user_mute_appeal", "category": "actionable_untimed", "description": "User to be reassessed."},
                {"status_id": 11, "name": "user_banned", "category": "decision_final", "description": "User banned, account access restricted."},
                {"status_id": 12, "name": "comment_acceptable", "category": "decision", "description": "Comment fine, no action neede."},
                {"status_id": 13, "name": "comment_reported", "category": "actionable_untimed", "description": "Comment reported, pending review."},
                {"status_id": 14, "name": "comment_hidden", "category": "decision", "description": "Comment hidden from general view."},
                {"status_id": 15, "name": "comment_deleted", "category": "decision_final", "description": "Comment deleted, do not display."},
                {"status_id": 16, "name": "tag_pending", "category": "actionable_timed", "description": "Tag under review."},
                {"status_id": 17, "name": "tag_appealed", "category": "actionable_timed", "description": "Tag to be reassessed."},
                {"status_id": 18, "name": "tag_reported", "category": "actionable_untimed", "description": "Tag reported, pending review."},
                {"status_id": 19, "name": "tag_accepted", "category": "decision", "description": "Tag approved for use."},
                {"status_id": 20, "name": "tag_rejected", "category": "decision", "description": "Tag rejected for use."}
            ]

            pd.DataFrame.from_records(status_reference).to_csv("./database/csv/status_reference.csv", index=False)
            del status_reference
        except Exception as err:
            print(f"Warning error creating status reference table. {err}")


    ## Permission Reference Table (4 rows)
    if not path.exists("./database/csv/premission_reference.csv"):
        print("Creating permission reference table.")

        try:
            permission_reference = [
                {"permission_id": 0, "name": "basic", "description": "Basic user, no special permissions."},
                {"permission_id": 1, "name": "premium", "description": "Premium user, able to view deleted images."},
                {"permission_id": 2, "name": "moderator", "description": "Moderator, able to act on reports."},
                {"permission_id": 3, "name": "admin", "description": "Administrator."},
            ]

            pd.DataFrame.from_records(permission_reference).to_csv("./database/csv/permission_reference.csv", index=False)
            del permission_reference
        except Exception as err:
            print(f"Warning error creating permission reference table. {err}")


    ## Tags Table (400 rows)
    if not path.exists("./database/csv/tags_table.csv"):
        print("Creating tags table.")

        try:
            with open("./database/setup/reference/nouns.txt", "r") as file:
                nouns = file.read().splitlines()

            tag_names = np.random.choice(a=nouns, size=400)
            tag_count = len(tag_names)
            description = cycle([""])

            tag_categories = cycle(["general"])
            temp_status_id = rng.choice(
                a=[16, 17, 18, 19, 20],
                size=tag_count,
                p=[0.15, 0.01, 0.01, 0.71, 0.12]
            )

            creation_timestamps = np.sort(np.random.randint(
                low=int(mktime(fasttime.parse_datetime("2009-05-14").timetuple())),
                high=int(mktime(fasttime.parse_datetime("2023-12-28").timetuple())),
                size=tag_count
            ))

            tag_status = [
                19 if t < mktime(fasttime.parse_datetime("2021-04-03").timetuple()) else temp_status_id[idx]
                for idx, t in enumerate(creation_timestamps)
            ]

            tags = sorted([*zip(range(tag_count), tag_categories, tag_names, description, tag_status, creation_timestamps)], key=lambda x: x[-1])
            pd.DataFrame(tags, columns=["tag_id", "type_category", "name", "description", "status_id", "creation_timestamp"]).to_csv("./database/csv/tags_table.csv", index=False)

            del tag_names, tag_categories, temp_status_id, creation_timestamps, tag_status, tag_count, tags, description
        except Exception as err:
            print(f"Warning error creating tags table. {err}")


    ## Users Table (50,000 rows)
    if not path.exists("./database/csv/users_table.csv"):
        print("Creating users table.")

        try:
            user_count = 50_000
            string = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+_"
            usernames = np.apply_along_axis(
                func1d=lambda x:"".join(x),
                axis=1,
                arr=rng.choice(a=list(string), size=(user_count, 14))
            )

            user_timestamps = np.sort(np.random.randint(
                low=int(mktime(fasttime.parse_datetime("2009-05-14").timetuple())),
                high=int(mktime(fasttime.parse_datetime("2023-12-28").timetuple())),
                size=user_count-120
            ))
            # Inject initial 120 users as preregistered users
            user_timestamps = np.concatenate([
                [int(mktime(fasttime.parse_datetime("2009-05-14").timetuple())) for _ in range(120)],
                user_timestamps
            ])

            temp_status_id = rng.choice(
                a=range(7, 12),
                size=user_count,
                p=[0.88, 0.01, 0.02, 0.01, 0.08]
            )

            status_id = [
                7 if t < mktime(fasttime.parse_datetime("2023-12-22").timetuple()) else temp_status_id[idx]
                for idx, t in enumerate(user_timestamps)
            ]

            permission_level = rng.choice(
                a=range(4),
                size=user_count,
                p=[0.832388, 0.166522, 0.001064, 0.000026]
            )


            pd.DataFrame(
                zip(range(user_count), usernames, user_timestamps, status_id, permission_level),
                columns=["user_id", "username", "creation_timestamp", "status_id", "permission_id"]
            ).to_csv("./database/csv/users_table.csv", index=False)
            del string, usernames, user_timestamps, temp_status_id, status_id, permission_level, user_count
        except Exception as err:
            print(f"Warning error creating users table. {err}")


    ## Images Timestamp Table (1,000,000 rows)
    if not path.exists("./database/csv/image_timestamps.csv"):
        print("Creating image timestamps table.")

        try:
            start_time = mktime(fasttime.parse_datetime("2009-05-20").timetuple())
            end_time = mktime(fasttime.parse_datetime("2023-12-28").timetuple())

            image_timestamps = np.sort(np.random.randint(
                low=floor(start_time),
                high=floor(end_time),
                size=1_000_000
            ))

            with open("./database/csv/image_timestamps.csv", "w") as file:
                file.writelines("\n".join(image_timestamps.astype(str)))

            del start_time, end_time, image_timestamps, file
        except Exception as err:
            print(f"Warning error creating images table. {err}")


    ## Comments Table (2,500,000 rows)
    if not path.exists("./database/csv/comments_table.csv"):
        print("Creating comments table.")

        try:
            batch_size = 100_000
            batch_count = 2_500_000//batch_size
            start_time = mktime(fasttime.parse_datetime("2009-05-20").timetuple())
            end_time = mktime(fasttime.parse_datetime("2023-12-28").timetuple())
            batch_timediff = (end_time - start_time)/batch_count

            string = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"

            # Newline padding
            newline_padding = cycle("\n")

            with open("./database/csv/comments_table.csv", "a+") as file:
                file.write("comment_id,status_id,content,creation_timestamp,edited,likes,dislikes\n")

                for idx in range(batch_count):
                    index = np.arange(batch_size*idx, batch_size*(idx+1)).astype(str)

                    comment_content = np.apply_along_axis(
                        func1d=lambda x: " ".join(x),
                        axis=1,
                        arr=np.apply_along_axis(
                            func1d=lambda x:"".join(x),
                            axis=1,
                            arr=rng.choice(a=list(string), size=(batch_size, 6, 8))
                        )
                    )

                    comment_timestamps = np.sort(np.random.randint(
                        low=start_time+batch_timediff*idx,
                        high=start_time+batch_timediff*(idx+1),
                        size=batch_size
                    ))

                    temp_status_id = rng.choice(
                        a=range(12, 16),
                        size=batch_size,
                        p=[0.97, 0.0015, 0.0085, 0.02]
                    )

                    image_status = np.array([
                        12 if t < int(mktime(fasttime.parse_datetime("2023-12-21").timetuple())) else temp_status_id[idx]
                        for idx, t in enumerate(comment_timestamps)
                    ])

                    comment_edited = np.random.randint(low=0, high=2, size=batch_size)
                    comment_likes = np.random.geometric(0.1, size=batch_size)
                    comment_dislikes = np.random.geometric(0.2, size=batch_size)

                    file.writelines(
                        (
                            ",".join(row)+"\n"
                            for row
                            in zip(
                                index,
                                temp_status_id.astype(str), comment_content.astype(str), comment_timestamps.astype(str),
                                comment_edited.astype(str), comment_likes.astype(str), comment_dislikes.astype(str)
                            )
                        )
                    )

            del (
                batch_size, batch_count, newline_padding, file, idx, temp_status_id,
                image_status, comment_content, comment_timestamps, comment_edited,
                comment_likes, comment_dislikes, index, string, start_time, end_time,
                batch_timediff
            )
        except Exception as err:
            print(f"Warning error creating comments table. {err}")


    ## Image Tag Junction Table
    if not path.exists("./database/csv/image_tag_junction.csv"):
        print("Creating image tag junction table.")

        try:
            batch_size = 100_000
            tag_timestamps = pd.read_csv("./database/csv/tags_table.csv", usecols=["creation_timestamp"]).to_numpy()
            random_func = lambda size: np.random.lognormal(mean=np.log(3), sigma=0.5, size=size)
            image_timestamps = np.transpose(pd.read_csv("./database/csv/image_timestamps.csv").to_numpy())[0]

            with open("./database/csv/image_timestamps.csv", "r") as image_file, open("./database/csv/image_tag_junction.csv", "a+") as output_file:
                # Batched data processing
                for batch_idx in range(image_timestamps.shape[0]//batch_size):
                    
                    # Loading batched data from csv file
                    result = time_dependent_random(
                        independent_time=tag_timestamps,
                        dependent_time=image_timestamps[batch_size*batch_idx:batch_size*(batch_idx+1)],
                        random_func=random_func,
                        offset=batch_idx*batch_size
                    ).astype(int)
                    result = np.vstack(sorted(np.unique(result, axis=0), key=lambda x: x[1])).astype(str)

                    output_file.writelines(
                        ",".join(row)+"\n"
                        for row
                        in result
                    )
            del batch_idx, batch_size, image_timestamps, output_file, random_func, tag_timestamps, result
        except Exception as err:
            raise err
            print(f"Warning error creating image tag junction table. {err}")


    ## User Comments Junction Table
    if not path.exists("./database/csv/user_comments_junction.csv"):
        print("Creating user comments junction table.")

        try:
            batch_size = 100_000
            batch_count = 2_500_000//batch_size
            user_timestamps = np.transpose(pd.read_csv("./database/csv/users_table.csv", usecols=["creation_timestamp"]).to_numpy())[0]
            random_func = lambda size: np.zeros(shape=size)

            with open("./database/csv/comments_table.csv", "r") as comment_file, open("./database/csv/user_comment_junction.csv", "a+") as output_file:
                # Removing headers
                comment_file.readline()

                # Batched data processing
                for batch_idx, batch_line in enumerate(comment_file):
                    
                    # Loading batched data from csv file
                    comment_line = [comment_file.readline() for _ in range(batch_size)]
                    comment_timestamps = []
                    for line in comment_line:
                        try:
                            comment_timestamps.append(line[1:-1].split(",")[3])
                        except:
                            pass
                    comment_timestamps = np.array(comment_timestamps).astype(int)

                    output_file.writelines(
                        ",".join(row)+"\n"
                        for row
                        in time_dependent_random(
                            independent_time=user_timestamps,
                            dependent_time=comment_timestamps,
                            random_func=random_func,
                            offset=batch_idx*batch_size
                        ).astype(str)
                    )
            del (
                batch_size, batch_count, user_timestamps, random_func, comment_file, output_file,
                batch_idx, line, comment_line, comment_timestamps, comment_line
            )
        except Exception as err:
            print(f"Warning error creating user comments junction table. {err}")


    ## User Favourites Junction Table
    if not path.exists("./database/csv/user_favourites_junction.csv"):
        print("Creating user favourites junction table.")

        try:
            user_timestamps = np.transpose(pd.read_csv("./database/csv/users_table.csv", usecols=["creation_timestamp"]).to_numpy())[0]
            with open("./database/csv/user_favourites_junction.csv", "a+") as output_file:
                # Removing headers
                user_timestamps = np.transpose(pd.read_csv("./database/csv/users_table.csv", usecols=["creation_timestamp"]).to_numpy())[0]

                user_fave_count = np.round(
                        np.power(
                            np.log1p(
                                np.log1p(
                                    np.floor_divide(
                                        (mktime(fasttime.parse_datetime("2023-12-28").timetuple()) - user_timestamps),
                                        86400
                                    )
                                )
                            ) + 0 + 3*rng.random(size=user_timestamps.shape[0]),
                            3
                        )
                    ).astype(int)


                result = np.column_stack((
                    np.repeat(np.arange(0, user_timestamps.shape[0]), user_fave_count),
                    np.random.choice(np.arange(0, 1_000_000), size=user_fave_count.sum()).astype(int)
                ))

                result = np.vstack(sorted(np.unique(result, axis=0), key=lambda x: 1_000_000*x[0]+x[1])).astype(str)

                output_file.writelines(
                    ",".join(row)+"\n"
                    for row
                    in result
                )
            del output_file, result, user_fave_count, user_timestamps
        except Exception as err:
            print(f"Warning error creating user favourites junction table. {err}")


if __name__ == "__main__":
    main()