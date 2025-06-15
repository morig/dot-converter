import { type NextRequest, NextResponse } from "next/server"

export async function POST(request: NextRequest) {
  try {
    const { image, size, position, colorPalette } = await request.json()

    // 実際の実装では、Pythonスクリプトを呼び出してピクセルアートを生成
    // ここではデモ用のダミーデータを返す

    const dummyPixelArt = Array(size)
      .fill(null)
      .map((_, row) =>
        Array(size)
          .fill(null)
          .map((_, col) => {
            // 簡単なパターンを生成
            const colors = ["#FF0000", "#00FF00", "#0000FF", "#FFFFFF", "#000000"]
            const colorNames = ["あか", "みどり", "あお", "しろ", "くろ"]
            const index = (row + col) % colors.length

            return {
              color: colors[index],
              colorName: colorNames[index],
            }
          }),
      )

    const dummyUsedColors = [
      { name: "あか", color: "#FF0000", count: Math.floor((size * size) / 5) },
      { name: "みどり", color: "#00FF00", count: Math.floor((size * size) / 5) },
      { name: "あお", color: "#0000FF", count: Math.floor((size * size) / 5) },
      { name: "しろ", color: "#FFFFFF", count: Math.floor((size * size) / 5) },
      { name: "くろ", color: "#000000", count: Math.floor((size * size) / 5) },
    ]

    return NextResponse.json({
      pixelArt: dummyPixelArt,
      usedColors: dummyUsedColors,
    })
  } catch (error) {
    console.error("Error processing pixel art:", error)
    return NextResponse.json({ error: "Failed to create pixel art" }, { status: 500 })
  }
}
