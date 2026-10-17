const API_URL = "/api/v1/minutes";
let selectedFile = null;

// APIキーの読み込み
document.addEventListener('DOMContentLoaded', () => {
  const savedKey = localStorage.getItem('apiKey');
  if (savedKey) {
    document.getElementById('apiKey').value = savedKey;
  }
});

// APIキーの保存
document.getElementById('saveKey').addEventListener('click', () => {
  const apiKey = document.getElementById('apiKey').value.trim();
  if (apiKey) {
    localStorage.setItem('apiKey', apiKey);
    alert('APIキーを保存しました');
  }
});

// ファイル選択ボタン
document.getElementById('selectFileBtn').addEventListener('click', () => {
  document.getElementById('fileInput').click();
});

// ファイル選択時
document.getElementById('fileInput').addEventListener('change', (e) => {
  if (e.target.files.length > 0) {
    handleFile(e.target.files[0]);
  }
});

// ドラッグ＆ドロップ
const dropZone = document.getElementById('dropZone');

dropZone.addEventListener('dragover', (e) => {
  e.preventDefault();
  dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
  dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
  e.preventDefault();
  dropZone.classList.remove('dragover');
  if (e.dataTransfer.files.length > 0) {
    handleFile(e.dataTransfer.files[0]);
  }
});

// ファイル処理
function handleFile(file) {
  if (!file.type.startsWith('audio/')) {
    alert('音声ファイルを選択してください（MP3, WAVなど）');
    return;
  }
  selectedFile = file;
  document.getElementById('fileName').textContent = `選択中: ${file.name}`;
  document.getElementById('generateBtn').disabled = false;
}

// 議事録生成
document.getElementById('generateBtn').addEventListener('click', async () => {
  const apiKey = localStorage.getItem('apiKey');
  if (!apiKey) {
    alert('APIキーを入力して保存してください');
    return;
  }
  if (!selectedFile) {
    alert('音声ファイルを選択してください');
    return;
  }

  const formData = new FormData();
  formData.append('file', selectedFile);

  document.getElementById('generateBtn').disabled = true;
  document.getElementById('loading').style.display = 'block';
  document.getElementById('resultArea').style.display = 'none';

  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'X-API-Key': apiKey
      },
      body: formData
    });

    if (!response.ok) {
      throw new Error(`エラー: ${response.status}`);
    }

    const data = await response.json();
    
    // 結果を表示
    document.getElementById('minutesContent').textContent = data.minutes;
    document.getElementById('transcriptContent').textContent = data.transcript;
    document.getElementById('resultArea').style.display = 'block';

  } catch (error) {
    alert(error.message);
  } finally {
    document.getElementById('generateBtn').disabled = false;
    document.getElementById('loading').style.display = 'none';
  }
});

// タブ切り替え
function switchTab(tabName) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  event.target.classList.add('active');

  if (tabName === 'minutes') {
    document.getElementById('minutesContent').style.display = 'block';
    document.getElementById('transcriptContent').style.display = 'none';
  } else {
    document.getElementById('minutesContent').style.display = 'none';
    document.getElementById('transcriptContent').style.display = 'block';
  }
}

// ダウンロード
document.getElementById('downloadBtn').addEventListener('click', () => {
  const minutes = document.getElementById('minutesContent').textContent;
  const blob = new Blob([minutes], { type: 'text/markdown' });
  const url = URL.createObjectURL(blob);
  
  const a = document.createElement('a');
  a.href = url;
  a.download = `議事録_${new Date().toISOString().slice(0,10)}.md`;
  a.click();
  
  URL.revokeObjectURL(url);
});