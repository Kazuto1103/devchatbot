# DevChatbot API Documentation (Proxy Mode)

This API Engine allows you to integrate the Pangkal Pinang City Chatbot into any application (Web, Mobile, etc.).
**Auth Mode**: Proxy. The Engine holds the real Gemini Credentials. Clients use a `CHATBOT_ACCESS_KEY`.

**Base URL**: `http://localhost:5000` (or your deployed server address)

---

## Endpoints

### 1. Check Service Status

**URL**: `/api/status`
**Method**: `GET`
**Description**: Verifies if the API engine is running.
**Response**:

```json
{ "status": "online", "service": "DevChatbot API", ... }
```

---

### 2. Send Message (Chat)

**URL**: `/api/chat`
**Method**: `POST`
**Description**: Sends a user message to the bot. Requires your custom Access Key.

**Headers**:

- `Content-Type`: `application/json`

**Request Body (JSON):**
| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `apiKey` | string | **Yes** | Your **Chatbot Access Key** (defined in `.env` as `CHATBOT_ACCESS_KEY`). |
| `message` | string | **Yes** | The user's question or message. |
| `history` | array | No | List of previous messages for context. |

**Example Request:**

```json
{
  "apiKey": "dev-token-secret-123",
  "message": "Apa itu Senyum?",
  "history": []
}
```

**Response (200 OK):**

```json
{
  "text": "Senyum adalah singkatan dari Sejahtera, Nyaman, Unggul dan Mandiri..."
}
```

**Error Responses:**

- **401 Unauthorized**: Invalid `apiKey` (Access Key).
- **500 Internal Server Error**: Server-side misconfiguration (Missing `GEMINI_API_KEY`).

### 3. Send Message (GET via Postman/Browser)

**URL**: `/api/chat`
**Method**: `GET`
**Description**: Quick endpoint for testing via browser or Postman without a body.

**Query Parameters:**
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `apiKey` | string | **Yes** | Your **Chatbot Access Key**. |
| `message` | string | **Yes** | The user's question. |
| `stream` | boolean | No | Default `true`. Set to `false` for JSON response. |

**Example URL:**
`http://localhost:5000/api/chat?apiKey=dev-token-secret-123&message=Halo`

---

## Integration Guide (Example using Fetch API)

To use this in your other "Dummy Web Chatbot":

```javascript
const ACCESS_KEY = "dev-token-secret-123"; // Must match .env on server

async function sendMessageToEngine(userMessage) {
  try {
    const response = await fetch('http://localhost:5000/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        apiKey: ACCESS_KEY,
        message: userMessage,
        history: []
      })
    });

    // Handle response...
```
