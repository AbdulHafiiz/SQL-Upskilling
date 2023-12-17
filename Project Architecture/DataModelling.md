# Data Modeling

## Image Object
 - can be created and deleted
 - the underlying image will be static
 - the link to the original artist's post will be different from the link to the image mirror in blob storage

 - ### Image Metadata
    - some details like image size/resolution, upload date should be static
    - some details like number of image state/status should be dynamic

 - ### Image Tags
    - dynamic
    - will be considered different from Image Metadata and as a type of supporting data
    - can be further broken down to subtypes (foreground, background, character, author etc.)
    - will serve as aggregators (allow users to search for art by tags)

 - ### User Interactions
    - users can bookmark images or like images (separate category from image metadata)
    - images can be viewed by users
    - all users can add comment on any image at any point in time
    - all users can delete their own comments

## Comment Object
 - can be created by users
 - can be updated/edited and deleted by the original writer
 - must be attached to an Image Object

 - ### Comment Metadata
    - some details like upload date should be static
    - some details like edited date, content or User Object should be dynamic
        - writer should be dynamic because User Objects can be deleted

## User Object
 - can be created and deleted
 - have multiple types based on permissions/privileges

 - ### User Metadata
    - some details like login credentials should be semi-static
    - some details like user permissions should be dynamic

 - ### Object Interactions
    - can create images and comments that are not intrinsically connected to the User
        - meaning deleting a User Object will not delete the associated Image or Comment Object
        - will just remove the User Object data
    - can like/dislike or bookmark images

 - ### User Permissions
    - consists of 4 types:
        - unregistered users, transient and no data is kept
        - registered users, can create comments, images, and raise reports & requests
        - moderators, can approve reports and requests, as well as delete comments and users
        - admins, no restrictions
    - used for access management