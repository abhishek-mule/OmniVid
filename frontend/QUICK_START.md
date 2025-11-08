## Backend Quick Start

This guide will get you started with the backend of the OmniVid project. The backend is responsible for the core AI and video processing functionalities.

### Prerequisites

- Docker
- An IDE that supports the devcontainer spec (like VSCode)

### Getting Started

1.  **Clone the repository**

    ```bash
    git clone https://github.com/your-username/omnivid.git
    cd omnivid
    ```

2.  **Open in Devcontainer**

    Open the project in your IDE. If you're using VSCode, it should automatically prompt you to reopen the project in a devcontainer. This will build the Docker image and install all the necessary dependencies.

3.  **Run the Backend**

    Once the devcontainer is up and running, you can start the backend with the following command:

    ```bash
    python main.py
    ```

    This will start the backend server on `http://localhost:8000`.

### API

The backend exposes a single API endpoint:

- `POST /generate`

  This endpoint accepts a JSON payload with the following structure:

  ```json
  {
    "script": "Your video script here"
  }
  ```

  The `script` field should contain the text that you want to convert into a video.

  You can use `curl` to test the endpoint:

  ```bash
  curl -X POST -H "Content-Type: application/json" -d '{"script": "Hello, world!"}' http://localhost:8000/generate
  ```

## Frontend Quick Start

This guide will get you started with the frontend of the OmniVid project. The frontend is a Next.js application that provides the user interface for interacting with the video generation platform.

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Copy environment variables
cp .env.local.example .env.local

# Update with your Supabase credentials
# NEXT_PUBLIC_SUPABASE_URL=your_url
# NEXT_PUBLIC_SUPABASE_ANON_KEY=your_key
```

### Development

```bash
# Start development server
npm run dev

# Open http://localhost:3000
```

### Build

```bash
# Build for production
npm run build

# Start production server
npm start
```
