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

-- Commit changes NOW (before verification to avoid encoding issues on Windows)
COMMIT;

-- ==============================================
-- 3. Verification Queries (run separately)
-- ==============================================
-- Summary counts only (no Vietnamese characters to avoid encoding issues)
SELECT 
    (SELECT COUNT(*) FROM public.users WHERE avatar_url LIKE 'https://travel-img-drive.s3%') AS users_s3,
    (SELECT COUNT(*) FROM public.place_images WHERE image_url LIKE 'https://travel-img-drive.s3%') AS images_s3;

