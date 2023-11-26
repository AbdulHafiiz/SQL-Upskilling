# User Experience

## Uploading/Creating an image.

1. User logs into account.
2. User clicks upload button and select image file to upload.
    - can include local files or uri/url to remote files
3. Image is sent to a approval queue to be checked for suitability
    - users with elevated privileges will decide if an image is accepted or not
    - will automatically check for duplicate images using perceptual hashing
4. Image is copied and saved in a blob storage along with a uuid for retrieval
5. Partial metadata is inferred and stored in a relational table
    - metadata schema will be consistent across all images
    - the user can update/alter the image metadata
        - users with elevated privileges can also alter the metadata
        - alterations will be logged
6. The user and users with elevated privileges can add or remove tags to the image to classify it
    - registered users can add but not remove tags from the image
    - alterations will be logged
7. After a certain amount of time (6 months), image metadata and tags are 'archived', meaning that elevated permissions are required to alter them
    - after alterations, the data will be 'un-archived' for a short period (3 months)
8. At any step of this process, if an image is rejected, the process halts and the deletion process commences

## Process of deleting an image.
1. Image will be scheduled for deletion after a short period (7 days)
    - a tag will be added to the image, and the image will be hidden from regular users
2. During this period users can appeal the decision, during which the process is paused
    - on approval, the image will be removed from the delete queue and the process continues as usual
    - on rejection the deletion process continues where it left off
3. The appeal process has a time limit (7 days)
    - if no decision is reached, the process will default to a rejection
4. At the end of the deletion schedule, the image is deleted from the blob storage, the metadata and tags are also removed
    - the image id is kept and a note is placed on the page explaining the reason for the deletion

## Individual image display.
1. Images are displayed alongside some metadata and all tags
2. Registered users can interact with the image, unregistered users can only see the image, data and tags
    - registered users can comment, like, dislike or bookmark the image
        - the bookmarked images will accessible by user from a folder on their home page
    - comments will be display to all users
        - registered users will be able to like, dislike and report comments
        - users with elevated privileges will be able to remove comments
    - tags can be added to the image
        - only users with elevated privileges will be able to remove tags

## Process of reporting an image.
1. Users goes to an individual image display and clicks the report button
    - reporting an image adds it to the report queue
    - the report queue has no time limit unlike the delete queue
    - registered users can create reports
    - elevated privileged users can close and act on reports
2. No action is taken against an image or comment if a report is not processed