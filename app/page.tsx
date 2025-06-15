"use client"

import type React from "react"

import { useState, useRef, useCallback } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card } from "@/components/ui/card"
import { Upload, Download } from "lucide-react"

// カラーパレット定義
const COLOR_PALETTE = {
  クリーム: "#F2E5C5",
  パステルきいろ: "#F7F5B5",
  レモン: "#FDEE93",
  きいろ: "#FFE835",
  ひまわり: "#FFD900",
  リッチバター: "#FFC400",
  やまぶきいろ: "#FFB300",
  オレンジ: "#FF8C00",
  タンジェリン: "#FF6600",
  トマト: "#FF4500",
  ピーチ: "#FFDAB9",
  フラミンゴ: "#FFC0CB",
  さんごいろ: "#FF7F50",
  しゅいろ: "#EB6100",
  サーモンピンク: "#FA8072",
  ローズ: "#E0648A",
  あか: "#FF0000",
  ラズベリー: "#E30074",
  クランベリー: "#9E1834",
  エッグプラント: "#614051",
  スモーキーピンク: "#E6B4B8",
  さくらいろ: "#FFF0F5",
  コットンキャンディ: "#FFB6C1",
  ピンク: "#FF69B4",
  つつじいろ: "#E75480",
  マゼンタ: "#FF00FF",
  アザミ: "#C7A2C4",
  ラベンダー: "#E6E6FA",
  パステルむらさき: "#DDA0DD",
  むらさき: "#800080",
  トワイライトプラム: "#5E435E",
  ぶどういろ: "#5E2F5E",
  オーキッド: "#DA70D6",
  あお: "#0000FF",
  ミッドナイトブルー: "#191970",
  ラムネ: "#ADD8E6",
  スカイブルー: "#87CEEB",
  ロビンズエッグ: "#00CCCC",
  ミスト: "#E4E1E8",
  パステルあお: "#B0E0E6",
  みずいろ: "#AFDFE4",
  ブルーベリー: "#4F86F7",
  あおむらさき: "#8A2BE2",
  デニム: "#1560BD",
  オーシャンブルー: "#2E86C1",
  ミント: "#BDFCC9",
  うぐいすいろ: "#919E34",
  あおみどり: "#008080",
  クローバー: "#3EA055",
  みどり: "#008000",
  エバーグリーン: "#004000",
  もみのき: "#01642D",
  セロリ: "#B8D8A0",
  セージ: "#9EAB89",
  シャーベット: "#E0F0E0",
  マスカット: "#A8D37A",
  サワーアップル: "#8CDA3F",
  パステルみどり: "#90EE90",
  きみどり: "#9ACD32",
  よもぎいろ: "#99A63C",
  グラスグリーン: "#4E9258",
  オリーブ: "#808000",
  アプリコット: "#FFB380",
  こむぎいろ: "#E5C494",
  キャラメル: "#AF6E4D",
  ハニー: "#FFB200",
  おうどいろ: "#B8860B",
  "ジンジャ―ブレッド": "#C16E2C",
  ちゃいろ: "#964B00",
  こげちゃいろ: "#5C4033",
  ココア: "#8E4B37",
  モカ: "#6F4E37",
  マシュマロ: "#F0E6E6",
  しろ: "#FFFFFF",
  ライトグレー: "#D3D3D3",
  ストーン: "#888C8D",
  はいいろ: "#808080",
  ダークグレイ: "#A9A9A9",
  くろ: "#000000",
  パール: "#EAE0C8",
  シルバー: "#C0C0C0",
  ゴールド: "#FFD700",
  とうめい: "#FFFFFF",
  ラメとうめい: "#FFFFFF",
  ラメきいろ: "#FFFF00",
  ラメあか: "#FF4136",
  ラメむらさき: "#8A2BE2",
  ラメあお: "#1F75FE",
  ラメみどり: "#00FF00",
  夜光オレンジ: "#FF8C00",
  夜光ピンク: "#FF69B4",
  夜光むらさき: "#9932CC",
  夜光あお: "#00BFFF",
  夜光しろ: "#F5F5F5",
}

