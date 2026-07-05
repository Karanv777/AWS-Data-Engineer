# AWS S3 Image Compression Workflow

This documentation describes the serverless image compression pipeline designed using AWS S3 and AWS Lambda.

## Workflow Overview

The architecture provides an automated, scalable solution for image optimization. A raw image is uploaded to a specific folder in an S3 bucket. This upload triggers an AWS Lambda function which processes the image and saves the optimized version back to a different folder in the same S3 bucket.

***

## Detailed Steps

The following three steps define the end-to-end workflow:

### Step 1: Raw Image Upload

A user or application uploads a full-resolution raw image (e.g., `image.jpg`) to a specific prefix (folder) within the Amazon S3 bucket. This prefix must be clearly defined to distinguish it from processed files.

*   **Action:** Client-side upload.
*   **Destination Prefix:** `s3://[YourBucketName]/raw/`
*   **Example Object Key:** `raw/image.jpg`

### Step 2: Lambda Picks and Compresses

The creation of the raw object in the S3 bucket triggers an event notification (`s3:ObjectCreated:*`). This notification invokes an AWS Lambda function. The function's code (e.g., Python using Pillow or Node.js using Sharp) executes the actual processing.

*   **Trigger:** S3 Event Notification on the `/raw/` prefix.
*   **Lambda Function Actions:**
    1.  **Retrieve:** Reads the event payload to identify the bucket name and file key, then uses the AWS SDK to download the raw image into temporary storage (e.g., `/tmp`).
    2.  **Compress:** Executes the compression logic to resize or reduce the quality of the image while maintaining acceptable visual fidelity.
*   **Execution Location:** AWS Lambda Compute Environment.

### Step 3: Stores Compressed Image

Once the Lambda function successfully creates the optimized, compressed image, it uploads the new object back to the same Amazon S3 bucket, but saves it under a different prefix. This keeps the processed assets separate from the original data.

*   **Action:** Lambda-side upload using the AWS SDK (`PutObject`).
*   **Destination Prefix:** `s3://[YourBucketName]/compressed/`
*   **Example Object Key:** `compressed/image_compressed.jpg`

***

## Architectural Diagram

<img width="2816" height="1536" alt="Gemini_Generated_Image_q96gkiq96gkiq96g" src="https://github.com/user-attachments/assets/f9cf049f-c6b0-4cf4-b78d-46338a4c8cc3" />


