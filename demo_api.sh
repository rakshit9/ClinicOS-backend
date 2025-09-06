#!/bin/bash

# FastAPI Authentication API Demo Script
# Make sure the server is running on http://127.0.0.1:8000

echo "🚀 FastAPI Authentication API Demo"
echo "=================================="

BASE_URL="http://127.0.0.1:8000"
EMAIL="demo@example.com"
PASSWORD="DemoPass123!"

echo ""
echo "1. Health Check"
echo "---------------"
curl -s "$BASE_URL/health" | jq '.'

echo ""
echo "2. Register New User"
echo "-------------------"
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"Demo User\",
    \"email\": \"$EMAIL\",
    \"password\": \"$PASSWORD\",
    \"role\": \"doctor\"
  }")

echo "$REGISTER_RESPONSE" | jq '.'

# Extract tokens
ACCESS_TOKEN=$(echo "$REGISTER_RESPONSE" | jq -r '.tokens.access')
REFRESH_TOKEN=$(echo "$REGISTER_RESPONSE" | jq -r '.tokens.refresh')

echo ""
echo "3. Login User"
echo "-------------"
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$EMAIL\",
    \"password\": \"$PASSWORD\"
  }")

echo "$LOGIN_RESPONSE" | jq '.'

# Update tokens from login
ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.tokens.access')
REFRESH_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.tokens.refresh')

echo ""
echo "4. Get Current User (Protected Route)"
echo "------------------------------------"
curl -s -X GET "$BASE_URL/api/auth/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq '.'

echo ""
echo "5. Refresh Access Token"
echo "----------------------"
REFRESH_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/refresh" \
  -H "Content-Type: application/json" \
  -d "{
    \"refreshToken\": \"$REFRESH_TOKEN\"
  }")

echo "$REFRESH_RESPONSE" | jq '.'

# Update access token
ACCESS_TOKEN=$(echo "$REFRESH_RESPONSE" | jq -r '.access')

echo ""
echo "6. Test Protected Route with New Token"
echo "-------------------------------------"
curl -s -X GET "$BASE_URL/api/auth/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq '.'

echo ""
echo "7. Forgot Password"
echo "-----------------"
curl -s -X POST "$BASE_URL/api/auth/forgot-password" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$EMAIL\"
  }" | jq '.'

echo ""
echo "8. Logout"
echo "--------"
curl -s -X POST "$BASE_URL/api/auth/logout" \
  -H "Content-Type: application/json" \
  -d "{
    \"refreshToken\": \"$REFRESH_TOKEN\"
  }"

echo ""
echo "✅ Demo completed successfully!"
echo ""
echo "📚 Interactive API Documentation:"
echo "   Swagger UI: $BASE_URL/docs"
echo "   ReDoc: $BASE_URL/redoc"
