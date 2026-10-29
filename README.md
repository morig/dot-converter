# Pixel Art Converter

This application allows you to convert uploaded images into pixel art. You can specify the output size and choose colors from a palette to further customize your artwork. Additionally, you can set a maximum number of colors for the final output to simplify the color scheme.

## How to Run

Follow these steps to set up and run the application locally.

### Prerequisites

Make sure you have the following installed:

*   **Node.js:** 20.9 or higher (LTS version recommended)
*   **npm** (comes with Node.js)
*   **Python 3:** 3.10 or higher
*   **pip** (comes with Python) or **uv**

### 1. Install Python Dependencies

The backend uses a Python script for image processing. Create a virtual environment named `.venv` in the project root and install the libraries listed in `requirements.txt`:

Using pip:
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate / macOS, Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Or using uv:
```bash
uv venv
uv pip install -r requirements.txt
```

The API route uses the Python interpreter in `.venv` automatically, so the virtual environment does not need to be activated when starting the server. To use a different interpreter, set the `PYTHON_PATH` environment variable to its path. Without `.venv` or `PYTHON_PATH`, `python3` (`python` on Windows) on `PATH` is used.

### 2. Install Node.js Dependencies

Navigate to the project's root directory in your terminal and install the Node.js dependencies:

```bash
npm install
```

### 3. Run the Application

Once the dependencies are installed, you can start the Next.js development server:

```bash
npm run dev
```

### 4. Access the Application

After the server starts (indicated by a message like `✓ Ready in ...s`), open your web browser and navigate to:

[http://localhost:3000](http://localhost:3000)

You should now see the Pixel Art Converter application running.
