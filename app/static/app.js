(() => {
  const form = document.getElementById("card-form");
  const text = document.getElementById("text");
  const textCount = document.getElementById("text-count");
  const status = document.getElementById("status");
  const previewEmpty = document.getElementById("preview-empty");
  const previewImage = document.getElementById("preview-image");
  const downloadBtn = document.getElementById("download-btn");
  const generateBtn = document.getElementById("generate-btn");

  let objectUrl = null;

  const setStatus = (message, isError = false) => {
    status.textContent = message;
    status.classList.toggle("is-error", isError);
  };

  const updateCount = () => {
    textCount.textContent = String(text.value.length);
  };

  const revokePreview = () => {
    if (objectUrl) {
      URL.revokeObjectURL(objectUrl);
      objectUrl = null;
    }
  };

  const showPreview = (blob) => {
    revokePreview();
    objectUrl = URL.createObjectURL(blob);
    previewImage.hidden = false;
    previewEmpty.hidden = true;
    previewImage.classList.remove("is-ready");
    previewImage.src = objectUrl;
    requestAnimationFrame(() => {
      previewImage.classList.add("is-ready");
    });
    downloadBtn.disabled = false;
  };

  const generate = async () => {
    const body = text.value.trim();
    if (!body) {
      setStatus("本文を入力してください。", true);
      text.focus();
      return;
    }

    generateBtn.disabled = true;
    setStatus("カードを描いています…");

    try {
      const data = new FormData(form);
      const response = await fetch("/api/card", {
        method: "POST",
        body: data,
      });

      if (!response.ok) {
        let detail = "生成に失敗しました。";
        try {
          const payload = await response.json();
          if (payload?.detail) detail = payload.detail;
        } catch (_) {
          /* ignore */
        }
        throw new Error(detail);
      }

      const blob = await response.blob();
      showPreview(blob);
      setStatus("プレビューを更新しました。");
    } catch (error) {
      setStatus(error.message || "生成に失敗しました。", true);
    } finally {
      generateBtn.disabled = false;
    }
  };

  text.addEventListener("input", updateCount);
  updateCount();

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    generate();
  });

  downloadBtn.addEventListener("click", () => {
    if (!objectUrl) return;
    const link = document.createElement("a");
    link.href = objectUrl;
    link.download = "kamifuda.png";
    document.body.appendChild(link);
    link.click();
    link.remove();
  });

  // Seed a first card so the page never feels empty on first paint.
  if (!text.value) {
    text.value = "静かな朝は、言葉の余白がよく似合う。";
    document.getElementById("attribution").value = "紙札";
    updateCount();
    generate();
  }
})();
