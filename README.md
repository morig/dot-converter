# Pixel Art Converter

This application allows you to convert uploaded images into pixel art. You can specify the output size and choose colors from a palette to further customize your artwork.

## How to Run

Follow these steps to set up and run the application locally.

### Prerequisites

Make sure you have the following installed:

*   **Node.js:** (LTS version recommended)
*   **npm** (comes with Node.js) or **pnpm**
*   **Python 3:** (Version 3.7 or higher recommended)
*   **pip** (comes with Python)

### 1. Install Python Dependencies

The backend uses a Python script for image processing. Install the necessary Python libraries:

```bash
pip install Pillow numpy scikit-learn scikit-image
```

### 2. Install Node.js Dependencies

Navigate to the project's root directory in your terminal and install the Node.js dependencies:

Using npm:
```bash
npm install
```

Or using pnpm:
```bash
pnpm install
```
*(If you encounter issues with peer dependencies, you might need to use `npm install --legacy-peer-deps` or configure pnpm accordingly.)*

### 3. Run the Application

Once the dependencies are installed, you can start the Next.js development server:

Using npm:
```bash
npm run dev
```

Or using pnpm:
```bash
pnpm dev
```

### 4. Access the Application

After the server starts (usually indicated by a message like `✓ Ready in ...ms` and `event - compiled client and server successfully in ... ms`), open your web browser and navigate to:

[http://localhost:3000](http://localhost:3000)

You should now see the Pixel Art Converter application running.
