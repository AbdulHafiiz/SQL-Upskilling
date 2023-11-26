# User Experience

#### Terms
Mods:
 - umbrella term to refer to moderators and admins (see DataModelling/User Object/User Permissions)
Regular Users:
 - umbrella term to refer to users who are not moderators or admins
OP:
 - an abbreviation of the phrase 'Original Poster'
 - refers to the user that initiates the action
    = e.g. the OP of 'Uploading/Creating an image' is the user who initially uploaded the image


## Uploading/Creating an image.

1. OP logs into account.
2. OP clicks upload button and select image file to upload.
    - can include local files or uri/url to remote files
3. Image is sent to a approval queue to be checked for suitability
    - mods will decide if an image is accepted or not
    - will automatically check for duplicate images using perceptual hashing
4. Image is copied and saved in a blob storage along with a uuid for retrieval
5. Partial metadata is inferred and stored in a relational table
    - metadata schema will be consistent across all images
    - OP can update/alter the image metadata
        - mods can also alter the metadata
        - all alterations will be logged
6. OP and mods can add or remove tags to the image to classify it
    - other registered users can add but not remove tags from the image
    - all alterations will be logged
7. After a certain amount of time (variable ~6 months) the image will be marked as 'archived'
    - OP and regular users are unable to alter the image tags/metadata 
    - only mods are able to alter the image tags and metadata
    - after any alterations, the data will be 'un-archived' for a period (variable ~3 months)
8. At any step of this process, if an image is rejected, the upload process halts and the deletion process starts

## Process of deleting an image.

1. Image will be added to a deletion queue
    - the image will be deleted after period (variable ~7 days) has passed
    - a special deleted tag will be added to the image, and the image will be hidden from regular users
2. During this image OP can appeal the decision, during which the process is paused
    - the approval process will be overseen by mods
    - on approval, the image will be removed from the delete queue
    - on rejection the deletion process continues where it left off
3. The appeal process has a time limit (variable ~7 days)
    - if no decision is reached, the decision will default to a rejection
4. At the end of the deletion schedule, the image is deleted from the blob storage, the metadata and tags are scrubbed
    - the image id is kept and a note is placed on the page explaining the reason for the deletion (if provided)

## Displaying individual images.

1. Images are displayed alongside some metadata and all tags
2. Registered users can interact with the image, unregistered users can only see the image, data and tags
    - registered users can comment, like, dislike or bookmark the image
        - the bookmarked images will accessible by user from a folder on their home page
    - comments will be display to all users
        - registered users will be able to like, dislike and report comments
        - mods will be able to remove comments
    - registered users can add tags to the image
        - only mods will be able to remove tags

## Reporting an image.

1. Users goes to an individual image display and clicks the report button
    - reporting an image adds it to the report queue
    - the report queue has no time limit unlike the delete queue
    - unregistered users cannot create reports
    - mods can close and act on reports
2. No action is taken against an image or comment if a report is not processed