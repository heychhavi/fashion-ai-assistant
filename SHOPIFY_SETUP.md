# Shopify API Setup Guide

This guide will help you set up your Shopify store and API access for the AI Wardrobe application. We use Shopify's Storefront API to search for products and provide outfit recommendations.

## Prerequisites

1. You must have a Shopify store. If you don't have one:
   - Sign up at [Shopify.com](https://www.shopify.com)
   - Start a free trial or activate your subscription
   - Set up your store with products

2. Your store must have products with:
   - Clear titles and descriptions
   - Accurate pricing
   - Product images
   - Proper categorization (e.g., shirts, dresses, etc.)

## Setting up the Storefront API

The Storefront API allows our application to search and display your products. Here's how to set it up:

### Step 1: Create a Custom App

1. Log into your [Shopify Admin Dashboard](https://admin.shopify.com)
2. Go to **Settings** > **Apps and sales channels**
3. Click **Develop apps** in the top right corner
4. Click **Create an app**
5. Enter the following details:
   - App name: `AI Wardrobe Integration`
   - App developer: Your name or organization
   - Emergency developer email: Your email
6. Click **Create app**

### Step 2: Configure API Access

1. In your new app's settings, find **API credentials**
2. Click **Configure Storefront API scopes**
3. Enable these permissions:
   - ✓ `unauthenticated_read_product_listings`
   - ✓ `unauthenticated_read_product_inventory`
4. Click **Save**

### Step 3: Get Your API Token

1. Still in API credentials, find **Storefront API access token**
2. Click **Install app** if prompted
3. Click **Reveal token once**
4. **IMPORTANT**: Copy this token immediately! It won't be shown again

### Step 4: Get Your Store URL

1. Your store URL is in the format: `your-store.myshopify.com`
2. Find it in your browser's address bar when logged into Shopify Admin
3. Only copy the domain part (e.g., `fashion-store.myshopify.com`)
4. Do not include `http://` or `https://`

## Setting Up Your Environment

### Step 1: Create Your .env File

1. Copy the `.env.example` file to create `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and update these values:
   ```bash
   # Your store's URL (e.g., fashion-store.myshopify.com)
   SHOPIFY_STORE_URL=your-store.myshopify.com

   # Your Storefront API token from Step 3 above
   SHOPIFY_STOREFRONT_TOKEN=your_token_here
   ```

### Step 2: Test Your Setup

1. Run the test script:
   ```bash
   python test_shopify_updated.py
   ```

2. You should see:
   - Successful connection to your store
   - List of test products
   - No authorization errors

## Troubleshooting

### Common Errors

1. **401 Unauthorized**
   - Check your Storefront API token is correct
   - Ensure you've enabled the required API scopes
   - Try creating a new token

2. **Invalid Store URL**
   - Must end with `.myshopify.com`
   - Remove `http://` or `https://`
   - Remove any trailing slashes

3. **No Products Found**
   - Verify your store has published products
   - Check product visibility settings
   - Try different search terms

### Need Help?

1. Review the [Shopify Storefront API docs](https://shopify.dev/api/storefront)
2. Check your store's [API health dashboard](https://shopify.dev/api/usage/rate-limits)
3. Contact Shopify support if issues persist
