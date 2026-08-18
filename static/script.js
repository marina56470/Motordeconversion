const valorInput = document.getElementById("valorInput");
const baseOrigen = document.getElementById("baseOrigen");
const bitsSelect = document.getElementById("bitsSelect");
const btnConvertir = document.getElementById("btnConvertir");
const errorBox = document.getElementById("errorBox");
const wordBadge = document.getElementById("wordBadge");

const bitcellsBinario = document.getElementById("bitcellsBinario");
const outOctal = document.getElementById("outOctal");
const outDecimal = document.getElementById("outDecimal");
const outHex = document.getElementById("outHex");

const aluBin1 = document.getElementById("aluBin1");
const aluBin2 = document.getElementById("aluBin2");
const aluOp = document.getElementById("aluOp");
const btnAlu = document.getElementById("btnAlu");
const aluErrorBox = document.getElementById("aluErrorBox");
const bitcellsAlu = document.getElementById("bitcellsAlu");
const aluOpLabel = document.getElementById("aluOpLabel");

function renderBitcells(container, cadenaBinaria, bitsPorDigito = 4) {
  container.innerHTML = "";
  const total = cadenaBinaria.length;

  [...cadenaBinaria].forEach((bit, i) => {
    const posicionDesdeIzquierda = i;
    const esInicioDeGrupo = posicionDesdeIzquierda > 0 && (total - posicionDesdeIzquierda) % bitsPorDigito === 0;

    const wrap = document.createElement("div");
    wrap.className = "bitcell" + (esInicioDeGrupo ? " group-start" : "");

    const box = document.createElement("div");
    box.className = "bit" + (bit === "1" ? " on" : "");
    box.textContent = bit;

    const idx = document.createElement("div");
    idx.className = "idx";
    idx.textContent = total - 1 - i;

    wrap.appendChild(box);
    wrap.appendChild(idx);
    container.appendChild(wrap);
  });
}

function showError(box, mensaje) {
  box.textContent = mensaje;
  box.classList.remove("hidden");
}

function hideError(box) {
  box.classList.add("hidden");
  box.textContent = "";
}

bitsSelect.addEventListener("change", () => {
  const label = bitsSelect.options[bitsSelect.selectedIndex].text;
  wordBadge.textContent = "registro · " + label.split("·")[0].trim() + " bits";
});

btnConvertir.addEventListener("click", async () => {
  hideError(errorBox);

  const valor = valorInput.value.trim();
  const base = parseInt(baseOrigen.value, 10);
  const bits = parseInt(bitsSelect.value, 10);

  if (!valor) {
    showError(errorBox, "Ingresa un valor para convertir.");
    return;
  }

  try {
    const resp = await fetch("/convertir", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ valor, base_origen: base, bits }),
    });
    const data = await resp.json();

    if (!data.ok) {
      showError(errorBox, data.error || "No se pudo procesar el valor.");
      bitcellsBinario.innerHTML = '<span class="placeholder">— sin datos —</span>';
      outOctal.textContent = "—";
      outDecimal.textContent = "—";
      outHex.textContent = "—";
      return;
    }

    renderBitcells(bitcellsBinario, data.binario, 4);
    outOctal.textContent = data.octal;
    outDecimal.textContent = data.decimal;
    outHex.textContent = data.hexadecimal;
  } catch (err) {
    showError(errorBox, "Error de conexión con el servidor.");
  }
});

btnAlu.addEventListener("click", async () => {
  hideError(aluErrorBox);

  const bin1 = aluBin1.value.trim();
  const bin2 = aluBin2.value.trim();
  const operacion = aluOp.value;

  if (!bin1 || !bin2) {
    showError(aluErrorBox, "Ingresa ambos operandos binarios.");
    return;
  }

  try {
    const resp = await fetch("/alu", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ bin1, bin2, operacion }),
    });
    const data = await resp.json();

    if (!data.ok) {
      showError(aluErrorBox, data.error || "No se pudo ejecutar la operación.");
      bitcellsAlu.innerHTML = '<span class="placeholder">— sin datos —</span>';
      aluOpLabel.textContent = "—";
      return;
    }

    renderBitcells(bitcellsAlu, data.resultado, 4);
    aluOpLabel.textContent = operacion;
  } catch (err) {
    showError(aluErrorBox, "Error de conexión con el servidor.");
  }
});

valorInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") btnConvertir.click();
});
