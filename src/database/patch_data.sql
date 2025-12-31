-- ==============================================
-- DATA PATCHING SCRIPT FOR S3 MIGRATION
-- ==============================================
-- Run this script AFTER importing init.sql to RDS
-- Purpose: Update image paths from local to S3 URLs
-- 
-- S3 Bucket: travel-img-drive
-- S3 URL: https://travel-img-drive.s3.ap-southeast-1.amazonaws.com/uploads/
-- ==============================================

-- Start transaction for safety
BEGIN;

-- ==============================================
-- 1. Update users.avatar_url
-- ==============================================
-- Replace '/static/uploads/' with S3 URL
UPDATE public.users
SET avatar_url = REPLACE(
    avatar_url,
    '/static/uploads/',
    'https://travel-img-drive.s3.ap-southeast-1.amazonaws.com/uploads/'
)
WHERE avatar_url IS NOT NULL
  AND avatar_url LIKE '%/static/uploads/%';

-- Also handle paths without leading slash
UPDATE public.users
SET avatar_url = REPLACE(
    avatar_url,
    'static/uploads/',
    'https://travel-img-drive.s3.ap-southeast-1.amazonaws.com/uploads/'
)
WHERE avatar_url IS NOT NULL
  AND avatar_url LIKE 'static/uploads/%';

-- Show affected rows
DO $$
DECLARE
    user_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO user_count FROM public.users 
    WHERE avatar_url LIKE 'https://travel-img-drive.s3%';
    RAISE NOTICE '[users] Updated % avatar_url paths to S3', user_count;
END $$;

-- ==============================================
-- 2. Update place_images.image_url
-- ==============================================
-- Replace '/static/uploads/' with S3 URL
UPDATE public.place_images
SET image_url = REPLACE(
    image_url,
    '/static/uploads/',
    'https://travel-img-drive.s3.ap-southeast-1.amazonaws.com/uploads/'
)
WHERE image_url IS NOT NULL
  AND image_url LIKE '%/static/uploads/%';

-- Also handle paths without leading slash
UPDATE public.place_images
SET image_url = REPLACE(
    image_url,
    'static/uploads/',
    'https://travel-img-drive.s3.ap-southeast-1.amazonaws.com/uploads/'
)
WHERE image_url IS NOT NULL
  AND image_url LIKE 'static/uploads/%';

-- Show affected rows
DO $$
DECLARE
    image_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO image_count FROM public.place_images 
    WHERE image_url LIKE 'https://travel-img-drive.s3%';
    RAISE NOTICE '[place_images] Updated % image_url paths to S3', image_count;
END $$;

-- ==============================================
-- 3. Verification Queries
-- ==============================================
-- Run these to verify the changes

-- Check sample users avatars
SELECT id, full_name, 
       CASE 
           WHEN avatar_url IS NULL THEN 'NULL'
           ELSE LEFT(avatar_url, 60) || '...'
       END AS avatar_preview
FROM public.users 
WHERE avatar_url IS NOT NULL 
LIMIT 5;

-- Check sample place images
SELECT id, place_id, 
       CASE 
           WHEN image_url IS NULL THEN 'NULL'
           ELSE LEFT(image_url, 70) || '...'
       END AS image_preview,
       is_main
FROM public.place_images 
LIMIT 10;

-- Summary counts
SELECT 
    (SELECT COUNT(*) FROM public.users WHERE avatar_url LIKE 'https://travel-img-drive.s3%') AS users_with_s3_avatar,
    (SELECT COUNT(*) FROM public.place_images WHERE image_url LIKE 'https://travel-img-drive.s3%') AS images_with_s3_url,
    (SELECT COUNT(*) FROM public.users WHERE avatar_url NOT LIKE 'https://%' AND avatar_url IS NOT NULL) AS users_old_path,
    (SELECT COUNT(*) FROM public.place_images WHERE image_url NOT LIKE 'https://%' AND image_url IS NOT NULL) AS images_old_path;

-- Commit if everything looks good
COMMIT;

-- ==============================================
-- ROLLBACK (uncomment if needed to undo changes)
-- ==============================================
-- ROLLBACK;
