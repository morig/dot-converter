import { type NextRequest, NextResponse } from "next/server"
import { spawn } from "child_process"
import path from "path"

export async function POST(request: NextRequest) {
  try {
    const { image, size, position, scale, colorPalette, maxColors } = await request.json()

    const scriptPath = path.join(process.cwd(), "scripts", "pixel_art_converter.py")
    const pythonExecutable = "python3" // Prefer python3

    return new Promise((resolve, reject) => {
      const pythonProcess = spawn(pythonExecutable, [scriptPath])

      let stdoutData = ""
      let stderrData = ""

      pythonProcess.stdin.write(
        JSON.stringify({
          image_data: image, // Python script expects 'image_data'
          size,
          position, // Pass through, even if not used by script currently
          scale,    // Pass through
          color_palette: colorPalette, // Python script expects 'color_palette'
          max_colors: maxColors, // Pass to Python script, snake_case
        }),
      )
      pythonProcess.stdin.end()

      pythonProcess.stdout.on("data", (data) => {
        stdoutData += data.toString()
      })

      pythonProcess.stderr.on("data", (data) => {
        stderrData += data.toString()
      })

      pythonProcess.on("close", (code) => {
        if (code !== 0) {
          console.error(`Python script exited with code ${code}: ${stderrData}`)
          resolve(
            NextResponse.json(
              { error: `Failed to process image. Script error: ${stderrData || "Unknown error"}` },
              { status: 500 },
            ),
          )
          return
        }

        if (stderrData) {
          // Sometimes warnings or other non-fatal messages can go to stderr
          console.warn(`Python script stderr: ${stderrData}`)
        }

        try {
          const result = JSON.parse(stdoutData)
          resolve(NextResponse.json({ pixelArt: result.pixelArt, usedColors: result.usedColors }))
        } catch (parseError) {
          console.error("Error parsing Python script output:", parseError)
          console.error("Python script stdout:", stdoutData)
          resolve(
            NextResponse.json(
              { error: "Failed to parse output from image processing script." },
              { status: 500 },
            ),
          )
        }
      })

      pythonProcess.on("error", (err) => {
        console.error("Failed to start Python script:", err)
        // Attempt to run with 'python' if 'python3' fails
        if ((err as any).code === 'ENOENT' && pythonExecutable === 'python3') {
          console.log("Python3 not found, trying with python...")
          const fallbackProcess = spawn("python", [scriptPath]);
          // Re-pipe and re-attach listeners (simplified for brevity, ideally refactor this)
          fallbackProcess.stdin.write(
            JSON.stringify({
              image_data: image,
              size,
              position,
              scale,
              color_palette: colorPalette,
              max_colors: maxColors, // Pass to Python script (fallback)
            }),
          );
          fallbackProcess.stdin.end();

          let fallbackStdoutData = "";
          let fallbackStderrData = "";

          fallbackProcess.stdout.on("data", (data) => {
            fallbackStdoutData += data.toString();
          });
          fallbackProcess.stderr.on("data", (data) => {
            fallbackStderrData += data.toString();
          });

          fallbackProcess.on("close", (fallbackCode) => {
            if (fallbackCode !== 0) {
              console.error(`Python (fallback) script exited with code ${fallbackCode}: ${fallbackStderrData}`);
              resolve(
                NextResponse.json(
                  { error: `Failed to process image (fallback). Script error: ${fallbackStderrData || "Unknown error"}` },
                  { status: 500 },
                ),
              );
              return;
            }
            try {
              const fallbackResult = JSON.parse(fallbackStdoutData);
              resolve(NextResponse.json({ pixelArt: fallbackResult.pixelArt, usedColors: fallbackResult.usedColors }));
            } catch (parseError) {
              console.error("Error parsing Python (fallback) script output:", parseError);
              resolve(
                NextResponse.json(
                  { error: "Failed to parse output from image processing script (fallback)." },
                  { status: 500 },
                ),
              );
            }
          });
          fallbackProcess.on("error", (fallbackErr) => {
             console.error("Failed to start Python script (fallback python):", fallbackErr)
             resolve(
                NextResponse.json(
                { error: "Failed to start image processing script. Ensure Python is installed and in PATH." },
                { status: 500 },
                ),
             )
          });
          return;
        }
        resolve(
          NextResponse.json(
            { error: "Failed to start image processing script. Ensure Python is installed and in PATH." },
            { status: 500 },
          ),
        )
      })
    })
  } catch (error) {
    console.error("Error processing pixel art request:", error)
    // Ensure a response is sent even for top-level errors
    return NextResponse.json({ error: "Failed to create pixel art due to an internal server error." }, { status: 500 })
  }
}
