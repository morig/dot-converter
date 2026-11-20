# ドット絵コンバーター 環境構築ガイド（WSL + uv 版）

このドキュメントでは、**Windows 11 の中の WSL（Ubuntu）** にアプリの実行環境を作り、
**Windows のブラウザ** からアプリを開くまでの手順を、コマンドを 1 つも省略せずに説明します。

各ステップでは次の 3 点を必ず示します。

- **目的**: なぜその操作をするのか
- **意味**: コマンドが何をしているのか
- **図**: いまどのマシン（環境）で作業しているか、何がどこに入ったか

> 英語のツール名や用語が多く出てきます。分からない言葉は、末尾の [用語集](#用語集) を参照してください。

---

## 目次

- [全体像](#全体像)
- [図の読み方](#図の読み方)
- [Step 0. WSL と Ubuntu を用意する（Windows）](#step-0-wsl-と-ubuntu-を用意するwindows)
- [Step 1. Ubuntu のターミナルを開く](#step-1-ubuntu-のターミナルを開く)
- [Step 2. 基本ツール（git, curl, libatomic1）を入れる](#step-2-基本ツールgit-curl-libatomic1を入れる)
- [Step 3. アプリのソースコードを取得する](#step-3-アプリのソースコードを取得する)
- [Step 4. Node.js を入れる（nvm）](#step-4-nodejs-を入れるnvm)
- [Step 5. uv を入れる](#step-5-uv-を入れる)
- [Step 6. uv で Python 3.12 を入れる](#step-6-uv-で-python-312-を入れる)
- [Step 7. 仮想環境（.venv）を作る](#step-7-仮想環境venvを作る)
- [Step 8. 仮想環境に入る（activate）](#step-8-仮想環境に入るactivate)
- [Step 9. Python ライブラリを入れる](#step-9-python-ライブラリを入れる)
- [Step 10. Node.js のパッケージを入れる](#step-10-nodejs-のパッケージを入れる)
- [Step 11. アプリ（開発サーバー）を起動する](#step-11-アプリ開発サーバーを起動する)
- [Step 12. Windows のブラウザでアプリを開く](#step-12-windows-のブラウザでアプリを開く)
- [Step 13. アプリを止める](#step-13-アプリを止める)
- [2 回目以降の起動手順](#2-回目以降の起動手順)
- [うまくいかないとき](#うまくいかないとき)
- [用語集](#用語集)

---

## 全体像

このアプリは 2 つのプログラムが協力して動いています。

- **画面とサーバー**: Next.js（**Node.js** で動く）
- **画像をドット絵に変換する処理**: Python スクリプト（`scripts/pixel_art_converter.py`）

そのため、**Node.js と Python の両方** を用意する必要があります。
完成すると、あなたの PC の中は次のような「入れ子」の構造になります。

```text
┌─ 🪟 Windows 11（あなたの PC）
│    ・ブラウザ（Edge / Chrome）       ← 最後にここでアプリを開く
│    ・Windows Terminal / PowerShell
│
│   ┌─ 🐧 WSL2 ─ Ubuntu（Windows の中で動く Linux）
│   │    ・git, curl          /usr/bin/
│   │    ・libatomic1         /usr/lib/
│   │    ・nvm                ~/.nvm/
│   │    ・Node.js, npm       ~/.nvm/versions/node/
│   │    ・uv                 ~/.local/bin/
│   │    ・Python 3.12        ~/.local/share/uv/python/
│   │
│   │   ┌┄ 📁 ~/dot-converter（アプリのソースコード）
│   │   ┊    ・node_modules/（Next.js, React などの部品）
│   │   ┊
│   │   ┊   ┌┄ 📦 .venv（このアプリ専用の Python 環境）
│   │   ┊   ┊    ・numpy, Pillow, scikit-learn, scikit-image
│   │   ┊   └┄
│   │   └┄
│   └─
└─
```

作業する場所の流れは次のとおりです。**ほとんどの作業は Ubuntu の中** で行います。

```text
Step 0        Windows（PowerShell）  … WSL と Ubuntu を入れる
Step 1〜7     Ubuntu                 … ツールとソースコードを用意する
Step 8〜11    Ubuntu の .venv の中    … ライブラリを入れて起動する
Step 12       Windows（ブラウザ）     … アプリを開く
```

---

## 図の読み方

```text
┌─ 実線の箱    = マシン（OS が動いている環境）。Windows と Ubuntu
┌┄ 点線の箱    = フォルダによる仕切り。マシンではない
📍 今ここ      = いまコマンドを打っている場所
★             = このステップで新しく入ったもの
・            = 前のステップまでに入っていたもの
```

---

## Step 0. WSL と Ubuntu を用意する（Windows）

> すでに Ubuntu を使える場合は、確認コマンド `wsl -l -v` だけ実行してください。
> `Ubuntu` の `VERSION` が `2` になっていれば、Step 1 へ進んでかまいません。

**目的**
Windows の中で Linux（Ubuntu）を動かせるようにします。
Web アプリの開発ツールは Linux 向けに作られているものが多く、Linux の上で動かすとトラブルが少なくなります。

**作業場所**

```text
┌─ 🪟 Windows 11                                  📍 今ここ（PowerShell）
│    ・ブラウザ
│    ・Windows Terminal / PowerShell
│
│   ┌─ 🐧 WSL2 ─ Ubuntu                           ★ このステップで入る
│   └─
└─
```

**操作**

1. スタートメニューで「PowerShell」を検索し、右クリック →「**管理者として実行**」で開きます。
2. 次のコマンドを実行します。

```powershell
wsl --install
```

3. 完了したら **PC を再起動** します。
4. 再起動後に Ubuntu の画面が自動で開くので、Ubuntu 用のユーザー名とパスワードを決めて入力します。

```text
Enter new UNIX username: you          ← 好きなユーザー名（半角英小文字）
New password:                         ← 入力しても画面には何も表示されません（正常です）
Retype new password:
```

5. PowerShell（管理者でなくてよい）で、正しく入ったか確認します。

```powershell
wsl -l -v
```

**意味**

- `wsl --install` … WSL 本体と、標準の Linux である Ubuntu をまとめてインストールします。
- `wsl -l -v` … インストール済みの Linux の一覧（`-l`）を、詳細つき（`-v`）で表示します。

**こうなれば成功**

```text
  NAME      STATE           VERSION
* Ubuntu    Running         2
```

> ここで決めた Ubuntu のパスワードは、Step 2 の `sudo` で使います。忘れないようにしてください。

---

## Step 1. Ubuntu のターミナルを開く

**目的**
Ubuntu にコマンドを打ち込むための画面（ターミナル）を開きます。
**Step 1〜11 は、すべてこの Ubuntu のターミナルで操作します。**

**作業場所**

```text
┌─ 🪟 Windows 11
│    ・ブラウザ
│    ・Windows Terminal / PowerShell
│
│   ┌─ 🐧 WSL2 ─ Ubuntu                           📍 今ここ
│   │    （まだ何も入れていない）
│   └─
└─
```

**操作**

スタートメニューで「**Ubuntu**」を検索して開きます。
（Windows Terminal を使う場合は、タブの「∨」から「Ubuntu」を選びます）

次の表示（プロンプト）が出ていれば、Ubuntu の中にいます。

```text
you@mypc:~$
```

- `you` … Step 0 で決めたユーザー名
- `mypc` … PC の名前
- `~` … いまいるフォルダ（`~` はホームフォルダの意味）
- `$` … 「ここにコマンドを入力できます」という合図

続けて、次のコマンドを実行します。

```bash
cd ~
pwd
```

**意味**

- `cd ~` … ホームフォルダ（あなた専用の作業場所）に移動します。
- `pwd` … いまいるフォルダの場所を表示します。

**こうなれば成功**

```text
/home/you
```

`C:\Users\...` ではなく `/home/...` と表示されることから、Windows ではなく Ubuntu の中にいると分かります。

---

## Step 2. 基本ツール（git, curl, libatomic1）を入れる

**目的**
この後のステップで使う道具と部品を用意します。

- **git** … ソースコードを GitHub からダウンロードする（Step 3）
- **curl** … インターネットからインストール用のファイルを取ってくる（Step 4, 5）
- **libatomic1** … Node.js が動くために必要な部品（共有ライブラリ）。WSL の Ubuntu には最初から入っておらず、これがないと Step 4 で入れる Node.js が起動しません

git と curl は最初から入っていることが多いですが、念のため最新の状態にします。

**作業場所**

```text
┌─ 🪟 Windows 11
│    ・ブラウザ
│
│   ┌─ 🐧 WSL2 ─ Ubuntu                           📍 今ここ
│   │    ★ git, curl          /usr/bin/
│   │    ★ libatomic1         /usr/lib/
│   └─
└─
```

**コマンド**

```bash
sudo apt update
sudo apt install -y git curl libatomic1
```

**意味**

- `sudo` … 次に続くコマンドを **管理者の権限** で実行します。パスワードを聞かれたら、Step 0 で決めた Ubuntu のパスワードを入力します（入力しても画面には何も表示されません）。
- `apt update` … Ubuntu のソフトウェアの「カタログ」を最新にします。インストールはまだしません。
- `apt install -y git curl libatomic1` … git、curl、libatomic1 をインストールします。`-y` は「インストールしますか？」という確認に自動で「はい」と答えるオプションです。

**こうなれば成功**

```bash
git --version
curl --version
```

それぞれ `git version 2.x.x`、`curl 8.x.x ...` のようにバージョンが表示されれば OK です。

---

## Step 3. アプリのソースコードを取得する

**目的**
GitHub にあるアプリのソースコードを、Ubuntu のホームフォルダにコピー（クローン）します。

**作業場所**

```text
┌─ 🪟 Windows 11
│    ・ブラウザ
│
│   ┌─ 🐧 WSL2 ─ Ubuntu                           📍 今ここ
│   │    ・git, curl, libatomic1
│   │
│   │   ┌┄ 📁 ~/dot-converter                     ★ このステップでできる
│   │   ┊    （アプリのソースコード）
│   │   └┄
│   └─
└─
```

**コマンド**

```bash
cd ~
git clone https://github.com/morig/dot-converter.git
cd dot-converter
ls
```

**意味**

- `cd ~` … ホームフォルダに移動します。
- `git clone <URL>` … GitHub のリポジトリを丸ごとダウンロードし、`dot-converter` という名前のフォルダを作ります。
- `cd dot-converter` … 作られたフォルダの中に移動します。
- `ls` … フォルダの中身を一覧表示します。

**こうなれば成功**

`app`、`scripts`、`package.json`、`requirements.txt` などが表示されれば OK です。
プロンプトも `you@mypc:~/dot-converter$` に変わります。

> **なぜ `C:` ドライブ（`/mnt/c/...`）ではなく Ubuntu のホームに置くのか**
> Ubuntu からは Windows の `C:` ドライブを `/mnt/c` として開けますが、そこに置くと
> ファイルの読み書きが遅くなり、ファイルの変更を検知して画面を自動更新する機能もうまく動きません。
> ソースコードは必ず Ubuntu 側（`/home/you/...`）に置きます。
>
> なお、Windows のエクスプローラーのアドレス欄に `\\wsl.localhost\Ubuntu\home\you\dot-converter`
> と入力すると、Windows からもこのフォルダを見られます。

---

## Step 4. Node.js を入れる（nvm）

**目的**
アプリの画面とサーバー部分（Next.js）は **Node.js** で動きます。
このアプリは **Node.js 20.9 以上** が必要です。Ubuntu の `apt` で入る Node.js は古い（Ubuntu 24.04 では v18）ため、
Node.js のバージョンを管理するツール **nvm** を使って新しい Node.js を入れます。

**作業場所**

```text
┌─ 🪟 Windows 11
│    ・ブラウザ
│
│   ┌─ 🐧 WSL2 ─ Ubuntu                           📍 今ここ
│   │    ・git, curl, libatomic1
│   │    ★ nvm                ~/.nvm/
│   │    ★ Node.js, npm       ~/.nvm/versions/node/
│   │
│   │   ┌┄ 📁 ~/dot-converter
│   │   └┄
│   └─
└─
```

**コマンド**

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.8/install.sh | bash
source ~/.bashrc
nvm install --lts
node -v
npm -v
which node npm
```

**意味**

- `curl -o- <URL> | bash` … nvm のインストール用スクリプトをダウンロードし（`curl`）、その場で実行します（`| bash`）。nvm は `~/.nvm` に入り、Ubuntu を開くたびに nvm が使えるよう `~/.bashrc` に設定が追記されます。
- `source ~/.bashrc` … 追記された設定を、いま開いているターミナルにすぐ反映させます（ターミナルを開き直しても同じ効果です）。
- `nvm install --lts` … Node.js の LTS（長期サポート版）をダウンロードしてインストールします。npm も一緒に入ります。
- `node -v` / `npm -v` … インストールされたバージョンを表示して確認します。
- `which node npm` … `node` と `npm` と打ったときに、どこのプログラムが使われるかを表示します。

**こうなれば成功**

```text
v26.13.0
11.20.0
/home/you/.nvm/versions/node/v26.13.0/bin/node
/home/you/.nvm/versions/node/v26.13.0/bin/npm
```

- バージョンの数字は時期によって変わります。`node -v` が **v20.9.0 以上** であれば問題ありません。
- `which` の結果は、**2 行とも `/home/you/.nvm/` で始まっている** ことを確認してください。

> **Windows に Node.js が入っている人は要注意**
> WSL は、Windows 側のコマンドの場所（PATH）も引き継ぎます。
> そのため、nvm の Node.js が使えない状態だと、`npm` と打ったときに **Windows の npm**（`/mnt/c/Program Files/nodejs/npm`）が動いてしまいます。
> Windows の npm で Step 10 を実行すると、Linux では動かない部品が入ってしまいます。
> `which` の結果が `/mnt/c/...` になっていたら、`source ~/.bashrc` を実行するか、ターミナルを開き直してから再確認してください。
>
> なお、nvm のインストール中に `You currently have modules installed globally with npm` という警告が出ることがあります。
> これは Windows 側の npm を見つけたという案内なので、無視してかまいません。

> **`node: error while loading shared libraries: libatomic.so.1` と表示されたら**
> Step 2 の libatomic1 が入っていません。`sudo apt install -y libatomic1` を実行してから、もう一度 `node -v` を実行してください。

---

## Step 5. uv を入れる

**目的**
Python まわりの作業（Python 本体のインストール、仮想環境の作成、ライブラリのインストール）は、すべて **uv** という 1 つのツールで行います。
従来の `pip` や `venv` を個別に使うよりも高速で、手順もシンプルになります。

**作業場所**

```text
┌─ 🪟 Windows 11
│    ・ブラウザ
│
│   ┌─ 🐧 WSL2 ─ Ubuntu                           📍 今ここ
│   │    ・git, curl, libatomic1
│   │    ・nvm, Node.js, npm
│   │    ★ uv                 ~/.local/bin/
│   │
│   │   ┌┄ 📁 ~/dot-converter
│   │   └┄
│   └─
└─
```

**コマンド**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
uv --version
```

**意味**

- `curl -LsSf <URL> | sh` … uv のインストール用スクリプトをダウンロードして実行します。uv は `~/.local/bin/uv` に入ります。
  - `-L` リダイレクト先までたどる / `-s` 進捗を表示しない / `-S` エラーだけは表示する / `-f` 失敗したらエラーにする
- `source $HOME/.local/bin/env` … `~/.local/bin` を **PATH**（コマンドを探しに行く場所のリスト）に追加し、`uv` というコマンドを使えるようにします。
- `uv --version` … インストールされたバージョンを表示して確認します。

**こうなれば成功**

```text
uv 0.13.6 (x86_64-unknown-linux-gnu)
```

のようにバージョンが表示されれば OK です（数字は時期によって変わります）。

---

## Step 6. uv で Python 3.12 を入れる

**目的**
このアプリで使う **Python 3.12** を、uv で入れます。

Ubuntu にも最初から Python（`/usr/bin/python3`）が入っていますが、これは **Ubuntu 自身が使うためのもの** です。
これにライブラリを追加したり入れ替えたりすると、Ubuntu の動作がおかしくなることがあります。
そこで、アプリ用の Python は uv で別に用意し、OS の Python には触らないようにします。

**作業場所**

```text
┌─ 🪟 Windows 11
│    ・ブラウザ
│
│   ┌─ 🐧 WSL2 ─ Ubuntu                           📍 今ここ
│   │    ・git, curl, libatomic1
│   │    ・nvm, Node.js, npm
│   │    ・uv
│   │    ★ Python 3.12        ~/.local/share/uv/python/
│   │      （Ubuntu 自身の /usr/bin/python3 とは別物）
│   │
│   │   ┌┄ 📁 ~/dot-converter
│   │   └┄
│   └─
└─
```

**コマンド**

```bash
uv python install 3.12
uv python find 3.12
```

**意味**

- `uv python install 3.12` … Python 3.12 をダウンロードし、uv の管理場所（`~/.local/share/uv/python/`）にインストールします。
- `uv python find 3.12` … uv が使う Python 3.12 の場所を表示して、正しく入ったかを確認します。

**こうなれば成功**

`uv python install 3.12` の結果が次のようになり、

```text
Installed Python 3.12.16 in 3.83s
 + cpython-3.12.16-linux-x86_64-gnu (python3.12)
```

`uv python find 3.12` で、`~/.local/share/uv/python/` の下のパスが表示されれば OK です。

```text
/home/you/.local/share/uv/python/cpython-3.12-linux-x86_64-gnu/bin/python3.12
```

`/usr/bin/python3.12`（Ubuntu 自身の Python）が表示された場合は、`uv python install 3.12` が成功しているか確認してください。

---

## Step 7. 仮想環境（.venv）を作る

**目的**
このアプリ専用の Python 環境（**仮想環境**）を、プロジェクトのフォルダの中に作ります。

仮想環境を作ると、このアプリのために入れるライブラリが `.venv` フォルダの中だけに入り、
ほかのアプリや Ubuntu 全体に影響しません。
アプリごとに必要なライブラリやバージョンが違っても、ぶつからずに済みます。

**作業場所**

```text
┌─ 🪟 Windows 11
│    ・ブラウザ
│
│   ┌─ 🐧 WSL2 ─ Ubuntu                           📍 今ここ
│   │    ・git, curl, libatomic1
│   │    ・nvm, Node.js, npm
│   │    ・uv
│   │    ・Python 3.12
│   │
│   │   ┌┄ 📁 ~/dot-converter
│   │   ┊
│   │   ┊   ┌┄ 📦 .venv                           ★ このステップでできる
│   │   ┊   ┊    （まだ空っぽ。Python 3.12 だけが使える状態）
│   │   ┊   └┄
│   │   └┄
│   └─
└─
```

**コマンド**

```bash
cd ~/dot-converter
uv venv --python 3.12
ls -a
```

**意味**

- `cd ~/dot-converter` … プロジェクトのフォルダに移動します（仮想環境はこの中に作るため）。
- `uv venv --python 3.12` … Step 6 の Python 3.12 を使って、`.venv` という名前の仮想環境を作ります。
- `ls -a` … `.` で始まる隠しフォルダも含めて一覧表示します（`.venv` は隠しフォルダなので、`-a` がないと見えません）。

**こうなれば成功**

`uv venv` の実行結果が次のようになり、`ls -a` の一覧に `.venv` が表示されれば OK です。

```text
Using CPython 3.12.16
Creating virtual environment at: .venv
Activate with: source .venv/bin/activate
```

> **名前と場所は変えないでください**
> アプリは、プロジェクト直下の `.venv` にある Python を自動で探して使います。
> 名前を変えたり別の場所に作ったりすると、画像の変換に失敗します。

---

## Step 8. 仮想環境に入る（activate）

**目的**
このターミナルで `python` と打ったときに、**`.venv` の Python が使われる** ように切り替えます。
これを「仮想環境に入る（activate する）」と言います。

**作業場所**

```text
┌─ 🪟 Windows 11
│    ・ブラウザ
│
│   ┌─ 🐧 WSL2 ─ Ubuntu
│   │    ・git, curl, libatomic1
│   │    ・nvm, Node.js, npm
│   │    ・uv
│   │    ・Python 3.12
│   │
│   │   ┌┄ 📁 ~/dot-converter
│   │   ┊
│   │   ┊   ┌┄ 📦 .venv                           📍 今ここ
│   │   ┊   ┊    （まだ空っぽ）
│   │   ┊   └┄
│   │   └┄
│   └─
└─
```

**コマンド**

```bash
source .venv/bin/activate
which python
```

**意味**

- `source .venv/bin/activate` … 仮想環境を有効にします。PATH の先頭に `.venv/bin` が追加され、`python` という名前で `.venv` の中の Python が呼ばれるようになります。
- `which python` … `python` と打ったときに、実際にどのファイルが実行されるかを表示します。

**こうなれば成功**

プロンプトの先頭に `(dot-converter)` が付きます。これが「仮想環境の中にいる」という目印です。

```text
(dot-converter) you@mypc:~/dot-converter$
```

`which python` の結果が `.venv` の中を指していれば OK です。

```text
/home/you/dot-converter/.venv/bin/python
```

> **仮想環境は「別のマシン」ではありません**
> 図では箱の中に入ったように描いていますが、実際には同じ Ubuntu の中で、
> 「`python` と打ったら `.venv` の Python を使う」という **切り替え** をしているだけです。
> そのため図では、マシン（実線の箱）ではなくフォルダの仕切り（点線の箱）で表しています。
> 抜けるときは `deactivate` と打ちます（Step 13）。

---

## Step 9. Python ライブラリを入れる

**目的**
画像をドット絵に変換する Python スクリプトが使うライブラリを、**`.venv` の中に** インストールします。
必要なライブラリの一覧は `requirements.txt` に書かれています。

**作業場所**

```text
┌─ 🪟 Windows 11
│    ・ブラウザ
│
│   ┌─ 🐧 WSL2 ─ Ubuntu
│   │    ・git, curl, libatomic1
│   │    ・nvm, Node.js, npm
│   │    ・uv
│   │    ・Python 3.12
│   │
│   │   ┌┄ 📁 ~/dot-converter
│   │   ┊
│   │   ┊   ┌┄ 📦 .venv                           📍 今ここ
│   │   ┊   ┊    ★ numpy, Pillow, scikit-learn, scikit-image
│   │   ┊   ┊      （＋それらが必要とする scipy など）
│   │   ┊   ┊      場所: .venv/lib/python3.12/site-packages/
│   │   ┊   └┄
│   │   └┄
│   └─
└─
```

**コマンド**

```bash
uv pip install -r requirements.txt
python -c "import numpy, PIL, sklearn, skimage; print('OK')"
```

**意味**

- `uv pip install -r requirements.txt` … `requirements.txt` に書かれたライブラリを、いま有効になっている仮想環境（`.venv`）にまとめてインストールします。`-r` は「ファイルに書かれた一覧から入れる」という意味です。
- `python -c "..."` … `"..."` の中の Python コードをその場で実行します。ここでは 4 つのライブラリを読み込み（`import`）、エラーが出なければ `OK` と表示します。

| requirements.txt の名前 | 役割 |
| --- | --- |
| `numpy` | 画像を数値の表として計算する |
| `Pillow`（コード中では `PIL`） | 画像ファイルを読み書き・縮小する |
| `scikit-learn`（コード中では `sklearn`） | 色をグループ分けして色数を減らす |
| `scikit-image`（コード中では `skimage`） | 人の見た目に近い色空間（CIELAB）で色を比べる |

**こうなれば成功**

`uv pip install` の結果の最後に、次のような一覧が表示されます。
`requirements.txt` の 4 つに加えて、それらが必要とするライブラリ（`scipy` など）も自動で入ります。

```text
Installed 14 packages in 45ms
 + cloudpickle==3.1.2
 + imageio==2.38.1
 ...
 + numpy==2.5.4
 + pillow==13.0.0
 + scikit-image==0.26.0
 + scikit-learn==1.9.1
 + scipy==1.18.1
 ...
```

続く `python -c ...` で次のように表示されれば OK です。

```text
OK
```

---

## Step 10. Node.js のパッケージを入れる

**目的**
アプリの画面とサーバー部分が使う部品（Next.js、React など）をインストールします。
必要な部品の一覧は `package.json` と `package-lock.json` に書かれています。

**作業場所**

```text
┌─ 🪟 Windows 11
│    ・ブラウザ
│
│   ┌─ 🐧 WSL2 ─ Ubuntu
│   │    ・git, curl, libatomic1
│   │    ・nvm, Node.js, npm
│   │    ・uv
│   │    ・Python 3.12
│   │
│   │   ┌┄ 📁 ~/dot-converter
│   │   ┊    ★ node_modules/（Next.js, React など）  ← .venv の外に入る
│   │   ┊
│   │   ┊   ┌┄ 📦 .venv                           📍 今ここ（activate したまま）
│   │   ┊   ┊    ・numpy, Pillow, scikit-learn, scikit-image
│   │   ┊   └┄
│   │   └┄
│   └─
└─
```

**コマンド**

```bash
npm ci
npm ls next
```

**意味**

- `npm ci` … `package-lock.json` に記録されたバージョンのとおりに、パッケージを `node_modules` フォルダにインストールします。誰がいつ実行しても同じ構成になるのが特徴です（`npm install` はバージョンが更新される場合があります）。
- `npm ls next` … インストールされた Next.js のバージョンを表示して確認します。

**こうなれば成功**

`npm ci` の結果が次のようになり、

```text
added 105 packages, and audited 106 packages in 25s
found 0 vulnerabilities
```

`npm ls next` で、パスが `/home/you/...` から始まり、`next@16.4.3` が表示されれば OK です。

```text
my-v0-project@0.1.0 /home/you/dot-converter
└── next@16.4.3
```

- パスが `\\wsl.localhost\...` で始まっている場合は、Windows の npm で実行されています。Step 4 の注意を確認して、`rm -rf node_modules` で消してから `npm ci` をやり直してください。
- `New major version of npm available!` という案内が出ることがありますが、無視してかまいません。

> **仮想環境は Node.js には関係しません**
> プロンプトには `(dot-converter)` が付いたままですが、仮想環境が切り替えるのは **Python だけ** です。
> Node.js のパッケージは `.venv` ではなく、プロジェクト直下の `node_modules` に入ります。

---

## Step 11. アプリ（開発サーバー）を起動する

**目的**
Next.js の **開発サーバー** を起動して、ブラウザからアプリにアクセスできる状態にします。

**作業場所**

```text
┌─ 🪟 Windows 11
│    ・ブラウザ
│
│   ┌─ 🐧 WSL2 ─ Ubuntu
│   │    ・git, curl, libatomic1
│   │    ・nvm, Node.js, npm
│   │    ・uv
│   │    ・Python 3.12
│   │    ⚙ Next.js 開発サーバー（ポート 3000 で待ち受け中）  ★ 起動
│   │
│   │   ┌┄ 📁 ~/dot-converter
│   │   ┊    ・node_modules/
│   │   ┊
│   │   ┊   ┌┄ 📦 .venv                           📍 今ここ
│   │   ┊   ┊    ・numpy, Pillow, scikit-learn, scikit-image
│   │   ┊   └┄
│   │   └┄
│   └─
└─
```

**コマンド**

```bash
npm run dev
```

**意味**

- `npm run dev` … `package.json` の `scripts` に書かれた `dev`（中身は `next dev`）を実行し、開発サーバーを起動します。
  開発サーバーはソースコードの変更を検知して、ブラウザの表示を自動で更新してくれます。

**こうなれば成功**

```text
▲ Next.js 16.4.3 (Turbopack)
- Local:         http://localhost:3000
- Network:       http://10.255.255.254:3000
✓ Ready in 278ms
```

- `Network:` の IP アドレスは環境によって変わります。このガイドでは使いません。
- 初回だけ `Attention: Next.js now collects completely anonymous telemetry ...`（匿名の利用統計を集めるという案内）が表示されます。気にしなくてかまいません。

> **このターミナルは閉じないでください**
> 開発サーバーは、このターミナルが開いている間だけ動きます。
> 別の作業をしたいときは、新しく Ubuntu のターミナルを開いてください。

---

## Step 12. Windows のブラウザでアプリを開く

**目的**
Windows のブラウザから、Ubuntu の中で動いているアプリを開きます。

**作業場所**

```text
┌─ 🪟 Windows 11                                  📍 今ここ（ブラウザ）
│    ・ブラウザ  → http://localhost:3000 を開く
│
│   ┌─ 🐧 WSL2 ─ Ubuntu
│   │    ⚙ Next.js 開発サーバー（ポート 3000）  ← ブラウザからの通信はここに届く
│   │
│   │   ┌┄ 📁 ~/dot-converter
│   │   ┊   ┌┄ 📦 .venv
│   │   ┊   ┊    ・Python 3.12 + ライブラリ  ← 画像の変換のときに呼ばれる
│   │   ┊   └┄
│   │   └┄
│   └─
└─
```

**操作**

1. Windows で Edge や Chrome を開きます。
2. アドレス欄に次の URL を入力して開きます。

```text
http://localhost:3000
```

3. 「ドット絵コンバーター」の画面が表示されたら、「クリックして画像を選択」から画像を選び、「**さくせい**」ボタンを押します。
4. ドット絵が表示されれば完成です。

**意味**

- `localhost` は「この PC 自身」を表す名前、`3000` は Step 11 の開発サーバーが待ち受けている番号（ポート）です。
- 本来、`localhost` は Windows 自身を指しますが、WSL2 には **Windows の localhost への通信を自動で Ubuntu に転送する仕組み** があります。そのため、Windows のブラウザから Ubuntu の中のアプリを開けます。

**「さくせい」を押したときの裏側の流れ**

```text
① ブラウザ（Windows）
     │  画像を送る（/api/create-pixel-art）
     ▼
② WSL2 の転送（自動）
     │
     ▼
③ Next.js 開発サーバー（Ubuntu・Node.js で動作）
     │  .venv/bin/python で scripts/pixel_art_converter.py を起動
     ▼
④ Python スクリプト（.venv の Python とライブラリで動作）
     │  画像を縮小し、パレットの色に置き換える
     ▼
⑤ 結果がブラウザに返り、ドット絵が表示される
```

アプリは `.venv` の Python を自動で使うので、開発サーバーを起動する前に activate していなくても変換は動きます。

---

## Step 13. アプリを止める

**目的**
作業が終わったら、開発サーバーを止めて仮想環境から抜けます。

**作業場所**

```text
┌─ 🪟 Windows 11
│
│   ┌─ 🐧 WSL2 ─ Ubuntu                           📍 今ここ（deactivate 後）
│   │    ⚙ Next.js 開発サーバー  → 停止
│   │
│   │   ┌┄ 📁 ~/dot-converter
│   │   ┊   ┌┄ 📦 .venv                           ← deactivate でここから出る
│   │   ┊   └┄
│   │   └┄
│   └─
└─
```

**操作**

1. Step 11 のターミナルで **`Ctrl` + `C`** を押して、開発サーバーを止めます。
2. 続けて次のコマンドを実行します。

```bash
deactivate
```

**意味**

- `Ctrl` + `C` … 実行中のプログラムを中断します。
- `deactivate` … 仮想環境から抜けます。プロンプトの `(dot-converter)` が消えます。

> インストールしたもの（Node.js、uv、Python、`.venv`、`node_modules`）は消えません。次回は下の「2 回目以降の起動手順」だけで動きます。

---

## 2 回目以降の起動手順

環境はすでにできているので、次の操作だけで起動できます。

1. Ubuntu のターミナルを開く（Step 1）
2. 次のコマンドを実行する

```bash
cd ~/dot-converter
source .venv/bin/activate
npm run dev
```

3. Windows のブラウザで `http://localhost:3000` を開く（Step 12）

---

## うまくいかないとき

- **`nvm: command not found` と表示される**
  `source ~/.bashrc` を実行するか、ターミナルを開き直してください。
- **`node: error while loading shared libraries: libatomic.so.1` と表示される**
  `sudo apt install -y libatomic1` を実行してください（Step 2）。
- **`which node npm` の結果や `npm ls` のパスが `/mnt/c/...` や `\\wsl.localhost\...` になる**
  Windows の Node.js が使われています。Step 4 の注意を確認してください。
- **`uv: command not found` と表示される**
  `source $HOME/.local/bin/env` を実行するか、ターミナルを開き直してください。
- **ブラウザで `http://localhost:3000` が開けない**
  Step 11 のターミナルで開発サーバーが動いているか確認してください。
  3000 番がほかのプログラムに使われていると、`http://localhost:3001` のように別の番号で起動することがあります。ターミナルの `Local:` に表示された URL を開いてください。
- **「さくせい」を押すとエラーになる**
  `~/dot-converter/.venv` があるか、Step 9 の確認コマンドで `OK` と表示されるかを確認してください。

---

## 用語集

### Windows・WSL まわり

- **Windows 11** … あなたの PC で動いている OS。このガイドでは、いちばん外側のマシンです。
- **PowerShell** … Windows でコマンドを打つための画面とその言語。Step 0 で使います。
- **Windows Terminal** … PowerShell や Ubuntu などのターミナルを、タブで切り替えて使えるアプリ。Windows 11 に標準で入っています。
- **WSL / WSL2**（Windows Subsystem for Linux）… Windows の中で Linux を動かす仕組み。WSL2 は、その中に本物の Linux を動かす新しい方式です。
- **Ubuntu** … Linux の種類（ディストリビューション）の一つ。WSL で標準的に使われます。
- **`/mnt/c`** … Ubuntu から見た Windows の `C:` ドライブ。ここにソースコードを置くと動作が遅くなります。
- **`\\wsl.localhost\Ubuntu\...`** … Windows のエクスプローラーから Ubuntu のフォルダを見るときの場所。

### Linux・ターミナルまわり

- **ターミナル** … 文字でコマンドを入力して PC を操作する画面。
- **シェル / bash** … ターミナルに打ったコマンドを解釈して実行するプログラム。Ubuntu の標準は bash です。
- **プロンプト** … `you@mypc:~$` のように、コマンド入力を待っている印。どこにいるかのヒントになります。
- **ホームフォルダ（`~`）** … ユーザーごとの作業場所。`/home/<ユーザー名>` のことです。
- **`sudo`** … コマンドを管理者権限で実行するための前置き。
- **`apt`** … Ubuntu のソフトウェアをインストール・更新する道具（Ubuntu のアプリストアのようなもの）。
- **共有ライブラリ** … 複数のプログラムが共通で使う部品。`libatomic1` は Node.js が使う共有ライブラリの一つです。
- **`source`** … ファイルに書かれた設定やコマンドを、いまのターミナルに読み込んで反映させるコマンド。
- **`~/.bashrc`** … ターミナルを開くたびに自動で読み込まれる設定ファイル。
- **PATH** … コマンド名を打ったときに、実行するプログラムを探しに行くフォルダのリスト。WSL では Windows 側の PATH も後ろに追加されます。
- **curl** … URL を指定してインターネットからデータを取ってくるコマンド。
- **`|`（パイプ）** … 左のコマンドの出力を、右のコマンドに渡す記号。`curl ... | bash` は「ダウンロードした内容をそのまま実行する」という意味です。

### Git まわり

- **Git** … ソースコードの変更履歴を管理する道具。
- **GitHub** … Git のリポジトリをインターネット上で共有するサービス。
- **リポジトリ** … ソースコードとその変更履歴をまとめたもの。
- **クローン（`git clone`）** … リポジトリを丸ごと自分の PC にコピーすること。

### Python まわり

- **Python** … プログラミング言語。このアプリでは画像の変換処理に使います。
- **ライブラリ / パッケージ** … ほかの人が作った便利なプログラムの部品。`numpy` や `Pillow` など。
- **uv** … Python 本体のインストール、仮想環境の作成、ライブラリのインストールを 1 つでこなす高速なツール。
- **pip** … Python の標準的なライブラリのインストール道具。このガイドでは代わりに `uv pip` を使います。
- **仮想環境（venv）** … アプリ専用の Python の作業場所。ライブラリをアプリごとに分けて入れられます。このガイドでは `.venv` フォルダです。
- **activate / deactivate** … 仮想環境に入る（`python` を `.venv` のものに切り替える）／抜けること。
- **`requirements.txt`** … そのアプリに必要な Python ライブラリの一覧を書いたファイル。
- **site-packages** … Python のライブラリが実際にインストールされるフォルダ。

### Node.js まわり

- **Node.js** … ブラウザの外で JavaScript を動かすための実行環境。Next.js はこの上で動きます。
- **npm** … Node.js のパッケージをインストール・管理する道具。Node.js と一緒に入ります。
- **nvm**（Node Version Manager）… Node.js のバージョンを切り替えたり、新しいバージョンを入れたりする道具。
- **LTS**（Long Term Support）… 長期間サポートされる安定版のこと。
- **`package.json`** … Node.js のアプリに必要なパッケージや、`npm run dev` などのコマンドを書いたファイル。
- **`package-lock.json`** … 実際にインストールするパッケージの正確なバージョンを記録したファイル。
- **`node_modules`** … npm でインストールしたパッケージが入るフォルダ。
- **Next.js** … React をベースにした Web アプリのフレームワーク。このアプリの画面とサーバーを担当します。
- **開発サーバー** … 開発中にアプリを動かすためのサーバー。ファイルを変更すると自動で反映されます。

### ネットワークまわり

- **localhost** … 「この PC 自身」を表す名前。
- **ポート** … 1 台の PC の中で、通信の窓口を区別するための番号。このアプリは 3000 番を使います。
- **localhost の転送（WSL2）** … Windows の `localhost` 宛ての通信を、WSL2 が自動で Ubuntu に届ける仕組み。Windows のブラウザから Ubuntu のアプリを開けるのはこのおかげです。