interface PixelData {
  color: string
  colorName: string
}

interface UsedColor {
  name: string
  color: string
  count: number
}

export default function PixelArtConverter() {
  const [uploadedImage, setUploadedImage] = useState<string | null>(null)
  const [imagePosition, setImagePosition] = useState({ x: 0, y: 0 })
  const [outputSize, setOutputSize] = useState<number>(32)
  const [pixelArt, setPixelArt] = useState<PixelData[][]>([])
  const [selectedColor, setSelectedColor] = useState<string>("")
  const [usedColors, setUsedColors] = useState<UsedColor[]>([])
  const [isProcessing, setIsProcessing] = useState(false)
  const [isDragging, setIsDragging] = useState(false)
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 })
  const [imageScale, setImageScale] = useState<number>(1)

  const fileInputRef = useRef<HTMLInputElement>(null)
  const imageRef = useRef<HTMLImageElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)

  const handleImageUpload = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        const result = e.target?.result as string
        setUploadedImage(result)
        // 背景削除の処理をここに実装（簡略化のため省略）
      }
      reader.readAsDataURL(file)
    }
  }, [])

  const handleImageDragStart = useCallback(
    (e: React.MouseEvent) => {
      setIsDragging(true)
      setDragStart({
        x: e.clientX - imagePosition.x,
        y: e.clientY - imagePosition.y,
      })
    },
    [imagePosition],
  )

  const handleImageDrag = useCallback(
    (e: React.MouseEvent) => {
      if (isDragging) {
        setImagePosition({
          x: e.clientX - dragStart.x,
          y: e.clientY - dragStart.y,
        })
      }
    },
    [isDragging, dragStart],
  )

  const handleImageDragEnd = useCallback(() => {
    setIsDragging(false)
  }, [])

  const createPixelArt = useCallback(async () => {
    if (!uploadedImage) return

    setIsProcessing(true)

    try {
      // Python スクリプトを呼び出してピクセルアートを生成
      const response = await fetch("/api/create-pixel-art", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          image: uploadedImage,
          size: outputSize,
          position: imagePosition,
          scale: imageScale,
          colorPalette: COLOR_PALETTE,
        }),
      })

      const result = await response.json()
      setPixelArt(result.pixelArt)
      setUsedColors(result.usedColors)
    } catch (error) {
      console.error("Error creating pixel art:", error)
      // デモ用のダミーデータ
      const dummyPixelArt: PixelData[][] = Array(outputSize)
        .fill(null)
        .map(() =>
          Array(outputSize)
            .fill(null)
            .map(() => ({
              color: "#FFFFFF",
              colorName: "しろ",
            })),
        )
      setPixelArt(dummyPixelArt)
      setUsedColors([{ name: "しろ", color: "#FFFFFF", count: outputSize * outputSize }])
    }

    setIsProcessing(false)
  }, [uploadedImage, outputSize, imagePosition, imageScale])

  const handlePixelClick = useCallback(
    (row: number, col: number) => {
      if (!selectedColor || pixelArt.length === 0) return

      const colorName =
        Object.keys(COLOR_PALETTE).find((key) => COLOR_PALETTE[key as keyof typeof COLOR_PALETTE] === selectedColor) ||
        "unknown"

      const newPixelArt = [...pixelArt]
      const oldColor = newPixelArt[row][col].color
      const oldColorName = newPixelArt[row][col].colorName

      newPixelArt[row][col] = {
        color: selectedColor,
        colorName: colorName,
      }
      setPixelArt(newPixelArt)

      // 使用色パレットを更新
      const newUsedColors = [...usedColors]
      const oldColorIndex = newUsedColors.findIndex((c) => c.color === oldColor)
      const newColorIndex = newUsedColors.findIndex((c) => c.color === selectedColor)

      if (oldColorIndex !== -1) {
        newUsedColors[oldColorIndex].count--
        if (newUsedColors[oldColorIndex].count === 0) {
          newUsedColors.splice(oldColorIndex, 1)
        }
      }

      if (newColorIndex !== -1) {
        newUsedColors[newColorIndex].count++
      } else {
        newUsedColors.push({ name: colorName, color: selectedColor, count: 1 })
      }

      setUsedColors(newUsedColors)
    },
    [selectedColor, pixelArt, usedColors],
  )

  const downloadResults = useCallback(() => {
    if (pixelArt.length === 0) return

    // メイン表示部をJPGとしてダウンロード
    const canvas = document.createElement("canvas")
    const ctx = canvas.getContext("2d")
    if (!ctx) return

    const pixelSize = 10
    canvas.width = pixelArt[0].length * pixelSize
    canvas.height = pixelArt.length * pixelSize

    pixelArt.forEach((row, rowIndex) => {
      row.forEach((pixel, colIndex) => {
        ctx.fillStyle = pixel.color
        ctx.fillRect(colIndex * pixelSize, rowIndex * pixelSize, pixelSize, pixelSize)
      })
    })

    canvas.toBlob((blob) => {
      if (blob) {
        const url = URL.createObjectURL(blob)
        const a = document.createElement("a")
        a.href = url
        a.download = "pixel-art.jpg"
        a.click()
        URL.revokeObjectURL(url)
      }
    }, "image/jpeg")

    // カラーパレット情報もダウンロード
    const paletteData = usedColors.map((color) => `${color.name}: ${color.color} (${color.count}個)`).join("\n")

    const blob = new Blob([paletteData], { type: "text/plain" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = "color-palette.txt"
    a.click()
    URL.revokeObjectURL(url)
  }, [pixelArt, usedColors])

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-center mb-8 text-gray-800">ドット絵コンバーター</h1>

        <div className="grid grid-cols-12 gap-6">
          {/* 左側パネル */}
          <div className="col-span-3 space-y-6">
            {/* 画像アップロード部 */}
            <Card className="p-4">
              <div
                className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-blue-400 transition-colors"
                onClick={() => fileInputRef.current?.click()}
              >
                {uploadedImage ? (
                  <img
                    ref={imageRef}
                    src={uploadedImage || "/placeholder.svg"}
                    alt="Uploaded"
                    className="max-w-full max-h-48 mx-auto cursor-move"
                    style={{
                      transform: `translate(${imagePosition.x}px, ${imagePosition.y}px) scale(${imageScale})`,
                    }}
                    onMouseDown={handleImageDragStart}
                    onMouseMove={handleImageDrag}
                    onMouseUp={handleImageDragEnd}
                    onMouseLeave={handleImageDragEnd}
                    draggable={false}
                  />
                ) : (
                  <div className="text-gray-500">
                    <Upload className="mx-auto mb-2" size={48} />
                    <p>クリックして画像を選択</p>
                  </div>
                )}
              </div>

              <input ref={fileInputRef} type="file" accept="image/*" onChange={handleImageUpload} className="hidden" />
              {uploadedImage && (
                <div className="mt-4 space-y-2">
                  <label className="block text-sm font-medium">スケール調整</label>
                  <div className="flex items-center gap-2">
                    <input
                      type="range"
                      min="0.1"
                      max="3"
                      step="0.1"
                      value={imageScale}
                      onChange={(e) => setImageScale(Number(e.target.value))}
                      className="flex-1"
                    />
                    <Input
                      type="number"
                      min="0.1"
                      max="3"
                      step="0.1"
                      value={imageScale}
                      onChange={(e) => setImageScale(Number(e.target.value))}
                      className="w-16 text-xs"
                    />
                  </div>
                  <div className="flex gap-2">
                    <Button onClick={() => setImageScale(1)} variant="outline" size="sm" className="text-xs">
                      リセット
                    </Button>
                    <Button
                      onClick={() => setImageScale(Math.max(0.1, imageScale - 0.1))}
                      variant="outline"
                      size="sm"
                      className="text-xs"
                    >
                      縮小
                    </Button>
                    <Button
                      onClick={() => setImageScale(Math.min(3, imageScale + 0.1))}
                      variant="outline"
                      size="sm"
                      className="text-xs"
                    >
                      拡大
                    </Button>
                  </div>
                  <div className="text-xs text-gray-500 text-center">{Math.round(imageScale * 100)}%</div>
                </div>
              )}
            </Card>

            {/* サイズ設定 */}
            <Card className="p-4">
              <label className="block text-sm font-medium mb-2">さいず</label>
              <Input
                type="number"
                value={outputSize}
                onChange={(e) => setOutputSize(Number(e.target.value))}
                min="8"
                max="128"
                className="mb-4"
              />

              <Button
                onClick={createPixelArt}
                disabled={!uploadedImage || isProcessing}
                className="w-full bg-blue-400 hover:bg-blue-500"
              >
                {isProcessing ? "処理中..." : "さくせい"}
              </Button>
            </Card>

            {/* 使用カラーパレット部 */}
            <Card className="p-4">
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {usedColors.map((color, index) => (
                  <div key={index} className="flex items-center gap-2 text-xs">
                    <div className="w-6 h-6 rounded border border-gray-300" style={{ backgroundColor: color.color }} />
                    <span className="flex-1">{color.name}</span>
                    <span className="text-gray-500">{color.count}</span>
                  </div>
                ))}
              </div>
            </Card>
          </div>

          {/* メイン表示部 */}
          <div className="col-span-6">
            <Card className="p-4 h-full">
              <div className="flex justify-center">
                <div
                  className="grid gap-0 border-2 border-gray-400 inline-block"
                  style={{
                    gridTemplateColumns: `repeat(${pixelArt[0]?.length || outputSize}, 1fr)`,
                    maxWidth: "600px",
                    maxHeight: "600px",
                  }}
                >
                  {pixelArt.map((row, rowIndex) =>
                    row.map((pixel, colIndex) => (
                      <div
                        key={`${rowIndex}-${colIndex}`}
                        className="w-4 h-4 border border-gray-200 cursor-pointer hover:opacity-80"
                        style={{ backgroundColor: pixel.color }}
                        onClick={() => handlePixelClick(rowIndex, colIndex)}
                      />
                    )),
                  )}

                  {/* 初期状態のグリッド表示 */}
                  {pixelArt.length === 0 &&
                    Array(outputSize)
                      .fill(null)
                      .map((_, rowIndex) =>
                        Array(outputSize)
                          .fill(null)
                          .map((_, colIndex) => (
                            <div
                              key={`empty-${rowIndex}-${colIndex}`}
                              className="w-4 h-4 border border-gray-200 bg-white"
                            />
                          )),
                      )}
                </div>
              </div>
            </Card>
          </div>

          {/* 右側パネル */}
          <div className="col-span-3 space-y-6">
            {/* カラーパレット部 */}
            <Card className="p-4">
              <div className="grid grid-cols-6 gap-1 max-h-96 overflow-y-auto">
                {Object.entries(COLOR_PALETTE).map(([name, color]) => (
                  <div
                    key={name}
                    className={`w-8 h-8 rounded cursor-pointer border-2 hover:scale-110 transition-transform ${
                      selectedColor === color ? "border-black" : "border-gray-300"
                    }`}
                    style={{ backgroundColor: color }}
                    onClick={() => setSelectedColor(color)}
                    title={name}
                  />
                ))}
              </div>

              {selectedColor && (
                <div className="mt-4 text-xs text-center">
                  選択中:{" "}
                  {Object.keys(COLOR_PALETTE).find(
                    (key) => COLOR_PALETTE[key as keyof typeof COLOR_PALETTE] === selectedColor,
                  )}
                </div>
              )}
            </Card>

            {/* ダウンロードボタン */}
            <Button
              onClick={downloadResults}
              disabled={pixelArt.length === 0}
              className="w-full bg-blue-400 hover:bg-blue-500"
            >
              <Download className="mr-2" size={16} />
              だうんろーど
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
